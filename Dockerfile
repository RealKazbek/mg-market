# syntax=docker/dockerfile:1

FROM node:20-bookworm-slim AS frontend-builder
WORKDIR /src

COPY miniapp/package.json miniapp/package-lock.json ./miniapp/
RUN npm ci --prefix miniapp
COPY admin/package.json admin/package-lock.json ./admin/
RUN npm ci --prefix admin

COPY shared ./shared
COPY miniapp ./miniapp
COPY admin ./admin
# Empty means same-origin at runtime; no deployment URL is baked into the image.
RUN printf 'VITE_API_URL=\n' > miniapp/.env \
    && npm run build --prefix miniapp
RUN printf 'VITE_API_URL=\n' > admin/.env \
    && npm run build --prefix admin

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY bot/requirements.txt /tmp/bot-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt -r /tmp/bot-requirements.txt

COPY backend ./backend
COPY bot ./bot
COPY landing ./landing
COPY shared ./shared
COPY scripts/start-production.sh ./scripts/start-production.sh
COPY --from=frontend-builder /src/miniapp/dist ./miniapp/dist
COPY --from=frontend-builder /src/admin/dist ./admin/dist

RUN chmod +x ./scripts/start-production.sh \
    && mkdir -p /data

EXPOSE 8000
CMD ["/app/scripts/start-production.sh"]
