# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY prisma ./prisma/

RUN apk add --no-cache openssl
RUN npm install

COPY . .

RUN npx prisma generate
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY prisma ./prisma/

RUN npm install --only=production

COPY --from=builder /app/dist ./dist

EXPOSE 4000

CMD ["npm", "start"]
