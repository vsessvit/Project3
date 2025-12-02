from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Recipe, Category, Ingredient, Comment, Rating
from database import db
from forms import RecipeForm, CommentForm
import os
from PIL import Image

bp = Blueprint('recipes', __name__, url_prefix='/recipes')

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_recipe_image(image_file):
    """Save and resize uploaded recipe image"""
    if not image_file or image_file.filename == '':
        return None
    
    if not allowed_file(image_file.filename):
        return None
    
    # Create secure filename
    filename = secure_filename(image_file.filename)
    filename = f"{current_user.id}_{filename}"
    
    # Save path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Open and resize image
        image = Image.open(image_file)
        # Resize to max 800x600 while maintaining aspect ratio
        image.thumbnail((800, 600), Image.Resampling.LANCZOS)
        image.save(file_path, optimize=True, quality=85)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

@bp.route('/')
def index():
    """List all recipes with pagination"""
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.order_by(Recipe.created_at.desc())\
        .paginate(page=page, per_page=12, error_out=False)
    
    categories = Category.query.all()
    return render_template('recipes/index.html', recipes=recipes, categories=categories)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new recipe"""
    form = RecipeForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Handle image upload
        image_filename = save_recipe_image(form.image.data) if form.image.data else None
        
        # Create recipe
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            instructions=form.instructions.data,
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            difficulty=form.difficulty.data,
            category_id=form.category_id.data,
            user_id=current_user.id,
            image=image_filename
        )
        
        db.session.add(recipe)
        db.session.flush()  # Get recipe ID
        
        # Process ingredients
        ingredients_data = request.form.getlist('ingredient_name')
        amounts_data = request.form.getlist('ingredient_amount')
        units_data = request.form.getlist('ingredient_unit')
        notes_data = request.form.getlist('ingredient_notes')
        
        for i, name in enumerate(ingredients_data):
            if name.strip():  # Only add non-empty ingredients
                ingredient = Ingredient(
                    name=name.strip(),
                    amount=float(amounts_data[i]) if amounts_data[i] and amounts_data[i].replace('.', '').isdigit() else None,
                    unit=units_data[i].strip() if i < len(units_data) else '',
                    notes=notes_data[i].strip() if i < len(notes_data) else '',
                    recipe_id=recipe.id,
                    order=i
                )
                db.session.add(ingredient)
        
        db.session.commit()
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('recipes.view', id=recipe.id))
    
    return render_template('recipes/create.html', form=form)

@bp.route('/<int:id>')
def view(id):
    """View a single recipe"""
    recipe = Recipe.query.get_or_404(id)
    comments = Comment.query.filter_by(recipe_id=id).order_by(Comment.created_at.desc()).all()
    
    # Check if current user has rated this recipe
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=id).first()
    
    comment_form = CommentForm()
    
    return render_template('recipes/view.html', 
                         recipe=recipe, 
                         comments=comments,
                         user_rating=user_rating,
                         comment_form=comment_form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a recipe (only by owner)"""
    recipe = Recipe.query.get_or_404(id)
    
    if recipe.user_id != current_user.id:
        flash('You can only edit your own recipes', 'error')
        return redirect(url_for('recipes.view', id=id))
    
    form = RecipeForm(obj=recipe)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_filename = save_recipe_image(form.image.data)
            if image_filename:
                recipe.image = image_filename
        
        # Update recipe
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.instructions = form.instructions.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.difficulty = form.difficulty.data
        recipe.category_id = form.category_id.data
        
        # Update ingredients (simplified - delete and recreate)
        Ingredient.query.filter_by(recipe_id=recipe.id).delete()
        
        ingredients_data = request.form.getlist('ingredient_name')
        amounts_data = request.form.getlist('ingredient_amount')
        units_data = request.form.getlist('ingredient_unit')
        notes_data = request.form.getlist('ingredient_notes')
        
        for i, name in enumerate(ingredients_data):
            if name.strip():
                ingredient = Ingredient(
                    name=name.strip(),
                    amount=float(amounts_data[i]) if amounts_data[i] and amounts_data[i].replace('.', '').isdigit() else None,
                    unit=units_data[i].strip() if i < len(units_data) else '',
                    notes=notes_data[i].strip() if i < len(notes_data) else '',
                    recipe_id=recipe.id,
                    order=i
                )
                db.session.add(ingredient)
        
        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipes.view', id=recipe.id))
    
    return render_template('recipes/edit.html', form=form, recipe=recipe)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a recipe (only by owner)"""
    recipe = Recipe.query.get_or_404(id)
    
    if recipe.user_id != current_user.id:
        flash('You can only delete your own recipes', 'error')
        return redirect(url_for('recipes.view', id=id))
    
    # Delete image file if exists
    if recipe.image:
        try:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image: {e}")
    
    db.session.delete(recipe)
    db.session.commit()
    
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('recipes.index'))

@bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Add a comment to a recipe"""
    recipe = Recipe.query.get_or_404(id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            recipe_id=id
        )
        db.session.add(comment)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'success': True,
                'comment': {
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        
        flash('Comment added successfully!', 'success')
    
    return redirect(url_for('recipes.view', id=id))

@bp.route('/<int:id>/rate', methods=['POST'])
@login_required
def rate(id):
    """Rate a recipe"""
    recipe = Recipe.query.get_or_404(id)
    score = request.form.get('rating', type=int)
    
    if not score or score < 1 or score > 5:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Invalid rating'}), 400
        flash('Invalid rating', 'error')
        return redirect(url_for('recipes.view', id=id))
    
    # Check if user already rated this recipe
    existing_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=id).first()
    
    if existing_rating:
        existing_rating.score = score
    else:
        rating = Rating(
            score=score,
            user_id=current_user.id,
            recipe_id=id
        )
        db.session.add(rating)
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'success': True,
            'new_average': recipe.get_average_rating(),
            'user_rating': score
        })
    
    flash('Rating submitted successfully!', 'success')
    return redirect(url_for('recipes.view', id=id))