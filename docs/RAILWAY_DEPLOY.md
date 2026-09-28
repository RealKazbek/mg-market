# Railway deployment

This repository deploys as one Docker-based Railway service. The container runs the FastAPI backend, Telegram bot, Mini App, admin dashboard, and preserves the landing files. FastAPI serves `miniapp/dist` at `/` and `admin/dist` at `/admin`.

1. Connect the GitHub repository to a new Railway project/service.
2. Ensure Railway uses the repository root `Dockerfile` (the included `railway.json` configures this).
3. Create a Railway Volume and mount it at `/data`.
4. Add the environment variables from `.env.example` / the Railway environment checklist. Set `DATABASE_PATH=/data/shop.sqlite3`.
5. Generate a Railway public domain.
6. Set `MINIAPP_URL`, `API_BASE_URL`, `CORS_ORIGINS`, and `TON_MANIFEST_URL` using the generated HTTPS domain. Use the same-origin URL for `MINIAPP_URL` and `API_BASE_URL` when serving the Mini App from this service.
7. Redeploy after saving the production URL variables.
8. Open `https://<railway-domain>/health` and confirm `{"status":"ok"}`.
9. Open the Telegram bot and test `/start`, the Mini App, and (if enabled) admin at `/admin`.

The container listens on `0.0.0.0:$PORT`; Railway supplies `PORT`. No manual `PORT` variable is required. The startup script fails without the existing production-critical values `BOT_TOKEN`, `ADMIN_CHAT_ID`, `ADMIN_PASSWORD`, `ADMIN_TOKEN`, `INTERNAL_SECRET`, `MINIAPP_URL`, `API_BASE_URL`, or `DATABASE_PATH`, and never prints their values.
