from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(100), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    recipes = db.relationship('Recipe', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_average_recipe_rating(self):
        """Calculate average rating for user's recipes"""
        if not self.recipes:
            return 0
        total_ratings = sum(recipe.get_average_rating() for recipe in self.recipes)
        return total_ratings / len(self.recipes)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Recipe categories for organization"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipes = db.relationship('Recipe', backref='category', lazy=True)
    
    def recipe_count(self):
        """Return number of recipes in this category"""
        return len(self.recipes)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Recipe(db.Model):
    """Main recipe model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer, default=4)
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    image = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='recipe', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        """Calculate average rating for this recipe"""
        if not self.ratings:
            return 0
        return sum(rating.score for rating in self.ratings) / len(self.ratings)
    
    def get_total_time(self):
        """Get total cooking time"""
        return (self.prep_time or 0) + (self.cook_time or 0)
    
    def get_scaled_ingredients(self, new_servings):
        """Return ingredients scaled for new serving size"""
        if not self.servings or self.servings == 0:
            return self.ingredients
        
        scale_factor = new_servings / self.servings
        scaled_ingredients = []
        
        for ingredient in self.ingredients:
            scaled_amount = ingredient.amount * scale_factor if ingredient.amount else None
            scaled_ingredients.append({
                'name': ingredient.name,
                'amount': scaled_amount,
                'unit': ingredient.unit,
                'notes': ingredient.notes
            })
        
        return scaled_ingredients
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

class Ingredient(db.Model):
    """Recipe ingredients with measurements"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float)  # Numeric amount (e.g., 2.5)
    unit = db.Column(db.String(50))  # cups, tbsp, kg, etc.
    notes = db.Column(db.String(200))  # e.g., "finely chopped", "to taste"
    order = db.Column(db.Integer, default=0)  # For ordering ingredients in recipe
    
    # Foreign key
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    def formatted_amount(self):
        """Return nicely formatted amount string"""
        if not self.amount:
            return ""
        
        # Convert to fraction if appropriate
        if self.amount < 1:
            if self.amount == 0.5:
                return "1/2"
            elif self.amount == 0.25:
                return "1/4"
            elif self.amount == 0.75:
                return "3/4"
            elif self.amount == 0.33:
                return "1/3"
            elif self.amount == 0.67:
                return "2/3"
        
        # For whole numbers, show as int
        if self.amount == int(self.amount):
            return str(int(self.amount))
        
        return str(self.amount)
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'

class Comment(db.Model):
    """User comments on recipes"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment by {self.author.username} on {self.recipe.title}>'

class Rating(db.Model):
    """User ratings for recipes (1-5 stars)"""
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)  # 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    # Ensure one rating per user per recipe
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),)
    
    def __repr__(self):
        return f'<Rating {self.score}/5 by {self.author.username}>'