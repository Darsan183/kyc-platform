# Multi-service Dockerfile for KYC Platform
# This builds all services with proper paths

# Stage 1: Backend Build
FROM gradle:8.7-jdk21 AS backend-builder
WORKDIR /app
COPY kyc/pom.xml ./
COPY kyc/src ./src
RUN mvn dependency:go-offline -q --batch-mode && \
    mvn package -DskipTests --batch-mode -Dmaven.javadoc.skip=true -Dmaven.source.skip=true

# Stage 2: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY kyc-frontend/package*.json ./
RUN npm ci
COPY kyc-frontend ./
RUN npm run build

# Stage 3: Agents Build
FROM python:3.12-slim AS agents-builder
WORKDIR /app
COPY kyc/agents/pyproject.toml kyc/agents/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY kyc/agents ./kyc/agents

# Stage 4: Backend Runtime
FROM eclipse-temurin:17-jre-alpine AS backend
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup
WORKDIR /app
COPY --from=backend-builder /app/target/*.jar app.jar
USER 1000
EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseG1GC", "-XX:MaxRAMPercentage=75", "-jar", "/app/app.jar"]

# Stage 5: Frontend Runtime
FROM nginx:alpine AS frontend
COPY --from=frontend-builder /app/out /usr/share/nginx/html
COPY --from=frontend-builder /app/.next/static /usr/share/nginx/html/.next/static
COPY kyc/infrastructure/docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Stage 6: Agents Runtime
FROM python:3.12-slim AS agents
WORKDIR /app
COPY --from=agents-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=agents-builder /app/kyc/agents ./agents
EXPOSE 8000
CMD ["uvicorn", "agents.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Default target
FROM backend