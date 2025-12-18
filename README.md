# Canary Take Home Challenge

A full-stack application that integrates GitHub with Django and Vue via OAuth, allowing users to authenticate with Google, link their GitHub account, and manage repository webhooks.

## Tech Stack

**Backend:**
- Python 3.13 / Django 5
- Django REST Framework
- PostgreSQL
- OAuth 2.0 (Google & GitHub)

**Frontend:**
- Vue 3 + TypeScript
- Vite
- Vue Router
- Axios

**Infrastructure:**
- Docker & Docker Compose

## Features

- **Google OAuth Login** – Users can sign in using their Google account
- **GitHub Account Linking** – Connect your GitHub account via OAuth
- **Repository Listing** – View all your public GitHub repositories
- **Repository Selection** – Select a repository to track
- **Webhook Registration** – Automatically subscribes to `push` and `pull_request` events
- **Webhook Endpoint** – Receives and parses GitHub webhook payloads

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│   (Vue 3)       │     │   (Django)      │     │                 │
│   :5173         │     │   :8000         │     │   :5432         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Google OAuth   │     │  GitHub OAuth   │
│                 │     │  + API          │
└─────────────────┘     └─────────────────┘
```

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended), OR
- Python 3.11+, Node.js 20+, PostgreSQL 16

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/canary-take-home.git
   cd canary-take-home
   ```

2. **Configure OAuth credentials** in `docker-compose.yml`:
   - `GOOGLE_CLIENT_ID` / `VITE_GOOGLE_CLIENT_ID`
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`

3. **Start the stack:**
   ```bash
   docker compose up --build
   ```

4. **Run migrations:**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Access the app:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

### Option 2: Local Development

1. **Backend setup:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GITHUB_CLIENT_ID="your-github-client-id"
   export GITHUB_CLIENT_SECRET="your-github-client-secret"
   export GITHUB_WEBHOOK_SECRET="your-webhook-secret"
   ```

3. **Setup PostgreSQL** and create a database:
   ```sql
   CREATE DATABASE canary_db;
   CREATE USER canary_user WITH PASSWORD 'canary_password';
   GRANT ALL PRIVILEGES ON DATABASE canary_db TO canary_user;
   ```

4. **Run migrations and start backend:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. **Frontend setup** (in a new terminal):
   ```bash
   cd frontend
   npm install
   echo "VITE_GOOGLE_CLIENT_ID=your-google-client-id" > .env
   npm run dev
   ```

## OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services > Credentials**
4. Create an **OAuth 2.0 Client ID** (Web application)
5. Add authorized JavaScript origins: `http://localhost:5173`
6. Copy the Client ID

### GitHub OAuth

1. Go to **Settings > Developer settings > OAuth Apps**
2. Click **New OAuth App**
3. Set:
   - Homepage URL: `http://localhost:5173`
   - Authorization callback URL: `http://localhost:5173/api/github/callback/`
4. Copy the Client ID and generate a Client Secret

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/auth/google/` | Authenticate with Google access token |
| GET | `/api/github/authorize-url/` | Get GitHub OAuth authorization URL |
| GET | `/api/github/callback/` | GitHub OAuth callback handler |
| GET | `/api/github/repos/` | List user's public repositories |
| POST | `/api/github/select-repo/` | Select a repository and register webhook |
| POST | `/api/github/webhook/` | Receive GitHub webhook events |

## Database Models

### AppUser
Stores user profile information linked to Google OAuth.

### GithubAccount
Stores GitHub OAuth credentials for linked accounts.

### RepositorySelection
Tracks selected repositories and their webhook IDs.

## Project Structure

```
canary-take-home/
├── backend/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/                # User authentication app
│   ├── models.py           # AppUser model
│   ├── views.py            # Google OAuth endpoint
│   └── urls.py
├── github_integration/      # GitHub integration app
│   ├── models.py           # GithubAccount, RepositorySelection
│   ├── views.py            # GitHub OAuth, repos, webhooks
│   └── urls.py
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   └── DashboardView.vue
│   │   ├── main.ts
│   │   └── App.vue
│   └── ...
├── docker-compose.yml
├── Dockerfile.backend
└── requirements.txt
```

## License

MIT
