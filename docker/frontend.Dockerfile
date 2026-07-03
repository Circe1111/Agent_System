FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm config set registry https://registry.npmmirror.com && \
    npm ci --only=production

COPY frontend/ .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

RUN rm -rf /etc/nginx/conf.d/default.conf.bak

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]