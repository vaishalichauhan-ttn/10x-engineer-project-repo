# PromptLab Frontend

React frontend for PromptLab, bootstrapped with Vite.

## Setup

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` by default.

## API integration

This app uses a reusable fetch client in `src/api/client.js`.

- Default API base URL: `/api`
- Vite dev proxy forwards `/api/*` to `http://localhost:8000/*`
- Optional override via `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

You can start from `.env.example`.

## Structure

```text
src/
  api/        # API client + endpoint modules
  components/ # Reusable UI components
  config/     # Runtime/frontend config
  pages/      # Route-level page components
  styles/     # Global styles
```
