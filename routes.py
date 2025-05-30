from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, MealPlan, DailyLog, Achievement, UserAchievement, RivalBot
from ai_meal_planner import generate_meal_plan
from rival_bot import update_bot_performance, get_bot_status
from datetime import date, datetime, timedelta
import json

@app.route('/')
def index():
    """Homepage with login/register options"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and not user.is_profile_complete():
            return redirect(url_for('complete_profile'))
        elif user:
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('signup.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash('Account created successfully! Please complete your profile.', 'success')
            return redirect(url_for('complete_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}!', 'success')
            
            if not user.is_profile_complete():
                return redirect(url_for('complete_profile'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            username = user.username
    
    session.clear()
    if username:
        flash(f'Goodbye, {username}! See you soon!', 'success')
    else:
        flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    """Complete user profile after signup"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update user profile
        user.age = int(request.form['age'])
        user.weight = float(request.form['weight'])
        user.height = float(request.form['height'])
        user.gender = request.form['gender']
        user.workout_frequency = request.form['workout_frequency']
        user.goal = request.form['goal']
        user.profile_completed = True
        
        try:
            db.session.commit()
            flash('Profile completed successfully!', 'success')
            return redirect(url_for('meal_plan'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            
    return render_template('complete_profile.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """View and edit user profile"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Update user profile
        user.age = int(request.form['age'])
        user.weight = float(request.form['weight'])
        user.height = float(request.form['height'])
        user.gender = request.form['gender']
        user.workout_frequency = request.form['workout_frequency']
        user.goal = request.form['goal']
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            
    return render_template('profile.html', user=user)

@app.route('/meal_plan')
def meal_plan():
    """Display current meal plan or generate new one"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('profile'))
    
    # Get current week's meal plan
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    current_plan = MealPlan.query.filter_by(
        user_id=user.id,
        week_start=week_start
    ).first()
    
    if not current_plan:
        # Generate new meal plan
        try:
            plan_data = generate_meal_plan(user)
            current_plan = MealPlan(
                user_id=user.id,
                week_start=week_start,
                plan_data=json.dumps(plan_data)
            )
            db.session.add(current_plan)
            db.session.commit()
        except Exception as e:
            flash('Error generating meal plan. Please try again.', 'error')
            return render_template('meal_plan.html', user=user, plan=None)
    
    plan_data = json.loads(current_plan.plan_data)
    return render_template('meal_plan.html', user=user, plan=plan_data)

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    """Daily tracking form"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('profile'))
    
    today = date.today()
    
    if request.method == 'POST':
        # Check if log already exists for today
        existing_log = DailyLog.query.filter_by(
            user_id=user.id,
            log_date=today
        ).first()
        
        meals_logged = bool(request.form.get('meals_logged'))
        workout_logged = bool(request.form.get('workout_logged'))
        notes = request.form.get('notes', '')
        
        if existing_log:
            existing_log.meals_logged = meals_logged
            existing_log.workout_logged = workout_logged
            existing_log.notes = notes
        else:
            new_log = DailyLog(
                user_id=user.id,
                log_date=today,
                meals_logged=meals_logged,
                workout_logged=workout_logged,
                notes=notes
            )
            db.session.add(new_log)
        
        # Update user points and streak
        if meals_logged or workout_logged:
            user.points += 1
            
            # Check yesterday's log for streak calculation
            yesterday = today - timedelta(days=1)
            yesterday_log = DailyLog.query.filter_by(
                user_id=user.id,
                log_date=yesterday
            ).first()
            
            if yesterday_log and (yesterday_log.meals_logged or yesterday_log.workout_logged):
                user.current_streak += 1
            else:
                user.current_streak = 1
                
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
        else:
            user.current_streak = 0
        
        db.session.commit()
        
        # Update rival bot
        update_bot_performance(user)
        
        # Check for achievements
        check_achievements(user)
        
        flash('Daily log updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get today's log if exists
    today_log = DailyLog.query.filter_by(
        user_id=user.id,
        log_date=today
    ).first()
    
    return render_template('tracker.html', user=user, today_log=today_log)

@app.route('/dashboard')
def dashboard():
    """Main dashboard with stats and rival bot"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('profile'))
    
    # Get recent logs (last 7 days)
    seven_days_ago = date.today() - timedelta(days=7)
    recent_logs = DailyLog.query.filter(
        DailyLog.user_id == user.id,
        DailyLog.log_date >= seven_days_ago
    ).order_by(DailyLog.log_date.desc()).all()
    
    # Get user achievements
    user_achievements = UserAchievement.query.filter_by(user_id=user.id).all()
    achievement_names = [ua.achievement.name for ua in user_achievements]
    
    # Get rival bot status
    bot_status = get_bot_status()
    
    return render_template('dashboard.html', 
                         user=user, 
                         recent_logs=recent_logs,
                         achievements=achievement_names,
                         bot=bot_status)

@app.route('/regenerate_meal_plan', methods=['POST'])
def regenerate_meal_plan():
    """Generate a new meal plan for current week"""
    if 'user_id' not in session:
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('profile'))
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    # Delete existing plan for this week
    existing_plan = MealPlan.query.filter_by(
        user_id=user.id,
        week_start=week_start
    ).first()
    
    if existing_plan:
        db.session.delete(existing_plan)
    
    try:
        # Generate new meal plan
        plan_data = generate_meal_plan(user)
        new_plan = MealPlan(
            user_id=user.id,
            week_start=week_start,
            plan_data=json.dumps(plan_data)
        )
        db.session.add(new_plan)
        db.session.commit()
        flash('New meal plan generated successfully!', 'success')
    except Exception as e:
        flash('Error generating new meal plan. Please try again.', 'error')
    
    return redirect(url_for('meal_plan'))

def check_achievements(user):
    """Check and award achievements to user"""
    # Initialize achievements if they don't exist
    if Achievement.query.count() == 0:
        achievements = [
            Achievement(name="First Steps", description="Complete your first daily log", 
                       icon="star", points_required=1),
            Achievement(name="Streak Master", description="Maintain a 3-day streak", 
                       icon="fire", streak_required=3),
            Achievement(name="Week Warrior", description="Maintain a 7-day streak", 
                       icon="crown", streak_required=7),
            Achievement(name="Points Pioneer", description="Earn 10 points", 
                       icon="gem", points_required=10),
            Achievement(name="Dedication Expert", description="Earn 25 points", 
                       icon="trophy", points_required=25)
        ]
        for achievement in achievements:
            db.session.add(achievement)
        db.session.commit()
    
    # Check which achievements user should have
    available_achievements = Achievement.query.all()
    user_achievement_ids = [ua.achievement_id for ua in user.achievements]
    
    for achievement in available_achievements:
        if achievement.id not in user_achievement_ids:
            earned = False
            
            if achievement.points_required and user.points >= achievement.points_required:
                earned = True
            elif achievement.streak_required and user.current_streak >= achievement.streak_required:
                earned = True
            
            if earned:
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                flash(f'Achievement unlocked: {achievement.name}!', 'achievement')
    
    db.session.commit()
