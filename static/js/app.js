// Jeremy's Secret Ingredient - JavaScript App
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize progress animations
    initializeProgressAnimations();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize auto-save functionality
    initializeAutoSave();
    
    // Initialize competition updates
    initializeCompetitionUpdates();
    
    // Initialize achievement animations
    initializeAchievementAnimations();
}

function initializeFormValidation() {
    // Profile form validation
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            if (!validateProfileForm()) {
                e.preventDefault();
                e.stopPropagation();
            }
            profileForm.classList.add('was-validated');
        });
    }
    
    // Tracker form validation
    const trackerForm = document.getElementById('trackerForm');
    if (trackerForm) {
        trackerForm.addEventListener('submit', function(e) {
            if (!validateTrackerForm()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            // Show loading state
            const submitButton = trackerForm.querySelector('button[type="submit"]');
            if (submitButton) {
                showLoadingState(submitButton);
            }
        });
        
        // Auto-save on checkbox changes
        const checkboxes = trackerForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateProgressIndicators();
                showSaveIndicator();
            });
        });
    }
}

function validateProfileForm() {
    const form = document.getElementById('profileForm');
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = ['username', 'email', 'age', 'weight', 'height', 'gender', 'workout_frequency', 'goal'];
    
    requiredFields.forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field && !field.value.trim()) {
            showFieldError(field, `${fieldName.replace('_', ' ')} is required`);
            isValid = false;
        }
    });
    
    // Validate email format
    const emailField = form.querySelector('[name="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            showFieldError(emailField, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Validate numeric ranges
    const ageField = form.querySelector('[name="age"]');
    if (ageField && (parseInt(ageField.value) < 13 || parseInt(ageField.value) > 100)) {
        showFieldError(ageField, 'Age must be between 13 and 100');
        isValid = false;
    }
    
    const weightField = form.querySelector('[name="weight"]');
    if (weightField && (parseFloat(weightField.value) < 30 || parseFloat(weightField.value) > 300)) {
        showFieldError(weightField, 'Weight must be between 30 and 300 kg');
        isValid = false;
    }
    
    const heightField = form.querySelector('[name="height"]');
    if (heightField && (parseInt(heightField.value) < 120 || parseInt(heightField.value) > 250)) {
        showFieldError(heightField, 'Height must be between 120 and 250 cm');
        isValid = false;
    }
    
    return isValid;
}

function validateTrackerForm() {
    const form = document.getElementById('trackerForm');
    if (!form) return true;
    
    const mealsLogged = form.querySelector('[name="meals_logged"]').checked;
    const workoutLogged = form.querySelector('[name="workout_logged"]').checked;
    
    if (!mealsLogged && !workoutLogged) {
        showAlert('Please log at least one activity (meals or workout) to continue.', 'warning');
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    // Remove existing error
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error class
    field.classList.add('is-invalid');
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
    
    // Remove error on input
    field.addEventListener('input', function() {
        field.classList.remove('is-invalid');
        if (errorDiv) {
            errorDiv.remove();
        }
    }, { once: true });
}

function initializeProgressAnimations() {
    // Animate progress bars and counters
    const progressElements = document.querySelectorAll('[data-progress]');
    progressElements.forEach(element => {
        animateProgress(element);
    });
    
    // Animate counter numbers
    const counterElements = document.querySelectorAll('[data-counter]');
    counterElements.forEach(element => {
        animateCounter(element);
    });
}

function animateProgress(element) {
    const targetValue = parseInt(element.dataset.progress);
    const progressBar = element.querySelector('.progress-bar');
    
    if (progressBar) {
        setTimeout(() => {
            progressBar.style.width = targetValue + '%';
            progressBar.style.transition = 'width 2s ease-out';
        }, 500);
    }
}

function animateCounter(element) {
    const targetValue = parseInt(element.dataset.counter || element.textContent);
    const duration = 2000;
    const startTime = Date.now();
    
    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentValue = Math.floor(progress * targetValue);
        
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = targetValue;
        }
    }
    
    updateCounter();
}

