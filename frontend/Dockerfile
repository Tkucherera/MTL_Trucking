FROM node:22-alpine AS base

# Dependencies 
FROM base AS deps 
RUN apk add --no-cache libc6-compat
WORKDIR /app


# Copy files 
COPY package.json package-lock.json ./
RUN npm ci 


# Rebuild source code only when needed 
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# SET Environment variables 
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL



RUN npm run build

RUN if [ ! -f .next/standalone/server.js ]; then \
    echo "ERROR: server.js not found in .next/standalone!!"; \
    ls -R .next; \
    exit 1; \
    fi

# Production image
FROM base AS runner
WORKDIR /app


ENV NODE_ENV=production 

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public 


# Set correct for permission for prerender cache 
RUN mkdir .next 
RUN chown nextjs:nodejs .next


# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone/ /app/
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# CMD ["node", "server.js"]
# Change your CMD to this temporarily
CMD ["sh", "-c", "find /app -name server.js && node server.js"]