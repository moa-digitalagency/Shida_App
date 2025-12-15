# Shida API Documentation

## Authentication

### POST /api/auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John",
  "age": 25
}
```

### POST /api/auth/login
Login an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### POST /api/auth/logout
Logout the current user.

### GET /api/auth/me
Get current authenticated user info.

## Profile

### GET /api/profile
Get current user's profile.

### PUT /api/profile
Update current user's profile.

**Request Body:**
```json
{
  "name": "John",
  "age": 25,
  "bio": "About me...",
  "religion": "Chrétienne",
  "tribe": "Gombe",
  "profession": "Entrepreneur",
  "objective": "Mariage"
}
```

### POST /api/profile/ghost-mode
Toggle ghost mode (VIP feature).

## Discovery

### GET /api/discovery
Get profiles available for swiping.

### POST /api/discovery/swipe
Swipe on a profile.

**Request Body:**
```json
{
  "profile_id": 1,
  "direction": "right"
}
```

**Response (if match):**
```json
{
  "match": true,
  "match_data": { ... }
}
```

## Matches & Messages

### GET /api/matches
Get all matches (negotiations).

### GET /api/matches/:id/messages
Get messages for a specific match.

### POST /api/matches/:id/messages
Send a message in a match.

**Request Body:**
```json
{
  "content": "Hello!"
}
```

## Tokens

### POST /api/tokens/use
Use one token.

## Dashboard

### GET /api/dashboard/stats
Get dashboard statistics.

**Response:**
```json
{
  "views_total": 34,
  "views_weekly": [8, 5, 6, 7, 10, 12, 8],
  "views_change_percent": 12,
  "tokens": 12,
  "negotiations_count": 3,
  "is_vip": true,
  "vip_type": "Gold"
}
```
