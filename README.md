# v01dworks Photography

A personal photography portfolio and blog application built with Flask. This project features a responsive public gallery for showcasing photos and a robust admin panel for content management.

## Features

*   **Public Gallery:** A clean, responsive masonry layout to display photography.
*   **Photo Details:** Automatically extracts and displays EXIF metadata (Camera, Lens, Aperture, Shutter Speed, ISO) from uploaded images.
*   **Admin Panel:** Secure interface built with Flask-Admin to manage photos, posts, and user profiles.
*   **Dark Mode:** Fully supported system-aware Dark/Light mode for both the public website and the admin interface.
*   **Image Processing:** Handles image uploads, resizing, and orientation correction (including HEIC support).
*   **Social Links:** Integrated social media links (Threads, Bluesky, Instagram, etc.) with FontAwesome icons.
*   **Dockerized:** Ready for deployment with Docker and Docker Compose.

## Tech Stack

*   **Backend:** Python 3.11, Flask
*   **Database:** SQLite (via Flask-SQLAlchemy)
*   **Frontend:** Jinja2 Templates, Bootstrap 3 (Public), Bootstrap 4 (Admin), CSS Variables for theming
*   **Image Processing:** Pillow, Pillow-HEIF
*   **Server:** Gunicorn (Production), Werkzeug (Dev)

## Getting Started

### Prerequisites

*   Docker & Docker Compose (Recommended)
*   OR Python 3.11+

### Option 1: Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd v01dworksphotography
    ```

2.  **Configure Environment:**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` if you want to change the secret key or database URL.

3.  **Build and Run:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the Application:**
    *   Public Site: `http://localhost:8000`
    *   Admin Panel: `http://localhost:8000/admin`

### Option 2: Local Development

1.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Setup:**
    Initialize the database and apply migrations:
    ```bash
    flask db upgrade
    ```

4.  **Create Admin User:**
    Run the helper script to create your initial admin account:
    ```bash
    python create_admin.py
    ```

5.  **Run the Server:**
    ```bash
    python run.py
    ```
    The app will be available at `http://localhost:5000`.

## Project Structure

*   `app/`: Application source code.
    *   `models.py`: Database models (User, Post, Photo).
    *   `routes.py`: View functions and routing logic.
    *   `templates/`: Jinja2 HTML templates.
    *   `static/`: CSS, JS, and uploaded images.
*   `migrations/`: Database migration files.
*   `config.py`: Application configuration settings.
*   `Dockerfile` & `docker-compose.yml`: Docker configuration.

## License

MIT License

## Author

**Dustin Olsen** (v01d / v01dworks)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/v01dworks)
