from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from basicsr.archs.rrdbnet_arch import RRDBNet
from flask_cors import CORS
from PIL import Image as PILImage
import os
import uuid
import torch
import numpy as np
from realesrgan import RealESRGANer
from config import Config

# Initialize Flask app, SQLAlchemy, JWT, and Bcrypt
app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENHANCED_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    enhanced_filename = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('images', lazy=True))

# Load RealESRGAN model
scale = 4
model_path = r'C:\Users\User\OneDrive\Desktop\Project\backend\Real-ESRGAN\experiments\pretrained_models\RealESRGAN_x4plus.pth'

model = None
if os.path.exists(model_path):
    try:
        print("Loading model...")
        model_net = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=23, num_grow_ch=32, scale=scale)
        model = RealESRGANer(
            scale=scale,
            model_path=model_path,
            model=model_net,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            device='cpu'
        )
        model.model.load_state_dict(torch.load(model_path), strict=False)
        model.model.eval()
        print("RealESRGAN model loaded successfully.")
    except Exception as e:
        print(f"Model loading failed: {e}")
else:
    print("Model file not found.")

# Enhance image
def enhance_image(image_path):
    if model is None:
        return None
    try:
        img = PILImage.open(image_path).convert('RGB')
        img_np = np.array(img)
        output, _ = model.enhance(img_np)

        enhanced_img = PILImage.fromarray(output).convert('RGB')
        unique_name = f"enhanced_{uuid.uuid4().hex}.png"
        enhanced_path = os.path.join(app.config['ENHANCED_FOLDER'], unique_name)
        enhanced_img.save(enhanced_path, format="PNG")
        return enhanced_path
    except Exception as e:
        print(f"Enhancement failed: {e}")
        return None

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify(message="User already exists"), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User registered successfully"), 201

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

@app.route('/')
def home():
    return "Flask app is running!"

# Upload + Enhance + Return Full URLs
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    user_id = int(get_jwt_identity())
    if 'image' not in request.files:
        return jsonify(message="No image part in the request"), 400

    uploaded = request.files['image']
    if uploaded.filename == '':
        return jsonify(message="No file selected"), 400

    unique_name = f"{uuid.uuid4().hex}_{uploaded.filename}"
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    try:
        uploaded.save(original_path)
    except Exception as e:
        return jsonify(message="Failed to save image"), 500

    enhanced_path = enhance_image(original_path)
    if not enhanced_path:
        return jsonify(message="Image enhancement failed"), 500

    enhanced_filename = os.path.basename(enhanced_path)
    new_image = Image(filename=unique_name, enhanced_filename=enhanced_filename, user_id=user_id)
    db.session.add(new_image)
    db.session.commit()

    # Build absolute URLs
    base_url = request.host_url.rstrip('/')
    return jsonify(
        message="Image enhanced",
        preview_url=f"{base_url}/preview/uploads/{unique_name}",
        enhanced_url=f"{base_url}/preview/enhanced/{enhanced_filename}",
        download_url=f"{base_url}/download/{enhanced_filename}"
    ), 200

# Download (returns as image, not attachment) — JWT removed
@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    try:
        return send_from_directory(app.config['ENHANCED_FOLDER'], filename, mimetype='image/png', as_attachment=False)
    except Exception as e:
        return jsonify(message="Failed to download image: " + str(e)), 500

# Preview (uploaded/enhanced) — JWT removed
@app.route('/preview/<folder>/<filename>', methods=['GET'])
def preview_image(folder, filename):
    if folder == 'uploads':
        directory = app.config['UPLOAD_FOLDER']
    elif folder == 'enhanced':
        directory = app.config['ENHANCED_FOLDER']
    else:
        return jsonify(message="Invalid folder"), 400

    try:
        return send_from_directory(directory, filename, mimetype='image/png', as_attachment=False)
    except Exception as e:
        return jsonify(message="Failed to preview image: " + str(e)), 500

# Create DB tables
with app.app_context():
    db.create_all()

# Run app
if __name__ == '__main__':
    app.run(debug=True)
