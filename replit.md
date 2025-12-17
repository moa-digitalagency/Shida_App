# Shida App

A dating/matching application with a unique "negotiation" concept, built with Flask and vanilla JavaScript.

## Overview

Shida is a mobile-first dating app featuring:
- **Home/Dashboard**: User stats, weekly views chart, VIP status, tokens
- **Discovery**: Swipe-based matching with animated cards
- **Negotiations**: Chat interface after matches
- **Profile**: User settings and dossier
- **Market**: Token and subscription purchases
- **Notifications**: Real-time alerts

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS (custom with animations), Vanilla JS
- **Database**: PostgreSQL
- **Icons**: Inline SVGs with Feather Icons CDN fallback

## Project Structure

```
├── app.py              # Flask app initialization
├── main.py             # Entry point
├── models/             # Database models (domain-specific)
│   ├── __init__.py    # Re-exports all models
│   ├── base.py        # SQLAlchemy db instance
│   ├── auth.py        # User, AdminUser
│   ├── social.py      # Profile, Like, Match, Message
│   ├── commerce.py    # Subscription, TokenTransaction, PricingPlan, PromoCode
│   ├── content.py     # Notification, ContentPage, MatchingConfig
│   └── admin.py       # Report, AuditLog, SupportTicket, TicketResponse
├── routes/             # API and view routes
│   ├── api.py         # REST API endpoints
│   └── views.py       # Page routes
├── templates/          # Jinja2 HTML templates
│   ├── auth/          # Login/Register pages
│   ├── app/           # Main app pages
│   └── components/    # Reusable components (bottom_nav)
├── statics/           # Static assets
│   ├── css/           # Stylesheets
│   │   └── style.css  # Main styles with animations
│   ├── js/            # JavaScript
│   └── uploads/       # User uploads
├── services/          # Business logic services
├── security/          # Auth decorators and validators
├── utils/             # Helper utilities
├── lang/              # Translations (French/English)
├── data/              # Static data and seeder
└── docs/              # Documentation complète
    ├── API.md                   # Documentation API REST
    ├── ARCHITECTURE_TECHNIQUE.md # Architecture et stack technique
    ├── MODELE_COMMERCIAL.md     # Monétisation et business model
    ├── GUIDE_UTILISATEUR.md     # Guide pour les utilisateurs finaux
    ├── ADMINISTRATION.md        # Guide admin et modération
    └── SECURITE.md              # Mesures de sécurité
```

## Running the App

The app uses gunicorn and runs on port 5000:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Demo Account

- Email: demo@shida.com
- Password: demo123

## Key Features

1. **Swipe Cards**: Drag cards left/right or use action buttons
2. **Match Popup**: Animated celebration with compatibility score
3. **Token System**: Users need tokens to initiate conversations
4. **VIP Status**: Gold/Platinum tiers with special features
5. **Weekly Stats**: Interactive chart showing profile views
6. **Modern UI**: SVG icons, gradients, and smooth animations

## Design System

### Colors
- Primary Pink: #ff1493
- Primary Gold: #ffd700
- Background Dark: #0a0a0a
- Card Background: #1a1a1a
- Success Green: #00ff88

### Typography
- Font: Poppins (Google Fonts)
- Weights: 300, 400, 500, 600, 700, 800

### Icons
All icons use inline SVGs for:
- Navigation (home, compass, message, user, settings)
- Actions (heart, X, star, send, camera)
- Stats (eye, trending, users, shield)

## API Endpoints

See `docs/API.md` for full documentation.

## User Preferences

- Dark theme with pink and gold accents
- French language as default
- Mobile-first responsive design
- Game-like animations and effects

## Navigation Tab Order

The bottom navigation tabs are ordered as:
1. **Accueil** (Home) - Dashboard with stats
2. **Alertes** - Notifications
3. **Explorer** - Discovery/swipe profiles (accessible without login)
4. **Négociation** - Chat with matches (requires login)
5. **Profil** - User profile and settings (requires login)

## Guest Access

- Discovery page is visible without login for browsing profiles
- Like/dislike interactions require login (redirects to login page)
- Market page is visible without login

## Database Initialization

The app uses `data/init_db.py` which contains hardcoded seed data for production deployment. This ensures profiles and initial data are available without relying on JSON files.

## Recent Changes

- Changed tab order to: Home, Alertes, Explorer, Négociation, Profil
- Replaced "Messages" label with "Négociation" throughout the app
- Added login requirement for swipe interactions on discovery page
- Created init_db.py script with hardcoded profile data for production
- Restructured models into domain-specific files (auth, social, commerce, content, admin)
- Harmonized styles across all pages with consistent CSS design system
- Implemented guest access for discovery and market pages
- Replaced all emojis with SVG icons
- Added Feather Icons CDN to base template
- Redesigned home dashboard with stats cards
- Enhanced bottom navigation with labeled icons
- Added modern animations (fade-in, pulse, shimmer)
- Improved VIP card with gradient effects
