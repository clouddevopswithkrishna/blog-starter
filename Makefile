.PHONY: up down build logs backend-shell test-backend

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

backend-shell:
	docker-compose exec backend sh

test-backend:
	docker-compose exec backend npm test

seed:
	docker-compose exec backend npm run seed