function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeAutoSave() {
    const trackerForm = document.getElementById('trackerForm');
    if (!trackerForm) return;
    
    // Auto-save notes field
    const notesField = trackerForm.querySelector('[name="notes"]');
    if (notesField) {
        let saveTimeout;
        notesField.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveNotes(notesField.value);
            }, 2000);
        });
    }
}

function autoSaveNotes(notes) {
    // Save notes to local storage as backup
    localStorage.setItem('tracker_notes_backup', notes);
    showSaveIndicator('Notes auto-saved');
}

function initializeCompetitionUpdates() {
    // Update competition status periodically
    if (document.querySelector('.vs-container') || document.querySelector('[data-bot-status]')) {
        setInterval(updateBotStatus, 60000); // Update every minute
    }
}

function updateBotStatus() {
    // This would typically make an AJAX call to get updated bot status
    // For now, we'll add visual effects to show the bot is "active"
    const botElements = document.querySelectorAll('[data-bot-status]');
    botElements.forEach(element => {
        element.classList.add('success-pulse');
        setTimeout(() => {
            element.classList.remove('success-pulse');
        }, 1000);
    });
}

function initializeAchievementAnimations() {
    // Animate achievement cards on page load
    const achievementCards = document.querySelectorAll('.achievement-badge, .card[data-achievement]');
    achievementCards.forEach((card, index) => {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fadeInUp');
    });
    
    // Add click effects to achievement cards
    achievementCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.add('success-pulse');
            setTimeout(() => {
                this.classList.remove('success-pulse');
            }, 600);
        });
    });
}

function updateProgressIndicators() {
    const trackerForm = document.getElementById('trackerForm');
    if (!trackerForm) return;
    
    const mealsChecked = trackerForm.querySelector('[name="meals_logged"]').checked;
    const workoutChecked = trackerForm.querySelector('[name="workout_logged"]').checked;
    
    // Update visual indicators
    const progressContainer = document.querySelector('.progress-indicators');
    if (progressContainer) {
        let progressValue = 0;
        if (mealsChecked) progressValue += 50;
        if (workoutChecked) progressValue += 50;
        
        const progressBar = progressContainer.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = progressValue + '%';
            progressBar.classList.toggle('bg-success', progressValue === 100);
            progressBar.classList.toggle('bg-warning', progressValue === 50);
        }
    }
}

function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
    button.disabled = true;
    
    // Restore button after 2 seconds (form submission should complete by then)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 2000);
}

function showSaveIndicator(message = 'Changes saved') {
    // Create or update save indicator
    let indicator = document.querySelector('.save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'save-indicator position-fixed top-0 end-0 m-3 alert alert-success alert-dismissible fade';
        indicator.style.zIndex = '9999';
        document.body.appendChild(indicator);
    }
    
    indicator.innerHTML = `
        <i data-feather="check" class="me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    indicator.classList.add('show');
    
    // Initialize feather icons in the new element
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        indicator.classList.remove('show');
    }, 3000);
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || document.querySelector('.container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 5000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Handle form submissions with better UX
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        showLoadingState(submitButton);
    }
});

// Handle navigation with smooth transitions
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href]');
    if (link && link.hostname === window.location.hostname) {
        // Add smooth transition effect
        document.body.style.opacity = '0.8';
        setTimeout(() => {
            document.body.style.opacity = '1';
        }, 200);
    }
});

// Easter egg: Konami code for extra motivation
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

document.addEventListener('keydown', function(e) {
    konamiCode.push(e.keyCode);
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        showMotivationalMessage();
        konamiCode = [];
    }
});

function showMotivationalMessage() {
    const messages = [
        "🎉 You found the secret! Jeremy believes in you!",
        "💪 You're already a champion for trying the Konami code!",
        "🔥 Secret unlocked: Your dedication is your superpower!",
        "⭐ Jeremy's real secret ingredient: It's YOU!"
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    showAlert(randomMessage, 'success');
    
    // Add special visual effect
    document.body.style.animation = 'pulse 0.5s ease-in-out';
    setTimeout(() => {
        document.body.style.animation = '';
    }, 500);
}

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page loaded in ${loadTime}ms`);
            
            if (loadTime > 3000) {
                console.warn('Page load time is slow. Consider optimizing assets.');
            }
        }, 1000);
    });
}
