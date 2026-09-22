# AAROHAN'26 Food Pass System 🚀

A robust, Django-based QR code generation and scanning system designed to streamline food distribution for large-scale college fests and events. Built originally for AAROHAN'26, this system completely eliminates paper coupons, replacing them with a secure, single-use digital QR ecosystem.

## ✨ Features

- **Automated QR Generation**: Instantly generates mathematically unique QR codes for every registered student.
- **Background Email Dispatch**: Seamlessly emails QR passes directly to students via SMTP, running in a background thread to prevent UI freezing.
- **Mobile-First Scanner UI**: A beautiful, Tailwind-styled web app for volunteers. Uses the device camera to scan QR codes instantly via `html5-qrcode`.
- **Live Stats Dashboard**: A real-time JSON endpoint to monitor Veg vs. Non-Veg consumption and track pending distributions.
- **Advanced Admin Panel**: Extended Django Admin interface featuring one-click CSV student imports and bulk email triggers.
- **Secure API**: Endpoints are protected by custom `X-Verify-Token` headers to prevent unauthorized scans.
- **Concurrency Safe**: Uses database-level row locking (`select_for_update`) to prevent race conditions during simultaneous scans.

## 🛠️ Tech Stack

- **Backend**: Python, Django, PostgreSQL
- **Frontend**: HTML5, Vanilla JS, Tailwind CSS
- **Scanning**: HTML5-QRCode library
- **Deployment**: Docker, Docker Compose, Gunicorn, Nginx

## 🚀 Quick Start (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/raazix/Food-Coupon-QR-Code-System.git
cd Food-Coupon-QR-Code-System
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_google_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
VERIFY_TOKEN=supersecrettoken123
```

### 4. Migrate and Run
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🐳 Docker Deployment

This project is fully containerized for production deployment.

```bash
# Build and run the containers in detached mode
docker-compose up --build -d

# Run migrations inside the web container
docker-compose exec web python manage.py migrate

# Create the admin user
docker-compose exec web python manage.py createsuperuser
```

*Note: For camera access on mobile devices during production, the web scanner must be served over HTTPS. You can easily achieve this using a reverse proxy like Ngrok or setting up Let's Encrypt with Nginx.*

## 🔒 Security Notes
- Never commit your `.env` file or expose your `VERIFY_TOKEN`.
- The `EMAIL_HOST_PASSWORD` must be a Google App Password, not a standard account password.

---
*Built for AAROHAN'26*
