from PIL import Image, ExifTags, ImageOps
from geopy.geocoders import Nominatim
from datetime import datetime
import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

def fix_image_orientation(image_path):
    try:
        image = Image.open(image_path)
        # exif_transpose will rotate the image according to the EXIF orientation tag
        # and remove the orientation tag.
        transposed_image = ImageOps.exif_transpose(image)
        
        # If the image was actually rotated/transposed
        if transposed_image is not image:
            # Save the image back to the same path
            # We try to preserve the original format
            # Note: This might strip other EXIF data depending on how it's saved,
            # but since we extract metadata to DB separately, visual correctness is priority here.
            transposed_image.save(image_path, quality=95)
            print(f"Fixed orientation for {image_path}")
            return True
    except Exception as e:
        print(f"Error fixing orientation for {image_path}: {e}")
    return False

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]
    
    decimal = float(degrees) + (float(minutes) / 60.0) + (float(seconds) / 3600.0)
    
    if ref in ['S', 'W']:
        decimal = -decimal
        
    return decimal

def get_lat_lon(exif_data):
    if 'GPSInfo' in exif_data:
        gps_info = exif_data['GPSInfo']
        
        lat_dms = gps_info.get(2)
        lat_ref = gps_info.get(1)
        lon_dms = gps_info.get(4)
        lon_ref = gps_info.get(3)
        
        if lat_dms and lat_ref and lon_dms and lon_ref:
            return get_decimal_from_dms(lat_dms, lat_ref), get_decimal_from_dms(lon_dms, lon_ref)
    return None

def process_image_metadata(image_path):
    try:
        img = Image.open(image_path)
        exif_data = {}
        if img._getexif():
            for tag, value in img._getexif().items():
                if tag in ExifTags.TAGS:
                    exif_data[ExifTags.TAGS[tag]] = value
    except Exception as e:
        print(f"Error reading EXIF: {e}")
        return {}

    metadata = {}
    
    # Date Taken
    if 'DateTimeOriginal' in exif_data:
        try:
            metadata['date_taken'] = datetime.strptime(exif_data['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        except ValueError:
            pass
            
    # Camera Make/Model
    metadata['camera_make'] = exif_data.get('Make')
    metadata['camera_model'] = exif_data.get('Model')
    
    # Lens
    metadata['lens'] = exif_data.get('LensModel')
    
    # Settings
    if exif_data.get('FocalLength'):
        metadata['focal_length'] = f"{exif_data.get('FocalLength')}mm"
    
    if exif_data.get('FNumber'):
        metadata['aperture'] = f"f/{exif_data.get('FNumber')}"
        
    if exif_data.get('ExposureTime'):
        metadata['shutter_speed'] = f"{exif_data.get('ExposureTime')}s"
        
    metadata['iso'] = exif_data.get('ISOSpeedRatings')

    # Location
    lat_lon = get_lat_lon(exif_data)
    if lat_lon:
        geolocator = Nominatim(user_agent="photography_blog_v01d")
        try:
            location = geolocator.reverse(lat_lon, language='en')
            # Try to get a shorter address (City, Country)
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village')
            country = address.get('country')
            if city and country:
                metadata['location'] = f"{city}, {country}"
            else:
                metadata['location'] = location.address
        except Exception as e:
            print(f"Geocoding error: {e}")
            metadata['location'] = f"{lat_lon[0]:.4f}, {lat_lon[1]:.4f}"
            
    return metadata
