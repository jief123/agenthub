# Stage 1: Frontend build
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install shared package
COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared/

# Install backend
COPY backend/ /app/backend/
RUN pip install --no-cache-dir /app/backend/

# Copy frontend build
COPY --from=frontend-build /build/dist /app/backend/static/

WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
