# Shida App

A dating/matching application with a unique "negotiation" concept, built with Flask and vanilla JavaScript.

## Overview

Shida is a mobile-first dating app featuring:
- **Home/Dashboard**: User stats, weekly views chart, VIP status, tokens
- **Discovery**: Swipe-based matching with animated cards
- **Negotiations**: Chat interface after matches
- **Profile**: User settings and ghost mode

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS (custom with Tailwind-inspired design), Vanilla JS
- **Database**: SQLite (development)

## Project Structure

```
├── app.py              # Main Flask application
├── models/             # Database models (User, Profile, Match, Message)
├── routes/             # API and view routes
│   ├── api.py         # REST API endpoints
│   └── views.py       # Page routes
├── templates/          # Jinja2 HTML templates
│   ├── auth/          # Login/Register pages
│   ├── app/           # Main app pages
│   └── components/    # Reusable components
├── statics/           # Static assets
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript
│   └── uploads/       # User uploads
├── services/          # Business logic services
├── security/          # Auth decorators and validators
├── utils/             # Helper utilities
├── lang/              # Translations (French/English)
├── data/              # Static data (objectives, religions, etc.)
├── logs/              # Application logs
└── docs/              # API documentation
```

## Running the App

```bash
python app.py
```

The app runs on port 5000.

## Demo Account

- Email: demo@shida.com
- Password: demo123

## Key Features

1. **Swipe Cards**: Drag cards left/right or use buttons
2. **Match Popup**: Animated celebration with confetti
3. **Token System**: Users need tokens to initiate conversations
4. **Ghost Mode**: VIP feature to browse anonymously
5. **Weekly Stats**: Chart showing profile views

## API Endpoints

See `docs/API.md` for full documentation.

## User Preferences

- Dark theme with pink (#ff1493) and gold (#ffd700) accents
- French language as default
- Mobile-first responsive design
- Game-like animations and effects
