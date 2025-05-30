# AI Meal Planner

An interactive diet companion web app that leverages AI for personalized meal planning, daily nutritional tracking, and gamified fitness motivation.

## Features

- AI-powered personalized meal planning
- Daily nutrition and workout tracking
- Gamified experience with points and achievements
- Competitive element with AI rival bot
- User profile management
- Weekly meal plan generation

## Tech Stack

- **Backend**: Flask with SQLAlchemy
- **Frontend**: Vanilla JavaScript with Bootstrap
- **Database**: PostgreSQL
- **AI Integration**: OpenAI API
- **Package Manager**: Poetry

## Installation

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SESSION_SECRET`: Secret key for Flask sessions
   - `OPENAI_API_KEY`: OpenAI API key for meal planning

3. Run the application:
   ```bash
   poetry run gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Usage

1. Create an account and complete your profile
2. Get your personalized weekly meal plan
3. Track your daily meals and workouts
4. Compete with the AI rival bot
5. Unlock achievements as you progress

## Development

This project uses Poetry for dependency management. All dependencies are listed in `pyproject.toml`.