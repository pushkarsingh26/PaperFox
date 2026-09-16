# ──────────────────────────────────────────────────────────────────────────────
# PaperFox Frontend — Production Dockerfile
#
# Multi-stage build:
#   Stage 1 (deps)    — install all node_modules
#   Stage 2 (builder) — build the Next.js application
#   Stage 3 (runner)  — minimal runtime image
#
# Why npm install instead of npm ci:
#   The package-lock.json is generated on Windows x64. npm will not resolve
#   optional packages that target wasm32 (cpu: ['wasm32']) on any native host
#   OS, so their transitive peer dependencies (@emnapi/core, @emnapi/runtime
#   v1.11.x) are structurally absent from a lockfile produced on Windows or
#   Linux x64. npm ci treats this absence as an error; npm install correctly
#   skips those unresolvable optional packages on the current platform and
#   produces a working install. All non-optional packages are still installed
#   deterministically from the lockfile. The Next.js build does not require the
#   skipped WASM32 optional packages.
# ──────────────────────────────────────────────────────────────────────────────

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# Use npm install (not npm ci) — see header comment for why.
RUN npm install

# ─────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_API_URL must be known at build time so Next.js can embed it.
# Pass it as a build argument; the default points to the backend service.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# ─────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy only the built output + standalone server
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
