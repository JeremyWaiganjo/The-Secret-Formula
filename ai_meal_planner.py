import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def generate_meal_plan(user):
    """Generate a personalized weekly meal plan for the user"""
    
    if not openai:
        # Fallback meal plan structure when OpenAI is not available
        return get_fallback_meal_plan(user)
    
    # Calculate BMR and daily calories
    bmr = calculate_bmr(user)
    daily_calories = calculate_daily_calories(bmr, user.workout_frequency, user.goal)
    
    # Create prompt for OpenAI
    prompt = f"""
    Create a personalized weekly meal plan for a {user.age}-year-old {user.gender} who:
    - Weighs {user.weight} kg and is {user.height} cm tall
    - Works out {user.workout_frequency}
    - Has a goal to {user.goal}
    - Needs approximately {daily_calories} calories per day
    
    Please provide a 7-day meal plan with breakfast, lunch, dinner, and 2 snacks each day.
    Include variety, nutritional balance, and consider the user's fitness goals.
    
    Respond with JSON in this exact format:
    {{
        "daily_calories": {daily_calories},
        "plan": {{
            "Monday": {{
                "breakfast": {{
                    "name": "meal name",
                    "description": "detailed description",
                    "calories": estimated_calories,
                    "image": "food_photo_url"
                }},
                "lunch": {{
                    "name": "meal name", 
                    "description": "detailed description",
                    "calories": estimated_calories,
                    "image": "food_photo_url"
                }},
                "dinner": {{
                    "name": "meal name",
                    "description": "detailed description", 
                    "calories": estimated_calories,
                    "image": "food_photo_url"
                }},
                "snack1": {{
                    "name": "snack name",
                    "description": "description",
                    "calories": estimated_calories,
                    "image": "food_photo_url"
                }},
                "snack2": {{
                    "name": "snack name",
                    "description": "description",
                    "calories": estimated_calories,
                    "image": "food_photo_url"
                }}
            }},
            "Tuesday": {{ ... }},
            ... (continue for all 7 days)
        }},
        "tips": ["tip1", "tip2", "tip3"]
    }}
    
    For image URLs, use high-quality food photography from Unsplash API using this format:
    https://source.unsplash.com/400x300/?[food-keywords]
    
    Examples:
    - Oatmeal: https://source.unsplash.com/400x300/?oatmeal,breakfast
    - Turkey wrap: https://source.unsplash.com/400x300/?turkey,wrap,sandwich
    - Grilled chicken: https://source.unsplash.com/400x300/?grilled,chicken,healthy
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional nutritionist and meal planning expert. "
                    + "Create detailed, realistic meal plans that are practical and delicious."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return get_fallback_meal_plan(user)

def calculate_bmr(user):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if user.gender.lower() == 'male':
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
    return bmr

def calculate_daily_calories(bmr, workout_frequency, goal):
    """Calculate daily calorie needs based on activity level and goal"""
    activity_multipliers = {
        'sedentary': 1.2,
        '1-2 times per week': 1.375,
        '3-4 times per week': 1.55,
        '5-6 times per week': 1.725,
        'daily': 1.9
    }
    
    activity_level = activity_multipliers.get(workout_frequency, 1.375)
    maintenance_calories = bmr * activity_level
    
    if goal == 'slim':
        return int(maintenance_calories - 500)  # 500 calorie deficit
    elif goal == 'bulk':
        return int(maintenance_calories + 300)  # 300 calorie surplus
    else:  # maintain
        return int(maintenance_calories)

def get_fallback_meal_plan(user):
    """Provide a basic meal plan when OpenAI is unavailable"""
    daily_calories = calculate_daily_calories(
        calculate_bmr(user), 
        user.workout_frequency, 
        user.goal
    )
    
    if user.goal == 'slim':
        plan_type = "Weight Loss"
        meals = {
            "breakfast": {
                "name": "Greek yogurt with berries and granola",
                "image": "https://images.unsplash.com/photo-1488477304112-4944851de03d?w=400&h=300&fit=crop",
                "calories": 280,
                "description": "Creamy Greek yogurt topped with fresh mixed berries and crunchy granola"
            },
            "lunch": {
                "name": "Grilled chicken salad with mixed vegetables",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
                "calories": 450,
                "description": "Tender grilled chicken breast over fresh mixed greens with colorful vegetables"
            },
            "dinner": {
                "name": "Baked salmon with steamed broccoli and quinoa",
                "image": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400&h=300&fit=crop",
                "calories": 520,
                "description": "Flaky baked salmon with nutritious quinoa and fresh steamed broccoli"
            },
            "snack1": {
                "name": "Apple with almond butter",
                "image": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=300&fit=crop",
                "calories": 180,
                "description": "Crisp apple slices with creamy natural almond butter"
            },
            "snack2": {
                "name": "Carrot sticks with hummus",
                "image": "https://images.unsplash.com/photo-1505576391880-b3f9d713dc4f?w=400&h=300&fit=crop",
                "calories": 120,
                "description": "Fresh crunchy carrot sticks with smooth Mediterranean hummus"
            }
        }
        tips = [
            "Stay hydrated with at least 8 glasses of water daily",
            "Include protein in every meal to maintain muscle mass",
            "Choose whole grains over refined carbohydrates"
        ]
    elif user.goal == 'bulk':
        plan_type = "Muscle Building"
        meals = {
            "breakfast": {
                "name": "Oatmeal with banana, nuts, and protein powder",
                "image": "https://images.unsplash.com/photo-1571167364315-7ba86d3c14cf?w=400&h=300&fit=crop",
                "calories": 580,
                "description": "Hearty oatmeal bowl with fresh banana, mixed nuts, and vanilla protein powder"
            },
            "lunch": {
                "name": "Turkey and avocado wrap with sweet potato",
                "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop",
                "calories": 650,
                "description": "Whole wheat wrap filled with lean turkey, creamy avocado, and roasted sweet potato"
            },
            "dinner": {
                "name": "Lean beef stir-fry with brown rice and vegetables",
                "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&h=300&fit=crop",
                "calories": 720,
                "description": "Tender lean beef with colorful vegetables over nutty brown rice"
            },
            "snack1": {
                "name": "Greek yogurt with granola and honey",
                "image": "https://images.unsplash.com/photo-1488477304112-4944851de03d?w=400&h=300&fit=crop",
                "calories": 320,
                "description": "Thick Greek yogurt with crunchy granola and golden honey drizzle"
            },
            "snack2": {
                "name": "Protein smoothie with banana and peanut butter",
                "image": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400&h=300&fit=crop",
                "calories": 380,
                "description": "Creamy protein smoothie blended with banana and natural peanut butter"
            }
        }
        tips = [
            "Eat protein within 30 minutes after workouts",
            "Include healthy fats like nuts, avocado, and olive oil",
            "Don't skip meals - consistency is key for muscle growth"
        ]
    else:  # maintain
        plan_type = "Maintenance"
        meals = {
            "breakfast": {
                "name": "Scrambled eggs with whole grain toast and avocado",
                "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400&h=300&fit=crop",
                "calories": 420,
                "description": "Fluffy scrambled eggs with multigrain toast and fresh avocado slices"
            },
            "lunch": {
                "name": "Quinoa bowl with grilled chicken and vegetables",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop",
                "calories": 480,
                "description": "Nutritious quinoa bowl topped with grilled chicken and rainbow vegetables"
            },
            "dinner": {
                "name": "Baked cod with roasted vegetables and brown rice",
                "image": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400&h=300&fit=crop",
                "calories": 510,
                "description": "Flaky baked cod with colorful roasted vegetables and fluffy brown rice"
            },
            "snack1": {
                "name": "Mixed nuts and dried fruit",
                "image": "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=400&h=300&fit=crop",
                "calories": 200,
                "description": "Premium mix of almonds, walnuts, cashews with sweet dried fruits"
            },
            "snack2": {
                "name": "Greek yogurt with berries",
                "image": "https://images.unsplash.com/photo-1488477304112-4944851de03d?w=400&h=300&fit=crop",
                "calories": 150,
                "description": "Creamy Greek yogurt with fresh seasonal berries"
            }
        }
        tips = [
            "Focus on balanced nutrition with variety",
            "Listen to your hunger cues",
            "Maintain regular meal timing for better energy levels"
        ]
    
    # Create 7-day plan with variations
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_plan = {}
    
    for day in days:
        weekly_plan[day] = meals.copy()
    
    return {
        "daily_calories": daily_calories,
        "plan_type": plan_type,
        "plan": weekly_plan,
        "tips": tips
    }
