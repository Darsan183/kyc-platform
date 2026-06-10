.PHONY: build up down logs clean test deploy

# Development commands
build:
	docker-compose -f docker-compose.yml build

up:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose -f docker-compose.yml down

logs:
	docker-compose -f docker-compose.yml logs -f

clean:
	docker-compose -f docker-compose.yml down -v
	docker system prune -f

# Testing
test:
	./mvnw test -f kyc/pom.xml

# Production deployment
deploy-helm:
	cd kyc/infrastructure && helm upgrade --install kyc-platform helm \
		--namespace kyc-platform --create-namespace

deploy-k8s:
	kubectl apply -f kyc/infrastructure/k8s/manifests/
	kubectl apply -f kyc/infrastructure/monitoring/

# Monitoring
monitoring-up:
	docker-compose -f docker-compose.yml up -d prometheus grafana otel-collector

monitoring-down:
	docker-compose -f docker-compose.yml stop prometheus grafana otel-collector