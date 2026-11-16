# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend ./frontend
# Vite build uses index.html at frontend/ root; adjust base to / for subpath deployments
ENV VITE_API_URL=http://localhost:8000
RUN npm run build

# Production stage: serve with nginx
FROM nginx:alpine AS runner

COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Replace default nginx config with SPA fallback + API proxy
RUN rm -f /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
