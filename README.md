# StayHome — Apartment Booking Platform

A full-stack apartment booking platform built for the German short-term rental market. Guests can search, filter, and book verified apartments; hosts can list, manage, and track the performance of their properties.

## Features

**For guests**
- Browse listings with search, price range filtering, and popularity sorting
- Interactive map view with listing location
- Date-range booking with a live availability calendar
- Simulated card payment flow with email confirmation
- Leave and read reviews after a completed stay
- Save listings to favorites
- View host profiles and public ratings

**For hosts**
- Create and edit listings with photo galleries
- Pin the exact location on an interactive map (with reverse/forward geocoding)
- Toggle listing visibility (active/hidden) without deleting it
- Respond publicly to guest reviews
- Track per-listing statistics: views, bookings, revenue, average rating
- View personal statistics: total earned, total spent, listings, bookings, rating

**Platform**
- JWT authentication (email + password)
- Multi-language interface: Russian, English, German, Ukrainian
- Search history and view-count tracking per listing
- Soft-delete for user accounts (no data loss on account removal)
- Full audit history on key models (via `django-simple-history`)
- Swagger/OpenAPI documentation for the entire API

## Tech Stack

- **Backend:** Django, Django REST Framework, SimpleJWT
- **Database:** MySQL 8.4
- **Frontend:** Vanilla HTML/CSS/JavaScript (no framework), Leaflet.js for maps, Flatpickr for date selection
- **Infrastructure:** Docker, Docker Compose
- **Docs:** drf-yasg (Swagger UI)

## Project Structure

├── apps/
│ ├── core/ # shared abstract models (UUID, timestamps)
│ ├── users/ # custom user model, auth, profile
│ ├── listings/ # listings, photos, favorites
│ ├── bookings/ # bookings, payment
│ ├── reviews/ # reviews and host responses
│ └── statist/ # statistics, search/view history
├── config/ # Django project settings, URLs
├── frontend/ # static HTML/CSS/JS client
├── docker-compose.yml
├── Dockerfile
└── requirements.txt


## Running Locally with Docker

1. Clone the repository:
```bash
   git clone https://github.com/Firemaniak/Project_apart_booking.git
   cd Project_apart_booking
```

2. Create a `.env` file in the project root:

SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_ENGINE=mysql
DB_NAME=apart_booking
DB_USER=apart_booking_user
DB_PASSWORD=your-password
DB_ROOT_PASSWORD=your-root-password
DB_HOST=db
DB_PORT=3306


3. Build and start the containers:
```bash
   docker compose up -d --build
```

4. Create a superuser:
```bash
   docker compose exec web python manage.py createsuperuser
```

5. (Optional) Populate the database with sample listings:
```bash
   docker compose exec web python manage.py seed_data --count 30
```

6. Open the app:
   - Frontend: `http://localhost:8000/`
   - Admin panel: `http://localhost:8000/admin/`
   - API docs: `http://localhost:8000/swagger/`

## Test Account

If you ran `seed_data`, a test host account is created automatically:
- **Email:** `test_owner@example.com`
- **Password:** `testpass123`

## API Overview

Full interactive documentation is available at `/swagger/`. Main resource groups:

| Endpoint | Description |
|---|---|
| `/api/users/` | Registration, login (JWT), profile |
| `/api/listings/` | Listings, photos, favorites |
| `/api/bookings/` | Bookings, payment, availability |
| `/api/reviews/` | Reviews and host responses |
| `/api/statistics/` | Listing and user statistics, popular searches |

## License

This project was built as a coursework assignment.