Blur Image Quality Enhancer

A web-based application that enhances the quality of blurred images using deep learning (Real-ESRGAN). Users can upload blurry images, enhance them, and download the results. The project also includes user authentication, history tracking, and cloud storage.


Features

Upload and enhance blurred images.
Preview blurry and enhanced images.
Download enhanced images.
User registration and login.
View previously enhanced images (history).
Cloud storage for user images.


Download Latest Real-ESRGAN Model

This project uses Real-ESRGAN for image enhancement. You need to download the latest pretrained model before running the backend.

Go to the Real-ESRGAN releases page.
Download the latest RealESRGAN_x4plus.pth model (usually under "Assets").
Place the downloaded model inside the backend/real_esrgan/weights/ folder.
Make sure app.py points to the correct path: model_path = "real_esrgan/weights/RealESRGAN_x4plus.pth"
Now your Flask backend is ready to enhance images.


Installation

Backend

Clone the repository:
git clone <repo-url>
cd backend

Create a virtual environment:
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

Install dependencies:
pip install -r requirements.txt

Create a .env file in the backend/ folder and add the following environment variables:
FLASK_APP=app.py
SECRET_KEY=<your_secret_key>
DATABASE_URL=<your_database_url>
Make sure to replace <your_secret_key> and <your_database_url> with your actual values.

Run the Flask server:
flask run


Frontend

Navigate to the Flutter app folder:
cd flutter_app

Install dependencies:
flutter pub get

Run the web app:
flutter run -d chrome
