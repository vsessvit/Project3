from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from models import Recipe, Category, Rating
from database import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page with featured recipes and categories"""
    # Get featured recipes (highest rated)
    featured_recipes = Recipe.query.join(Rating).group_by(Recipe.id)\
        .order_by(desc(func.avg(Rating.score))).limit(6).all()
    
    # Get all categories for navigation
    categories = Category.query.all()
    
    # Get recent recipes
    recent_recipes = Recipe.query.order_by(desc(Recipe.created_at)).limit(6).all()
    
    return render_template('index.html', 
                         featured_recipes=featured_recipes,
                         recent_recipes=recent_recipes,
                         categories=categories)

@bp.route('/search')
def search():
    """Search recipes by various criteria"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty')
    max_time = request.args.get('max_time', type=int)
    
    # Build search query
    recipes = Recipe.query
    
    if query:
        recipes = recipes.filter(
            Recipe.title.contains(query) | 
            Recipe.description.contains(query) |
            Recipe.instructions.contains(query)
        )
    
    if category_id:
        recipes = recipes.filter(Recipe.category_id == category_id)
    
    if difficulty:
        recipes = recipes.filter(Recipe.difficulty == difficulty)
    
    if max_time:
        recipes = recipes.filter(
            (Recipe.prep_time + Recipe.cook_time) <= max_time
        )
    
    recipes = recipes.order_by(desc(Recipe.created_at)).all()
    
    categories = Category.query.all()
    
    return render_template('search.html', 
                         recipes=recipes,
                         categories=categories,
                         search_query=query,
                         selected_category=category_id,
                         selected_difficulty=difficulty,
                         selected_max_time=max_time)

@bp.route('/categories')
def categories():
    """Browse recipes by category"""
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@bp.route('/category/<int:category_id>')
def category_recipes(category_id):
    """Show all recipes in a specific category"""
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    
    recipes = Recipe.query.filter_by(category_id=category_id)\
        .order_by(desc(Recipe.created_at))\
        .paginate(page=page, per_page=12, error_out=False)
    
    return render_template('category_recipes.html', 
                         category=category,
                         recipes=recipes)

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/api/recipe/<int:recipe_id>/scale')
@login_required
def scale_recipe(recipe_id):
    """API endpoint to get scaled recipe ingredients"""
    recipe = Recipe.query.get_or_404(recipe_id)
    new_servings = request.args.get('servings', type=int)
    
    if not new_servings or new_servings <= 0:
        return jsonify({'error': 'Invalid serving size'}), 400
    
    scaled_ingredients = recipe.get_scaled_ingredients(new_servings)
    
    return jsonify({
        'original_servings': recipe.servings,
        'new_servings': new_servings,
        'ingredients': scaled_ingredients
    })

@bp.route('/shopping-list')
@login_required
def shopping_list():
    """Generate shopping list from selected recipes"""
    recipe_ids = request.args.getlist('recipes', type=int)
    servings = request.args.getlist('servings', type=int)
    
    if not recipe_ids:
        return render_template('shopping_list.html', ingredients={})
    
    # Combine ingredients from multiple recipes
    combined_ingredients = {}
    
    for i, recipe_id in enumerate(recipe_ids):
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            continue
            
        recipe_servings = servings[i] if i < len(servings) else recipe.servings
        scaled_ingredients = recipe.get_scaled_ingredients(recipe_servings)
        
        for ingredient in scaled_ingredients:
            name = ingredient['name'].lower()
            unit = ingredient['unit'] or ''
            amount = ingredient['amount'] or 0
            
            # Simple ingredient combination (could be enhanced)
            key = f"{name}_{unit}"
            if key in combined_ingredients:
                combined_ingredients[key]['amount'] += amount
            else:
                combined_ingredients[key] = {
                    'name': ingredient['name'],
                    'amount': amount,
                    'unit': unit,
                    'notes': ingredient['notes']
                }
    
    return render_template('shopping_list.html', 
                         ingredients=combined_ingredients.values())