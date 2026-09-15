FROM node:22-alpine AS compilacao
WORKDIR /aplicacao
ENV NEXT_TELEMETRY_DISABLED=1
ARG API_INTERNA=http://api:8000
ENV API_INTERNA=$API_INTERNA
COPY package.json package-lock.json ./
COPY aplicacoes/web/package.json ./aplicacoes/web/package.json
RUN npm ci
COPY aplicacoes/web/ ./aplicacoes/web/
WORKDIR /aplicacao/aplicacoes/web
RUN npm run build

FROM node:22-alpine AS execucao
WORKDIR /aplicacao
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
RUN addgroup -S observatorio && adduser -S observatorio -G observatorio
COPY --from=compilacao --chown=observatorio:observatorio /aplicacao/aplicacoes/web/.next/standalone ./
COPY --from=compilacao --chown=observatorio:observatorio /aplicacao/aplicacoes/web/.next/static ./aplicacoes/web/.next/static
USER observatorio
EXPOSE 3000
CMD ["node","aplicacoes/web/server.js"]
