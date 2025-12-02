from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB

# Initialize database
from database import db
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Import models
from models import User, Recipe, Category, Comment, Rating, Ingredient

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes
from routes import main, auth, recipes

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(recipes.bp)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default categories if none exist
        if not Category.query.first():
            default_categories = [
                'Italian', 'Mexican', 'Asian', 'Mediterranean', 'American',
                'Indian', 'French', 'Thai', 'Greek', 'Spanish',
                'Appetizers', 'Main Course', 'Desserts', 'Beverages',
                'Vegetarian', 'Vegan', 'Gluten-Free', 'Quick & Easy'
            ]
            for cat_name in default_categories:
                category = Category(name=cat_name)
                db.session.add(category)
            db.session.commit()
            print("Default categories created!")
        
    app.run(debug=True)