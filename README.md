# RAG Vault

Premium RAG chat with OTP sign-up, JWT authentication, role-based admin controls, and document source links.

## Local setup

1. Copy `.env.example` to `.env`. Set `JWT_SECRET_KEY`, database values and Gmail SMTP details. Without SMTP, OTP is printed to the API console for local testing only.
2. Start PostgreSQL: `docker compose up -d postgres`.
3. Backend: `cd backend_fastapi`, create a virtual environment, `pip install -r requirements.txt`, then `uvicorn app.main:app --reload`.
4. Frontend: `cd react_frontend`, `npm install`, then `npm run dev`. The Vite proxy forwards browser requests from `/api` to the local backend.
5. Create the first admin once: `docker compose run --rm api python create_admin.py` (or run the same command in the backend virtual environment).

## Deploy to AWS

1. On an EC2 instance with Docker Compose, copy the project and create a production `.env` from `.env.example`.
2. Set a strong database password and JWT secret. Gmail SMTP works for initial deployment; use a dedicated Gmail account and Google App Password. For larger production volume, migrate to AWS SES later. Do not use console OTP outside development.
3. Run `docker compose up -d --build`, then run the admin bootstrap command above once.
4. Put an HTTPS load balancer or reverse proxy in front of port 80. Restrict EC2 security groups to HTTP/HTTPS and do not expose PostgreSQL.

## Roles

- **User:** can sign up, verify email OTP, sign in, ask questions, and open cited source PDFs.
- **Admin:** also gets document upload, list, rename, delete, and source-open tools.

## Gmail OTP setup

1. Create or use a dedicated Gmail account for this app.
2. In that Google account, enable **2-Step Verification**.
3. Open Google Account → Security → **App passwords**, create one named `RAG Vault`, and copy its 16-character password.
4. Put the Gmail address in `SMTP_USERNAME` and `SMTP_FROM`; put that generated App Password (not the normal Gmail password) in `SMTP_PASSWORD`.
