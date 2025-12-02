from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    first_name = StringField('First Name', validators=[
        Length(max=50, message='First name cannot exceed 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        Length(max=50, message='Last name cannot exceed 50 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])

class RecipeForm(FlaskForm):
    """Recipe creation and editing form"""
    title = StringField('Recipe Title', validators=[
        DataRequired(message='Recipe title is required'),
        Length(max=200, message='Title cannot exceed 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters')
    ], render_kw={'rows': 3})
    
    instructions = TextAreaField('Instructions', validators=[
        DataRequired(message='Instructions are required')
    ], render_kw={'rows': 8})
    
    prep_time = IntegerField('Prep Time (minutes)', validators=[
        Optional(),
        NumberRange(min=0, max=1440, message='Prep time must be between 0 and 1440 minutes')
    ])
    
    cook_time = IntegerField('Cook Time (minutes)', validators=[
        Optional(),
        NumberRange(min=0, max=1440, message='Cook time must be between 0 and 1440 minutes')
    ])
    
    servings = IntegerField('Servings', validators=[
        DataRequired(message='Number of servings is required'),
        NumberRange(min=1, max=50, message='Servings must be between 1 and 50')
    ], default=4)
    
    difficulty = SelectField('Difficulty', choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ], validators=[DataRequired(message='Please select difficulty level')])
    
    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message='Please select a category')
    ])
    
    image = FileField('Recipe Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                   message='Only image files are allowed (jpg, jpeg, png, gif, webp)')
    ])

class CommentForm(FlaskForm):
    """Recipe comment form"""
    content = TextAreaField('Your Comment', validators=[
        DataRequired(message='Comment cannot be empty'),
        Length(max=1000, message='Comment cannot exceed 1000 characters')
    ], render_kw={'rows': 4, 'placeholder': 'Share your thoughts about this recipe...'})

class IngredientForm(FlaskForm):
    """Individual ingredient form (used dynamically)"""
    name = StringField('Ingredient', validators=[
        DataRequired(message='Ingredient name is required'),
        Length(max=100, message='Ingredient name cannot exceed 100 characters')
    ])
    
    amount = StringField('Amount', validators=[
        Length(max=10, message='Amount cannot exceed 10 characters')
    ])
    
    unit = SelectField('Unit', choices=[
        ('', 'Select unit'),
        ('cup', 'Cup'),
        ('cups', 'Cups'),
        ('tbsp', 'Tablespoon'),
        ('tsp', 'Teaspoon'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
        ('g', 'Gram'),
        ('kg', 'Kilogram'),
        ('ml', 'Milliliter'),
        ('l', 'Liter'),
        ('piece', 'Piece'),
        ('pieces', 'Pieces'),
        ('clove', 'Clove'),
        ('cloves', 'Cloves'),
        ('slice', 'Slice'),
        ('slices', 'Slices'),
        ('to taste', 'To taste'),
        ('pinch', 'Pinch'),
        ('bunch', 'Bunch')
    ])
    
    notes = StringField('Notes', validators=[
        Length(max=200, message='Notes cannot exceed 200 characters')
    ], render_kw={'placeholder': 'e.g., finely chopped, optional'})

class SearchForm(FlaskForm):
    """Recipe search form"""
    query = StringField('Search Recipes', validators=[
        Length(max=100, message='Search query cannot exceed 100 characters')
    ], render_kw={'placeholder': 'Search for recipes, ingredients, or keywords...'})
    
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    
    difficulty = SelectField('Difficulty', choices=[
        ('', 'Any Difficulty'),
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ], validators=[Optional()])
    
    max_time = IntegerField('Max Total Time (minutes)', validators=[
        Optional(),
        NumberRange(min=1, max=1440, message='Time must be between 1 and 1440 minutes')
    ])

class RatingForm(FlaskForm):
    """Recipe rating form"""
    score = SelectField('Rating', choices=[
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    ], coerce=int, validators=[
        DataRequired(message='Please select a rating')
    ])