# Personal Agent

Personal Agent is a Django REST API for a personal knowledge assistant. It lets users upload personal documents, extract and chunk their content, generate embeddings, and query the knowledge base using a retrieval-augmented generation (RAG) flow. It also supports a nightly AI brain that summarizes newly added knowledge and creates voice briefings.

The project combines:
- Django + Django REST Framework
- PostgreSQL with pgvector
- Celery + Redis for background jobs
- LangChain + Groq for AI processing
- Cloudinary for file storage
- JWT authentication

## Tech stack

- Backend: Django 5.2, DRF
- Database: PostgreSQL
- Vector search: pgvector
- Async jobs: Celery + Redis
- AI: LangChain, LangGraph, Groq-based LLMs
- File storage: Cloudinary
- Auth: JWT via `djangorestframework-simplejwt`
- OCR / document parsing: PyMuPDF, python-docx, python-pptx, PaddleOCR

## Project structure

```text
PERSONAL AGENT/
├── README.md
├── pyproject.toml
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── account/
│       │   ├── models.py
│       │   ├── serializer.py
│       │   ├── urls.py
│       │   ├── views.py
│       │   └── ...
│       ├── document/
│       │   ├── models.py
│       │   ├── serializer.py
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── worker.py
│       │   ├── llm.py
│       │   └── RAG/
│       │       ├── chunking.py
│       │       ├── embedding.py
│       │       └── extract_text.py
│       ├── agent/
│       │   ├── agent.py
│       │   ├── views.py
│       │   ├── urls.py
│       │   └── evaluate_relevance.py
│       └── nightly_brain/
│           ├── models.py
│           ├── tasks.py
│           ├── views.py
│           └── agent/
│               ├── connections.py
│               ├── discovery_agent.py
│               ├── extracttopic.py
│               ├── generate_insight.py
│               ├── generate_summary.py
│               ├── generate_voice.py
│               └── validate_instace.py
```

## High-level flow

1. User registers/logs in.
2. User uploads a document.
3. Document is stored in Cloudinary.
4. Celery worker downloads the file, extracts text, chunks it, creates embeddings, and stores vectors in PostgreSQL.
5. User asks a question via RAG endpoints.
6. The API uses vector similarity to find relevant chunks.
7. An LLM answers using only the retrieved context.
8. Nightly system processes recent user knowledge, finds topics/connections/insights, and generates a voice summary briefing.

## Settings explained (`src/config/settings.py`)

### Core Django config

- `BASE_DIR`: project root
- `SECRET_KEY`: insecure development secret; for production this must be moved to environment variables
- `DEBUG = True`: development mode
- `ALLOWED_HOSTS = []`: no host restrictions in development

### Installed apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.account',
    'apps.document',
    'apps.agent',
    'apps.nightly_brain',
    'django_celery_beat',
]
```

These apps are the core of the project:
- `account`: user auth and profiles
- `document`: file upload, text extraction, vector storage, Q&A/RAG
- `agent`: stateful LangGraph agent orchestration
- `nightly_brain`: daily summary and voice briefing generation
- `django_celery_beat`: periodic scheduler for Celery tasks

### Database

The project uses PostgreSQL:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "personal_agent",
        "USER": "postgres",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "5433",
        "CONN_MAX_AGE": 60,
    }
}
```

This means the app expects a PostgreSQL instance running locally on port 5433. The `pgvector` extension is necessary for vector similarity search.

### Auth and JWT

```python
AUTH_USER_MODEL = 'account.User'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

- The app replaces Django's default user model with custom `account.User`.
- Every protected endpoint uses JWT authentication.

JWT configuration:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}
```

This means:
- access token lasts 15 minutes
- refresh token lasts 30 days
- tokens are not rotated by default

### Cloudinary config

```python
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)
```

This stores uploaded files in Cloudinary and allows the app to fetch them later for processing.

### Celery and Redis

```python
CELERY_BROKER_URL = "redis://127.0.0.1:6378/1"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6378/1"
```

Redis is used as the message broker and result backend. Celery task queues are run in the background to avoid blocking the API.

### Celery beat schedule

```python
CELERY_BEAT_SCHEDULE = {
    "nightly-brain-every-day": {
        "task": "apps.nightly_brain.tasks.nightly_brain",
        "schedule": crontab(hour=2, minute=0),
    },
}
```

The app automatically runs the nightly brain task every day at 2:00 AM.

### Timezone

```python
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True
```

The app is configured to use Indian Standard Time.

