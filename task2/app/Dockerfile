FROM node:18-bullseye-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev || npm install --omit=dev

COPY . .

EXPOSE 3000

# Intentionally not setting a non-root USER for the demo (will be flagged by IaC scanners).
CMD ["node", "server.js"]

