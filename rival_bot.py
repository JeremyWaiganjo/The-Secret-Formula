import random
from datetime import datetime, timedelta
from app import db
from models import RivalBot, DailyLog

def get_or_create_bot():
    """Get the rival bot or create one if it doesn't exist"""
    bot = RivalBot.query.first()
    if not bot:
        bot = RivalBot(
            name="Bot Jeremy",
            points=0,
            current_streak=0
        )
        db.session.add(bot)
        db.session.commit()
    return bot

def update_bot_performance(user):
    """Update bot performance based on user activity"""
    bot = get_or_create_bot()
    
    # Check if bot should gain points (when user misses a day)
    today = datetime.now().date()
    user_log_today = DailyLog.query.filter_by(
        user_id=user.id,
        log_date=today
    ).first()
    
    # Bot gains points probabilistically and when user misses days
    bot_gain_chance = 0.3  # 30% chance bot gains point each day
    
    if not user_log_today or (not user_log_today.meals_logged and not user_log_today.workout_logged):
        # User missed logging - bot definitely gains points
        bot.points += 1
        bot.current_streak += 1
    elif random.random() < bot_gain_chance:
        # Random chance for bot to gain points
        bot.points += 1
        if random.random() < 0.7:  # 70% chance to continue streak
            bot.current_streak += 1
        else:
            bot.current_streak = 0
    else:
        # Bot might lose streak
        if random.random() < 0.2:  # 20% chance to break streak
            bot.current_streak = 0
    
    bot.last_updated = datetime.utcnow()
    db.session.commit()

def get_bot_status():
    """Get current bot status for display"""
    bot = get_or_create_bot()
    
    # Generate bot motivation message
    messages = [
        "I'm crushing my fitness goals! 💪",
        "Consistency is my middle name! 🔥",
        "Another day, another victory! 🏆",
        "I never miss a workout! 💯",
        "Discipline beats motivation! ⚡",
        "I'm in the zone today! 🎯",
        "Healthy habits = healthy life! 🌟",
        "Challenge accepted! 💪",
        "No excuses, just results! 🚀",
        "I'm unstoppable! ⭐"
    ]
    
    # Adjust message based on bot's current streak
    if bot.current_streak >= 7:
        competitive_messages = [
            "Week streak complete! Can you keep up? 🔥",
            "7 days strong! Your move! 💪",
            "I'm on fire! Try to catch me! 🏆"
        ]
        messages.extend(competitive_messages)
    elif bot.current_streak >= 3:
        messages.extend([
            "3-day streak! I'm feeling strong! 💯",
            "Momentum building! Can you match this? ⚡"
        ])
    
    current_message = random.choice(messages)
    
    # Determine bot mood based on performance
    if bot.current_streak >= 5:
        mood = "confident"
        mood_emoji = "😎"
    elif bot.current_streak >= 2:
        mood = "motivated"
        mood_emoji = "😤"
    else:
        mood = "determined"
        mood_emoji = "🤖"
    
    return {
        "name": bot.name,
        "points": bot.points,
        "current_streak": bot.current_streak,
        "message": current_message,
        "mood": mood,
        "mood_emoji": mood_emoji,
        "last_updated": bot.last_updated
    }

def get_competition_status(user):
    """Get competition comparison between user and bot"""
    bot = get_or_create_bot()
    
    point_difference = user.points - bot.points
    streak_difference = user.current_streak - bot.current_streak
    
    if point_difference > 0:
        point_status = f"You're ahead by {point_difference} points! 🎉"
    elif point_difference < 0:
        point_status = f"Bot is ahead by {abs(point_difference)} points! 😰"
    else:
        point_status = "It's a tie! 🤝"
    
    if streak_difference > 0:
        streak_status = f"Your streak is {streak_difference} days longer! 🔥"
    elif streak_difference < 0:
        streak_status = f"Bot's streak is {abs(streak_difference)} days longer! 💪"
    else:
        streak_status = "Equal streaks! 🤖"
    
    return {
        "point_status": point_status,
        "streak_status": streak_status,
        "user_winning": point_difference > 0,
        "user_points": user.points,
        "bot_points": bot.points,
        "user_streak": user.current_streak,
        "bot_streak": bot.current_streak
    }