## App-by-app explanation

### 1) `apps.account`

This is the authentication and user layer.

Files:
- `models.py`: custom `User` model
- `customemanager.py`: custom user manager for email login
- `serializer.py`: `RegisterSerializer` and `LoginSerializer`
- `views.py`: registration and login APIs
- `urls.py`: auth route setup

Features:
- Email-based authentication (not username-based)
- JWT login flow
- User creation with hashed password via custom manager

Important model:

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
```

This custom user model is used globally by `AUTH_USER_MODEL`.

### 2) `apps.document`

This is the main document intelligence and RAG layer.

Files:
- `models.py`: `Document` and `DocumentChunk`
- `serializer.py`: serializers for file upload and chunk data
- `views.py`: document list, question answering, and similarity search
- `worker.py`: asynchronous document processing job
- `llm.py`: LLM model loader
- `RAG/`: chunking, embedding, text extraction modules

Key models:

`Document`
- `title`
- `user`
- `file` (Cloudinary raw file)
- `file_size`
- `mime_type`
- `uploaded`
- `status` (PENDING, PROCESSING, READY, FAILED)

`DocumentChunk`
- `document`
- `chunk_index`
- `text`
- `embedding` (vector field, 1024 dimensions)
- `metadata`
- `token_count`

This is the real knowledge-base storage for the system.

Workflow:
- Upload file
- Celery worker downloads the file from Cloudinary
- Extract text according to file type
- Split content into chunks
- Generate embeddings
- Save chunks + vectors in PostgreSQL

### 3) `apps.agent`

This app handles the advanced conversational agent powered by LangGraph.

Files:
- `agent.py`: graph workflow definition
- `evaluate_relevance.py`: retriever relevance evaluation
- `views.py`: API endpoint for user questions

Features:
- Query rewriting when retrieval is weak
- Relevance scoring before generation
- Corrective RAG logic
- Thread-based user interaction using `thread_id`

The graph flow:
1. Retrieve relevant chunks
2. Evaluate relevance
3. Retry with rewritten query if poor
4. Generate final answer using the retrieved context

### 4) `apps.nightly_brain`

This app runs a daily intelligent summarization workflow.

Files:
- `models.py`: `NightlySession`, `Discovery`, `Recommendation`, `RecommendationFeedback`, `VoiceBriefing`
- `tasks.py`: scheduled Celery jobs
- `agent/`: discovery, summary, and voice generation logic

This is a personal insight generator that:
- scans recent document chunks from the last day
- extracts topics and connections
- creates summary text
- converts summary into speech
- uploads voice file to Cloudinary
- saves a completed `VoiceBriefing`

## API endpoints

Base URL: `/`

### Authentication endpoints

| Method | Endpoint | Auth | Purpose | Request body | Response |
|---|---|---:|---|---|---|
| POST | `/register/` | No | Register a user | `{ "email": "x@y.com", "password": "secret" }` | Created user or 409 conflict if email exists |
| POST | `/login/` | No | Login and get JWT tokens | `{ "email": "x@y.com", "password": "secret" }` | `{ "access": "...", "refresh": "..." }` |
| POST | `/refresh/` | No | Refresh expired access token | `{ "refresh": "..." }` | New access token |
| POST | `/logout/` | Yes | Blacklist refresh token | `{ "refresh": "..." }` | Success/error status |

### Document endpoints

| Method | Endpoint | Auth | Purpose | Request body | Response |
|---|---|---:|---|---|---|
| GET | `/document/` | Yes | List documents for the current user | None | Array of document objects |
| POST | `/document/` | Yes | Upload a document | `title`, `file` | Created document object |
| GET | `/document/<id>/` | Yes | Retrieve single document | None | Document object |
| PUT | `/document/<id>/` | Yes | Update document | Full document payload | Updated document object |
| PATCH | `/document/<id>/` | Yes | Partial update | Partial fields | Updated document object |
| DELETE | `/document/<id>/` | Yes | Delete document | None | 204 or deletion response |
| POST | `/document/similar/` | Yes | Find semantically similar chunks for text | `{ "message": "..." }` | Similar chunk list |
| POST | `/document/ask/` | Yes | Ask a RAG-based question | `{ "message": "..." }` | `{ "answer": "...", "sources": [...] }` |

### Agent endpoint

| Method | Endpoint | Auth | Purpose | Request body | Response |
|---|---|---:|---|---|---|
| POST | `/agent/` | Yes | Ask a conversational question through LangGraph agent | `{ "message": "...", "thread_id": "optional uuid" }` | `{ "thread_id": "...", "answer": "..." }` |

### Admin

| Method | Endpoint | Auth | Purpose |
|---|---|---:|---|
| GET/POST/PUT/etc | `/admin/` | Admin only | Django admin panel |

## Important endpoint behavior

### `POST /register/`

- Uses `RegisterView` (`generics.CreateAPIView`)
- Creates a user via `RegisterSerializer`
- Handles an email conflict gracefully with HTTP 409
- Returns the created user object unless there is a duplicate email

### `POST /login/`

- Uses `LoginSerializer`
- Authenticates via `authenticate(email, password)`
- Returns JWT access + refresh tokens

### `POST /document/`

- Uses `DocumentView` (`ModelViewSet`)
- User can only access their own documents (`get_queryset` filters by request.user)
- `perform_create` assigns `user=self.request.user`
- On create, it triggers `DocumentProcessWorker.delay(document.id)`
- The actual processing is asynchronous

### `POST /document/similar/`

- Converts incoming message to an embedding
- Finds most similar chunks of the logged-in user using cosine distance
- Returns up to 4 nearest matches

### `POST /document/ask/`

- Only uses the user's own document chunks
- Embeds the user input
- Finds the top matching chunks
- Builds an LLM prompt with those chunks as context
- Returns the answer and source metadata

### `POST /agent/`

- Accepts `message` and optional `thread_id`
- If no `thread_id`, creates a new UUID
- Runs a stateful LangGraph agent with context and retrieval logic
- Response includes `thread_id` to continue a conversation across requests

## Response patterns

Most endpoints return JSON through `rest_framework.response.Response`.

Common statuses:
- `200 OK`: successful read/update
- `201 Created`: object created
- `400 Bad Request`: invalid payload / missing required field
- `401 Unauthorized`: no valid token
- `409 Conflict`: duplicate email or conflict case
- `500 Internal Server Error`: backend processing failure

## Background processing

The app uses Celery heavily.

### `DocumentProcessWorker`

Triggered after a document upload.

It does:
1. Set document status to `PROCESSING`
2. Download file from Cloudinary URL
3. Detect extension
4. Extract text from the document
5. Split into chunks
6. Generate embeddings
7. Save `DocumentChunk` rows with vector embeddings
8. Set status to `READY`
9. Fail gracefully with `FAILED` if any step crashes

### Nightly brain task

`apps.nightly_brain.tasks.nightly_brain`
- finds users who created chunks in the last day
- creates a `NightlySession`
- creates a `VoiceBriefing`
- dispatches `process_user_nightly_brain`

That task then:
- reads the last day's chunks
- runs discovery agent
- builds summary
- generates speech audio
- uploads audio to Cloudinary
- updates `VoiceBriefing` and `NightlySession`

## Key features

- Secure user authentication with JWT
- Personal document storage and retrieval
- AI-powered semantic search using embeddings and pgvector
- RAG question answering grounded only in user documents
- LangGraph corrective retrieval flow with query rewriting and relevance checks
- Background job processing for uploaded documents
- Daily automated insight generation and voice briefing
- Cloudinary-powered file hosting
- Multi-model AI support using Groq LLMs

## Notes and important caveats

- `settings.py` is currently configured for local development.
- The secret key is hardcoded and should not be used in production.
- Database credentials are hardcoded and should move to environment variables.
- Redis is expected at `127.0.0.1:6378`.
- PostgreSQL must support `pgvector`.
- Cloudinary credentials must be set in environment variables:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`

## Environment variables to set

Suggested `.env` values:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
GROQ_API_KEY=your_groq_api_key
DATABASE_NAME=personal_agent
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5433
```

## Suggested startup flow

1. Start PostgreSQL with the `pgvector` extension enabled.
2. Start Redis.
3. Set required environment variables.
4. Run migrations:

```bash
cd src
python manage.py migrate
```

5. Start Celery worker and beat:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

6. Start Django server:

```bash
python manage.py runserver
```

## Summary

This project is a personal AI memory system. It stores personal documents, extracts useful information, builds vector embeddings, answers questions from past content, and creates daily AI-generated briefings. The architecture is centered around Django REST APIs, a vector database, LLM-based retrieval, and background job processing.

The main business value is that the system behaves like a private personal knowledge assistant: it answers based on the user's own documents and keeps context grounded in those documents instead of relying on general knowledge alone.
