import os
import requests
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from flask_admin.model.form import InlineFormAdmin
from flask_admin.menu import MenuLink
from app import app, db, admin
from app.models import User, Post, Photo, Profile
from app.utils import process_image_metadata, fix_image_orientation

# Add link to public site in menu
admin.add_link(MenuLink(name='View Site', url='/'))

@app.context_processor
def inject_admin_data():
    if request.endpoint == 'admin.index':
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return dict(dashboard_posts=posts)
    return dict()

# Custom Admin View to ensure security
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class PhotoInlineModelView(InlineFormAdmin):
    form_overrides = dict(image_filename=ImageUploadField)
    form_args = dict(image_filename=dict(
        label='Image',
        base_path=app.config['UPLOAD_FOLDER'], 
        url_relative_path='uploads/'
    ))

class PostView(SecureModelView):
    # Override form_extra_fields to use ImageUploadField
    # We map the 'image_filename' column to an ImageUploadField
    # Note: The model field 'image_filename' will store the filename string.
    edit_template = 'admin/model/edit_post.html'
    create_template = 'admin/model/edit_post.html'

    form_overrides = dict(image_filename=ImageUploadField)
    form_args = dict(image_filename=dict(
        label='Cover Image',
        base_path=app.config['UPLOAD_FOLDER'], 
        url_relative_path='uploads/'
    ))
    
    inline_models = (PhotoInlineModelView(Photo),)

    def after_model_change(self, form, model, is_created):
        # Process metadata for photos
        print(f"DEBUG: after_model_change called. is_created={is_created}")
        metadata_updated = False
        for photo in model.photos:
            print(f"DEBUG: Processing photo: {photo.image_filename}")
            if photo.image_filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.image_filename)
                print(f"DEBUG: Checking file path: {file_path}")
                
                # Check if file exists
                if os.path.exists(file_path):
                    print(f"DEBUG: File exists. Processing metadata...")
                    try:
                        # First, try to extract metadata from the file
                        # We do this BEFORE fixing orientation because saving the image might strip EXIF
                        metadata = process_image_metadata(file_path)
                        print(f"DEBUG: Metadata extracted: {metadata}")
                        
                        # Now fix the orientation (rotate image if needed)
                        fix_image_orientation(file_path)
                        
                        if metadata:
                            # Only update fields if they are NOT already set (e.g. by the user/JS)
                            # or if we want to enforce server-side extraction.
                            # Given the user report, we should prioritize existing data if present.
                            
                            if not photo.date_taken and metadata.get('date_taken'):
                                photo.date_taken = metadata.get('date_taken')
                                metadata_updated = True
                                
                            if not photo.location and metadata.get('location'):
                                photo.location = metadata.get('location')
                                metadata_updated = True
                                
                            if not photo.camera_make and metadata.get('camera_make'):
                                photo.camera_make = metadata.get('camera_make')
                                metadata_updated = True
                                
                            if not photo.camera_model and metadata.get('camera_model'):
                                photo.camera_model = metadata.get('camera_model')
                                metadata_updated = True
                                
                            if not photo.lens and metadata.get('lens'):
                                photo.lens = metadata.get('lens')
                                metadata_updated = True
                                
                            if not photo.focal_length and metadata.get('focal_length'):
                                photo.focal_length = metadata.get('focal_length')
                                metadata_updated = True
                                
                            if not photo.aperture and metadata.get('aperture'):
                                photo.aperture = metadata.get('aperture')
                                metadata_updated = True
                                
                            if not photo.shutter_speed and metadata.get('shutter_speed'):
                                photo.shutter_speed = metadata.get('shutter_speed')
                                metadata_updated = True
                                
                            if not photo.iso and metadata.get('iso'):
                                photo.iso = str(metadata.get('iso'))
                                metadata_updated = True
                                
                    except Exception as e:
                        print(f"DEBUG: Error processing metadata: {e}")
                else:
                    print(f"DEBUG: File does not exist at {file_path}")
        
        if metadata_updated:
            db.session.commit()

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
            
        try:
            # Check if we have a private key stored (in a real app, store this securely in DB or env)
            # For this demo, we'll check if a key file exists
            key_path = os.path.join(app.instance_path, 'analytics_key.pem')
            headers = {}
            
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    private_key_bytes = f.read()
                    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
                    
                    timestamp = int(time.time())
                    site_id = 'v01dworks-photography'
                    message = f"{site_id}:{timestamp}".encode()
                    signature = private_key.sign(message).hex()
                    
                    headers = {
                        "X-Timestamp": str(timestamp),
                        "X-Signature": signature
                    }

            # Use a timeout to prevent hanging if the API is down
            response = requests.get('https://analytics.v01dworks.com/stats?site_id=v01dworks-photography', headers=headers, timeout=5)
            
            if response.status_code == 200:
                stats = response.json()
                return self.render('admin/analytics.html', stats=stats)
            elif response.status_code == 401:
                 return self.render('admin/analytics.html', error="Authentication Failed. Please pair with the server.")
            else:
                return self.render('admin/analytics.html', error=f"Error fetching stats: {response.status_code}")
        except Exception as e:
            return self.render('admin/analytics.html', error=f"Error connecting to analytics API: {str(e)}")

    @expose('/pair')
    def pair(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
            
        # Generate new key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Save private key
        key_path = os.path.join(app.instance_path, 'analytics_key.pem')
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        # Register public key
        public_hex = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        
        try:
            requests.post('https://analytics.v01dworks.com/register-key', json={
                "site_id": "v01dworks-photography",
                "public_key_hex": public_hex
            })
            flash('Successfully paired with Analytics Server!')
        except Exception as e:
            flash(f'Failed to register key: {e}')
            
        return redirect(url_for('analytics.index'))

    @expose('/qr')
    def qr_code(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Redirect to the API's QR code page
        return redirect('https://analytics.v01dworks.com/pair/v01dworks-photography')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class ProfileView(SecureModelView):
    form_overrides = dict(image_filename=ImageUploadField)
    form_args = dict(image_filename=dict(
        label='Profile Image',
        base_path=app.config['UPLOAD_FOLDER'], 
        url_relative_path='uploads/'
    ))

admin.add_view(SecureModelView(User, db.session))
admin.add_view(PostView(Post, db.session))
admin.add_view(ProfileView(Profile, db.session))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))

@app.route('/')
@app.route('/index')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/about')
def about():
    profile = Profile.query.first()
    return render_template('about.html', title='About Me', profile=profile)
