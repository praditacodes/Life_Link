# Blood Link

A web-based Blood Bank Management System built with Django. This platform connects blood donors, patients, and administrators, making it easy to manage blood requests, donations, and user information.

## Features
- Donor and patient registration/login
- Admin dashboard for managing users and requests
- Donor dashboard to track donation requests
- Patient dashboard to request and track blood
- Search for donors by blood group and location
- Responsive UI with Bootstrap

## Getting Started

### Prerequisites
- Python 3.7+
- pip
- Git

### Setup Instructions (Windows)
1. **Clone the repository:**
   ```sh
   git clone https://github.com/praditacodes/Life-Link.git
   cd blood_link
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
5. **Create a superuser (admin):**
   ```sh
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```
7. **Access the app:**
   - Open your browser and go to `http://127.0.0.1:8000/`

## Project Structure
- `blood/` - Main app for blood management
- `donor/` - Donor-related models and views
- `patient/` - Patient-related models and views
- `bloodbankmanagement/` - Project settings and configuration
- `templates/` - HTML templates
- `static/` - CSS, JS, and images

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.

