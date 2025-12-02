// Recipe Exchange JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initRecipeScaling();
    initRatingSystem();
    initCommentSystem();
    initShoppingList();
    initImagePreview();
    initIngredientManager();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Recipe Scaling Functionality
function initRecipeScaling() {
    const scalingContainer = document.getElementById('recipe-scaling');
    if (!scalingContainer) return;
    
    const servingDisplay = document.getElementById('serving-count');
    const decreaseBtn = document.getElementById('decrease-servings');
    const increaseBtn = document.getElementById('increase-servings');
    const recipeId = scalingContainer.dataset.recipeId;
    
    if (decreaseBtn && increaseBtn && servingDisplay) {
        decreaseBtn.addEventListener('click', () => adjustServings(-1, recipeId, servingDisplay));
        increaseBtn.addEventListener('click', () => adjustServings(1, recipeId, servingDisplay));
    }
}

function adjustServings(change, recipeId, servingDisplay) {
    const currentServings = parseInt(servingDisplay.textContent);
    const newServings = Math.max(1, currentServings + change);
    
    if (newServings === currentServings) return;
    
    servingDisplay.textContent = newServings;
    
    // Show loading state
    const ingredientsList = document.getElementById('ingredients-list');
    if (ingredientsList) {
        ingredientsList.style.opacity = '0.6';
    }
    
    // Fetch scaled ingredients
    fetch(`/api/recipe/${recipeId}/scale?servings=${newServings}`)
        .then(response => response.json())
        .then(data => {
            if (data.ingredients) {
                updateIngredientsDisplay(data.ingredients);
            }
        })
        .catch(error => {
            console.error('Error scaling recipe:', error);
            showToast('Error scaling recipe. Please try again.', 'error');
        })
        .finally(() => {
            if (ingredientsList) {
                ingredientsList.style.opacity = '1';
            }
        });
}

function updateIngredientsDisplay(ingredients) {
    const ingredientsList = document.getElementById('ingredients-list');
    if (!ingredientsList) return;
    
    ingredientsList.innerHTML = ingredients.map(ingredient => {
        const amount = ingredient.amount ? formatAmount(ingredient.amount) : '';
        const unit = ingredient.unit || '';
        const notes = ingredient.notes ? ` (${ingredient.notes})` : '';
        
        return `
            <div class="ingredient-item">
                <span class="ingredient-amount">${amount} ${unit}</span>
                <span class="ingredient-name">${ingredient.name}${notes}</span>
            </div>
        `;
    }).join('');
    
    // Add animation
    ingredientsList.classList.add('fade-in');
}

function formatAmount(amount) {
    // Convert decimal to fraction when appropriate
    const fractions = {
        0.125: '1/8',
        0.25: '1/4',
        0.33: '1/3',
        0.5: '1/2',
        0.67: '2/3',
        0.75: '3/4'
    };
    
    // Check for close fraction matches
    for (const [decimal, fraction] of Object.entries(fractions)) {
        if (Math.abs(amount - decimal) < 0.01) {
            return fraction;
        }
    }
    
    // For mixed numbers
    const whole = Math.floor(amount);
    const remaining = amount - whole;
    
    for (const [decimal, fraction] of Object.entries(fractions)) {
        if (Math.abs(remaining - decimal) < 0.01) {
            return whole > 0 ? `${whole} ${fraction}` : fraction;
        }
    }
    
    // Return as decimal, removing unnecessary zeros
    return amount % 1 === 0 ? amount.toString() : amount.toFixed(2).replace(/\.?0+$/, '');
}

// Rating System
function initRatingSystem() {
    const ratingStars = document.querySelectorAll('.rating-input .fa-star');
    const ratingForm = document.getElementById('rating-form');
    
    ratingStars.forEach((star, index) => {
        star.addEventListener('click', () => submitRating(index + 1, ratingForm));
        star.addEventListener('mouseenter', () => highlightStars(index + 1));
        star.addEventListener('mouseleave', () => resetStarHighlight());
    });
}

function highlightStars(rating) {
    const stars = document.querySelectorAll('.rating-input .fa-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove('far');
            star.classList.add('fas');
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
        }
    });
}

function resetStarHighlight() {
    const currentRating = document.getElementById('current-user-rating');
    const rating = currentRating ? parseInt(currentRating.value) : 0;
    highlightStars(rating);
}

function submitRating(rating, form) {
    if (!form) return;
    
    const formData = new FormData();
    formData.append('rating', rating);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateAverageRating(data.new_average);
            updateUserRating(data.user_rating);
            showToast('Thank you for your rating!', 'success');
        } else {
            showToast(data.error || 'Error submitting rating', 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting rating:', error);
        showToast('Error submitting rating', 'error');
    });
}

