# MugShot Studio Backend

FastAPI backend for MugShot Studio, handling authentication, image generation jobs, and chat sessions.

## Setup

1.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in the values.
    ```bash
    cp .env.example .env
    ```
    Required variables:
    - `SUPABASE_URL`, `SUPABASE_KEY`
    - `JWT_SECRET` (Generate a secure random string)
    - `GEMINI_API_KEY`, `BYTEDANCE_API_KEY`, `FAL_KEY`
    - `REDIS_URL`

    To generate a secure JWT secret, you can use:
    ```bash
    openssl rand -hex 32
    ```
    Or in Python:
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Migrations**:
    Apply the SQL schema to your Supabase database.
    ```bash
    ./migrations/apply_migrations.sh
    ```
    Or copy the content of `migrations/001_initial_schema.sql` and run it in the Supabase SQL Editor.

## Running Locally

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```
This starts the API (port 8000), Redis, Celery Worker, and Flower.

### Manual Run
1.  Start Redis.
2.  Start API:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  Start Celery Worker:
    ```bash
    celery -A app.worker.celery_app worker --loglevel=info
    ```

## Testing

```bash
pytest
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for Swagger UI.

## API Endpoints

### Authentication

#### POST `/api/v1/auth/start`
Check if user exists by email.
- **Request Body**: `{ "email": "user@example.com" }`
- **Response**: `{ "exists": true/false, "next": "password/create_account/social_login" }`
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/start" \
    -H "Content-Type: application/json" \
    -d '{"email": "user@example.com"}'
  ```

#### POST `/api/v1/auth/signup`
Create a new user account.
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "confirm_password": "securepassword",
    "username": "uniqueusername",
    "full_name": "User Name",
    "dob": "1990-01-01"
  }
  ```
- **Response**: `{ "user_id": "uuid", "next": "confirm_email" }`
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/signup" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user@example.com",
      "password": "securepassword",
      "confirm_password": "securepassword",
      "username": "uniqueusername",
      "full_name": "User Name",
      "dob": "1990-01-01"
    }'
  ```

#### POST `/api/v1/auth/signin`
Sign in to an existing account.
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**: `{ "access_token": "jwt_token", "token_type": "bearer", "user": {user_object} }`
- **Authentication**: None (required for sign-in)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/signin" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user@example.com",
      "password": "securepassword"
    }'
  ```

#### POST `/api/v1/auth/confirm`
Confirm email address.
- **Request Body**: `{ "token": "confirmation_token" }`
- **Response**: `{ "message": "Email confirmed" }`
- **Authentication**: None
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/confirm" \
    -H "Content-Type: application/json" \
    -d '{"token": "confirmation_token"}'
  ```

### Projects

#### POST `/api/v1/projects/`
Create a new thumbnail project.
- **Request Body**: 
  ```json
  {
    "mode": "design",
    "platform": "youtube",
    "width": 1920,
    "height": 1080,
    "headline": "Title",
    "subtext": "Subtitle",
    "vibe": "professional",
    "model_pref": "nano_banana"
  }
  ```
- **Response**: Project object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/projects/" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "mode": "design",
      "platform": "youtube",
      "width": 1920,
      "height": 1080,
      "headline": "Title",
      "subtext": "Subtitle",
      "vibe": "professional",
      "model_pref": "nano_banana"
    }'
  ```

#### GET `/api/v1/projects/{project_id}`
Get project details.
- **Response**: Project object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/projects/PROJECT_ID" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

#### PATCH `/api/v1/projects/{project_id}`
Update project details.
- **Request Body**: Partial project object with fields to update
- **Response**: Updated project object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X PATCH "http://localhost:8000/api/v1/projects/PROJECT_ID" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"headline": "Updated Title"}'
  ```

### Assets

#### POST `/api/v1/assets/upload`
Upload an asset (image).
- **Form Data**: 
  - `file`: Image file
  - `type`: Type of asset (selfie, ref, copy_target, profile_photo)
- **Response**: Asset object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/assets/upload" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -F "file=@image.jpg" \
    -F "type=profile_photo"
  ```

### Jobs

#### POST `/api/v1/jobs/`
Queue a thumbnail generation job.
- **Request Body**: 
  ```json
  {
    "project_id": "uuid",
    "quality": "std",
    "variants": 2,
    "model": "nano_banana"
  }
  ```
- **Response**: `{ "id": "job_id", "status": "queued", "cost_credits": 2 }`
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/jobs/" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "project_id": "project_uuid",
      "quality": "std",
      "variants": 2,
      "model": "nano_banana"
    }'
  ```

#### GET `/api/v1/jobs/{job_id}`
Get job status.
- **Response**: Job status object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/jobs/JOB_ID" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

### Chat

#### POST `/api/v1/chat/new`
Create a new chat session.
- **Request Body**: `{ "session_name": "Chat Name" }` (optional)
- **Response**: `{ "chat_id": "uuid", "url": "https://localhost/c/{chat_id}" }`
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/chat/new" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"session_name": "My Chat"}'
  ```

#### GET `/api/v1/chat/{chat_id}`
Get chat details.
- **Response**: Chat object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/chat/CHAT_ID" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

#### GET `/api/v1/chat/{chat_id}/messages`
Get chat messages.
- **Response**: Array of message objects
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/chat/CHAT_ID/messages" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

#### POST `/api/v1/chat/{chat_id}/messages`
Send a message to a chat.
- **Request Body**: 
  ```json
  {
    "content": "Message content",
    "sender": "user"
  }
  ```
- **Response**: Message object
- **Authentication**: Required (JWT Bearer Token)
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/chat/CHAT_ID/messages" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "content": "Hello!",
      "sender": "user"
    }'
  ```

## Project Structure

- `app/core`: Configuration and Auth logic.
- `app/api/v1/endpoints`: API Routes (Auth, Assets, Chat, Jobs, Projects).
- `app/services`: Provider integrations (Gemini, Bytedance, Fal).
- `app/worker.py`: Celery task definitions.
- `migrations`: SQL migration files.