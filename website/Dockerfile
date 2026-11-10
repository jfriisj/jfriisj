# Build Astro to static files; runtime remains a small non-root Nginx container.
FROM node:24-alpine AS builder
WORKDIR /site
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.30.6-alpine-slim
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /site/dist/ /usr/share/nginx/html/
USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
CMD ["nginx", "-g", "daemon off;"]