function updateAverageRating(average) {
    const avgRatingElement = document.getElementById('average-rating');
    if (avgRatingElement) {
        const stars = avgRatingElement.querySelectorAll('.fa-star');
        stars.forEach((star, index) => {
            if (index < Math.round(average)) {
                star.classList.remove('far');
                star.classList.add('fas');
            } else {
                star.classList.remove('fas');
                star.classList.add('far');
            }
        });
    }
}

function updateUserRating(rating) {
    const userRatingInput = document.getElementById('current-user-rating');
    if (userRatingInput) {
        userRatingInput.value = rating;
    }
    highlightStars(rating);
}

// Comment System
function initCommentSystem() {
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentSubmit);
    }
}

function handleCommentSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addCommentToList(data.comment);
            form.reset();
            showToast('Comment added successfully!', 'success');
        } else {
            showToast(data.error || 'Error adding comment', 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting comment:', error);
        showToast('Error submitting comment', 'error');
    });
}

function addCommentToList(comment) {
    const commentsList = document.getElementById('comments-list');
    if (!commentsList) return;
    
    const commentElement = document.createElement('div');
    commentElement.className = 'comment-item slide-in';
    commentElement.innerHTML = `
        <div class="comment-meta">
            <strong>${comment.author}</strong> • ${comment.created_at}
        </div>
        <div class="comment-content">${comment.content}</div>
    `;
    
    commentsList.insertBefore(commentElement, commentsList.firstChild);
}

// Shopping List
function initShoppingList() {
    const checkboxes = document.querySelectorAll('.shopping-item input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const item = this.closest('.shopping-item');
            if (this.checked) {
                item.classList.add('checked');
            } else {
                item.classList.remove('checked');
            }
        });
    });
    
    // Add to shopping list button
    const addToShoppingBtn = document.getElementById('add-to-shopping');
    if (addToShoppingBtn) {
        addToShoppingBtn.addEventListener('click', addToShoppingList);
    }
}

function addToShoppingList() {
    const recipeId = document.querySelector('[data-recipe-id]')?.dataset.recipeId;
    const servings = document.getElementById('serving-count')?.textContent || '4';
    
    if (!recipeId) return;
    
    const url = `/shopping-list?recipes=${recipeId}&servings=${servings}`;
    window.open(url, '_blank');
    showToast('Added to shopping list!', 'success');
}

// Image Preview
function initImagePreview() {
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`;
                    imagePreview.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.innerHTML = '';
                imagePreview.classList.add('d-none');
            }
        });
    }
}

// Dynamic Ingredient Management
function initIngredientManager() {
    const addIngredientBtn = document.getElementById('add-ingredient');
    if (addIngredientBtn) {
        addIngredientBtn.addEventListener('click', addIngredientField);
    }
    
    // Remove ingredient functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-ingredient')) {
            e.target.closest('.ingredient-group').remove();
        }
    });
}

function addIngredientField() {
    const container = document.getElementById('ingredients-container');
    if (!container) return;
    
    const ingredientCount = container.children.length;
    const newIngredient = document.createElement('div');
    newIngredient.className = 'ingredient-group row mb-3';
    newIngredient.innerHTML = `
        <div class="col-md-4">
            <input type="text" class="form-control" name="ingredient_name" placeholder="Ingredient name" required>
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control" name="ingredient_amount" placeholder="Amount">
        </div>
        <div class="col-md-2">
            <select class="form-control" name="ingredient_unit">
                <option value="">Unit</option>
                <option value="cup">Cup</option>
                <option value="tbsp">Tbsp</option>
                <option value="tsp">Tsp</option>
                <option value="oz">Oz</option>
                <option value="lb">Lb</option>
                <option value="g">Gram</option>
                <option value="kg">Kg</option>
                <option value="ml">ml</option>
                <option value="l">Liter</option>
                <option value="piece">Piece</option>
                <option value="to taste">To taste</option>
            </select>
        </div>
        <div class="col-md-3">
            <input type="text" class="form-control" name="ingredient_notes" placeholder="Notes (optional)">
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-danger btn-sm remove-ingredient">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    container.appendChild(newIngredient);
    newIngredient.classList.add('slide-in');
}

// Utility Functions
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Search functionality
function initSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Add debounced search
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length > 2) {
                    // Implement live search if needed
                    console.log('Searching for:', this.value);
                }
            }, 300);
        });
    }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', initSearch);

// Smooth page transitions
function addPageTransitions() {
    // Add fade-in effect to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Please wait...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

// Initialize page transitions
document.addEventListener('DOMContentLoaded', addPageTransitions);