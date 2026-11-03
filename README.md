# CreatorSpark — Instagram Content Creation & Planning Platform

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/PostgreSQL%20%2F%20SQLite-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Repo](https://img.shields.io/badge/GitHub-rohitrishe84--bit%2FCREATORSPARK-181717?style=flat&logo=github)](https://github.com/rohitrishe84-bit/CREATORSPARK)

> **GitHub Repository:** [https://github.com/rohitrishe84-bit/CREATORSPARK](https://github.com/rohitrishe84-bit/CREATORSPARK)  
> **Live Deployment Blueprint:** `render.yaml` configured for Render Blueprint deployment  
> **Live Web Service URL:** `https://creatorspark.onrender.com`

---

## Table of Contents
1. [CreatorSpark Overview](#1-creatorspark-overview)
2. [Problem Statement](#2-problem-statement)
3. [Target Users](#3-target-users)
4. [Main Features](#4-main-features)
5. [Technology Stack](#5-technology-stack)
6. [Application Architecture](#6-application-architecture)
7. [Database Design](#7-database-design)
8. [SQL Models](#8-sql-models)
9. [MongoDB Architecture](#9-mongodb-architecture)
10. [FAQ REST API Documentation](#10-faq-rest-api-documentation)
11. [Standard Error-Code Catalog](#11-standard-error-code-catalog)
12. [Spark Assistant Workflow](#12-spark-assistant-workflow)
13. [Support Ticket Management](#13-support-ticket-management)
14. [Third-Party API Integration (Pexels)](#14-third-party-api-integration-pexels)
15. [Environment Variables & Secret Management](#15-environment-variables--secret-management)
16. [Local Installation](#16-local-installation)
17. [Virtual Environment Setup](#17-virtual-environment-setup)
18. [Dependency Installation](#18-dependency-installation)
19. [Database Migrations](#19-database-migrations)
20. [Seed-Data Commands](#20-seed-data-commands)
21. [Running the Development Server](#21-running-the-development-server)
22. [Automated Testing & QA](#22-automated-testing--qa)
23. [GitHub Setup & Version Control](#23-github-setup--version-control)
24. [Render Deployment Guide](#24-render-deployment-guide)
25. [MongoDB Atlas Setup](#25-mongodb-atlas-setup)
26. [Pexels API Setup](#26-pexels-api-setup)
27. [Health Endpoint (`/health/`)](#27-health-endpoint-health)
28. [Media Persistence](#28-media-persistence)
29. [Security Considerations](#29-security-considerations)
30. [Known Limitations](#30-known-limitations)
31. [Future Improvements](#31-future-improvements)

---

## 1. CreatorSpark Overview
**CreatorSpark** is a unified, full-stack Instagram content strategy, planning, and idea-generation platform. It empowers creators across 13+ niches to generate structured Instagram blueprints (hooks, visual directions, frame outlines, captions, categorized hashtags) and organize them into an actionable publishing calendar.

## 2. Problem Statement
Content creators frequently struggle with:
- Running out of content ideas or staring at a blank screen.
- Crafting 3-second visual and audio hooks that stop the scroll.
- Structuring multi-slide Carousels or fast-paced Reels.
- Finding categorized hashtags without falling into spam traps.
- Maintaining an organized, consistent posting calendar.
- Technical troubleshooting when tools fail without clear error context.

CreatorSpark eliminates this creative friction through modular templates, structured outputs, and integrated support.

## 3. Target Users
- **Instagram Influencers & Micro-Creators:** Streamline content brainstorming.
- **UGC Creators:** Generate authentic brand testimonial concepts.
- **Beginner & Faceless Creators:** Get step-by-step visual and b-roll directions.
- **Small Business Owners & Personal Brands:** Build trust, promote offers, and drive saves/shares.
- **Niche Creators:** Beauty, Skincare, Fashion, Lifestyle, Fitness, Food, Travel, Education, Tech.

---

## 4. Main Features
1. **Instagram Content Idea Generator:** Tailored by niche, format (Reels, Carousels, Stories, UGC, etc.), objective, tone, and audience.
2. **Saved Content Library:** Search, filter by niche/format/goal, star favorites, edit and delete concepts.
3. **Content Planner & Schedule:** Calendar and timeline views, tracking statuses (`idea`, `planned`, `in_progress`, `ready`, `published`).
4. **Caption & Hashtag Studio:** Craft punchy or long-form captions with categorized hashtags (Broad, Niche, Community, Topic).
5. **Visual Inspiration Gallery:** High-definition photography discovery powered by Pexels API with curated offline fallback.
6. **Spark Assistant Global Chat Widget:** Available on every page, answering platform FAQs, resolving error codes, and escalating inquiries.
7. **SQL-Backed Knowledge Base & Support Tickets:** Standardized error codes, REST APIs, and user-isolated ticket tracking.

---

## 5. Technology Stack
- **Backend:** Python 3.12 / 3.14, Django 5.0+, Django REST Framework.
- **Relational SQL Database:** SQLite (local development), PostgreSQL (production via `dj-database-url`).
- **NoSQL Database:** MongoDB Atlas via PyMongo (chat history & user feedback).
- **Frontend:** Server-rendered Django Templates, Bootstrap 5.3, Bootstrap Icons, Chart.js.
- **Static Assets:** WhiteNoise with compressed manifest caching.
- **Production Server:** Gunicorn WSGI.
- **Hosting & CI/CD:** GitHub + Render (Web Service & Managed PostgreSQL).

---

## 6. Application Architecture
```
creatorspark/
├── manage.py                   # Django CLI entrypoint
├── requirements.txt            # Production dependencies
├── render.yaml                 # Render Blueprint configuration
├── build.sh                    # Build & migration script for Render
├── .python-version             # Python runtime specification (3.12.8)
├── .env.example                # Safe environment variables template
├── .gitignore                  # Git exclusion rules
├── creatorspark/               # Project configuration
│   ├── settings.py             # Modular environment settings
│   ├── urls.py                 # URL routing & custom 404/500 handlers
│   ├── wsgi.py                 # WSGI application entrypoint
│   └── asgi.py                 # ASGI entrypoint
├── core/                       # Main application
│   ├── models.py               # CreatorProfile, ContentIdea, PlannerEntry, FAQ, ErrorCode, SupportTicket
│   ├── views.py                # Public, dashboard, generator, planner, support views
│   ├── forms.py                # Registration, onboarding, idea editing, tickets
│   ├── middleware.py           # Request logging & correlation ID injection
│   ├── context_processors.py   # Global template context
│   ├── admin.py                # Django Admin configurations
│   ├── tests.py                # 26 automated unit and integration tests
│   ├── services/               # Modular service layer
│   │   ├── generator_service.py # Niche templates & content blueprint engine
│   │   ├── caption_service.py   # Caption copywriting & categorized hashtags
│   │   ├── pexels_service.py    # Pexels API integration with 5s timeout & fallback
│   │   ├── assistant_service.py # SQL FAQ/ErrorCode matching & ticket escalation
│   │   └── mongo_service.py     # MongoDB chat persistence & feedback handler
│   ├── api/                    # REST API endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   └── views.py            # /api/faqs/, /api/error-codes/, /api/assistant/chat/, /health/
│   └── management/commands/    # Idempotent seed commands
│       ├── seed_faqs.py        # Seeds 15 knowledge base FAQs
│       └── seed_error_codes.py # Seeds 10 standardized error codes
├── templates/                  # Responsive Bootstrap templates
│   ├── base.html               # Master layout with global chat widget
│   ├── 404.html                # Custom 404 with Ask Assistant integration
│   ├── 500.html                # Custom 500 with Ask Assistant integration
│   ├── components/             # Reusable navbar, footer, chat widget
│   └── core/                   # Feature views (generator, planner, studio, faq, etc.)
└── static/                     # CSS, JavaScript, and branding assets
    ├── css/style.css           # Creator economy purple/indigo design system
    └── js/                     # chat_widget.js, main.js
```

---

## 7. Database Design
CreatorSpark uses a hybrid database architecture:
- **Relational Data (SQL):** Accounts, creator profiles, content ideas, planner entries, FAQs, error codes, support tickets.
- **Document Store (MongoDB):** Unstructured conversation sessions, assistant messages, and user satisfaction ratings.

---

## 8. SQL Models
- `CreatorProfile`: Linked 1:1 with `User`. Stores niche, display name, handle, target audience, preferred format, and onboarding status.
- `ContentIdea`: Belongs to `User`. Stores title, concept, visual hook, outline, visual direction, caption, hashtags, CTA, difficulty, effort, favorite status, and saved status.
- `PlannerEntry`: Scheduled post tied to a calendar date, time, format, and status (`idea`, `planned`, `in_progress`, `ready`, `published`).
- `FAQ`: Question, answer, category, display order, active status.
- `ErrorCode`: Unique code (`CS-AUTH-001`), title, explanation, possible causes, recommended solution, category, severity.
- `SupportTicket`: Unique ticket ID (`TK-XXXXXX`), user link, subject, description, error code reference, priority, status, and staff notes.

---

## 9. MongoDB Architecture
Configured via `MONGODB_URI` and `MONGODB_DATABASE`.
- `conversations`: Stores `conversation_id`, `user_id`, `created_at`, and an array of `messages` (role, content, timestamp, related_code).
- `feedback`: Stores `feedback_id`, `conversation_id`, `rating` (1-5), `feedback_text`, and timestamp.
- **Resilience:** If MongoDB is offline, `MongoService` logs safely and returns `False` without interrupting core Django functionality.

---

## 10. FAQ REST API Documentation
`GET /api/faqs/`
- **Query Parameters:**
  - `category` (optional): Filter by category (e.g., `General`, `Generator`, `Planner`, `Studio`, `Support`).
  - `q` (optional): Keyword search against question and answer texts.
- **Example Response:**
```json
{
  "count": 15,
  "categories": ["General", "Account", "Generator", "Profile", "Planner", "Studio", "Support"],
  "results": [
    {
      "id": 1,
      "question": "What is CreatorSpark?",
      "answer": "CreatorSpark is an all-in-one Instagram content planning...",
      "category": "General",
      "order": 1
    }
  ]
}
```

---

## 11. Standard Error-Code Catalog
| Code | Title | Severity | Recommended Solution |
|---|---|---|---|
| `CS-AUTH-001` | Authentication Required | Medium | Log in with valid credentials at `/login/`. |
| `CS-AUTH-002` | Access Denied / Unauthorized | High | Ensure you own the resource being modified. |
| `CS-FORM-001` | Invalid Form Submission | Low | Correct highlighted input fields. |
| `CS-GEN-001` | Content Generation Engine Failed | Medium | Verify niche dropdown and click Generate again. |
| `CS-DATA-001` | Saved Idea Not Found | Low | Verify idea exists in your saved library. |
| `CS-PLAN-001` | Invalid Planner Entry | Low | Select a valid calendar date (YYYY-MM-DD). |
| `CS-API-001` | External Media Service Unavailable | Medium | System falls back to curated stock suggestions. |
| `CS-SERVER-001` | Unexpected Server Error | Critical | Refresh page or file a support ticket. |
| `CS-TICK-001` | Support Ticket Creation Error | Medium | Fill out required subject and description. |
| `CS-MONGO-001` | Conversation Storage Degraded | Low | Chat operates normally; history logged locally. |

---

## 12. Spark Assistant Workflow
1. User enters query or clicks an "Ask Assistant" button.
2. The request is dispatched to `POST /api/assistant/chat/`.
3. If an error code format (e.g. `CS-AUTH-001`) is present, `ErrorCode` is queried and explained with solutions.
4. If a question is asked, SQL `FAQ` records are searched via keyword score matching.
5. If no confident match is found, the assistant explains that no verified answer exists and proposes escalating to a Support Ticket.
6. Upon user confirmation, a `SupportTicket` is created with a `TK-XXXXXX` reference.
7. User and assistant exchanges are logged to MongoDB.

---

## 13. Support Ticket Management
- **Creation:** Initiated via the Assistant chat widget or via `/support/`.
- **User Isolation:** Authenticated users can only view their own tickets.
- **Administration:** Support staff can review tickets, update status (`Open`, `In Progress`, `Resolved`, `Closed`), and append resolution notes via Django Admin.

---

## 14. Third-Party API Integration (Pexels)
- **API Key:** Configured via `PEXELS_API_KEY`.
- **Timeout:** Strict 5.0 second connection timeout.
- **Caching:** Successful responses cached for 1 hour.
- **Graceful Fallback:** If key is missing, network fails, or times out, the gallery automatically serves curated high-definition aesthetic creator imagery with photographer credits and lighting tips.

---

## 15. Environment Variables & Secret Management
Configured in `.env` (copy from `.env.example`):
```bash
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@hostname:5432/creatorspark
MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=creatorspark_db
PEXELS_API_KEY=your-optional-pexels-key
```

---

## 16. Local Installation
```bash
git clone https://github.com/rohitrishe84-bit/CREATORSPARK.git
cd CREATORSPARK
```

## 17. Virtual Environment Setup
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

## 18. Dependency Installation
```bash
pip install -r requirements.txt
```

## 19. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 20. Seed-Data Commands
```bash
python manage.py seed_faqs
python manage.py seed_error_codes
```

## 21. Running the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/`.

---

## 22. Automated Testing & QA
Run the full 26-test suite:
```bash
python manage.py test
```
All tests verify model constraints, permissions, APIs, fallbacks, and error codes.

---

## 23. GitHub Setup & Version Control
1. Ensure `.env` is listed in `.gitignore`.
2. Commit and push:
```bash
git add .
git commit -m "feat: complete CreatorSpark master build with hybrid DB and APIs"
git branch -M main
git remote add origin https://github.com/<username>/CREATORSPARK.git
git push -u origin main
```

---

## 24. Render Deployment Guide
1. Push your repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New +** > **Blueprint**.
3. Select your `CREATORSPARK` repository.
4. Render detects `render.yaml` and provisions:
   - **Web Service:** `creatorspark` (Python, `./build.sh`, Gunicorn, WhiteNoise).
   - **PostgreSQL Database:** `creatorspark-db` automatically linked via `DATABASE_URL`.
5. Under Web Service **Environment**, add:
   - `MONGODB_URI`: Your MongoDB Atlas connection string.
   - `PEXELS_API_KEY`: (Optional) Your Pexels API key.
6. Click **Apply Blueprint**. Render runs `build.sh` (collects static files, runs migrations, seeds FAQs and error codes) and launches the application.

---

## 25. MongoDB Atlas Setup
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Create a free M0 cluster.
3. Under **Database Access**, create a user with read/write permissions.
4. Under **Network Access**, add `0.0.0.0/0` (allow access from anywhere for cloud deployment).
5. Click **Connect** > **Drivers** > copy the connection string.
6. Set `MONGODB_URI` in Render environment variables.

---

## 26. Pexels API Setup
1. Sign up for a free developer account at [Pexels API](https://www.pexels.com/api/).
2. Generate an API Key (instant and free).
3. Set `PEXELS_API_KEY` in your `.env` or Render environment settings.

---

## 27. Health Endpoint (`/health/`)
Production health check endpoint verifying database connectivity:
`GET /health/`
```json
{
  "status": "ok",
  "application": "CreatorSpark",
  "version": "1.0.0",
  "timestamp": "2026-11-03T09:45:00.000000+00:00",
  "database": "connected",
  "mongodb": "connected"
}
```

---

## 28. Media Persistence
- Static assets are fingerprinted and served via WhiteNoise with compression.
- Render's ephemeral filesystem is not used for permanent storage. For user file uploads in future iterations, use an S3-compatible object store (e.g. AWS S3, Cloudflare R2).

---

## 29. Security Considerations
- `DEBUG=False` in production with strict secret key enforcement.
- CSRF protection on all forms and API endpoints.
- Secure HTTP headers (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `X-XSS-Protection`).
- Request logging sanitizes passwords, session cookies, and authentication tokens.
- User data isolation enforces that saved ideas and tickets cannot be accessed by unauthorized users.

---

## 30. Known Limitations
- CreatorSpark is a strategy and planning platform; it does not publish directly to Instagram without manual user action.
- Free-tier Render web services spin down after 15 minutes of inactivity; initial wakeup takes ~30 seconds.

---

## 31. Future Improvements
- Official Instagram Graph API direct publishing integration (pending Meta business app verification).
- Multimodal AI hook generation utilizing Google Gemini 1.5/2.0 API.
- Team collaboration and multi-creator workspaces.
- Brand deal and UGC contract tracker.
- Automated carousel graphic exporter with downloadable slide decks.
