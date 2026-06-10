.PHONY: build up down logs clean test deploy

# Development commands
build:
	docker-compose -f ../infrastructure/docker-compose.yml build

up:
	docker-compose -f ../infrastructure/docker-compose.yml up -d

down:
	docker-compose -f ../infrastructure/docker-compose.yml down

logs:
	docker-compose -f ../infrastructure/docker-compose.yml logs -f

clean:
	docker-compose -f ../infrastructure/docker-compose.yml down -v
	docker system prune -f

# Testing
test:
	./mvnw test -f ../pom.xml

# Production deployment
deploy-helm:
	helm upgrade --install kyc-platform infrastructure/helm \
		--namespace kyc-platform --create-namespace

deploy-k8s:
	kubectl apply -f infrastructure/k8s/manifests/
	kubectl apply -f infrastructure/monitoring/

# Monitoring
monitoring-up:
	docker-compose -f infrastructure/docker-compose.yml up -d prometheus grafana otel-collector

monitoring-down:
	docker-compose -f infrastructure/docker-compose.yml stop prometheus grafana otel-collector