COMPOSE_FILES = -f compose/db.yml -p hasaki
KNOWN_TARGETS = install build start stop
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))
EXEC := /bin/bash

.PHONY: install
install: ## Install the environment and docker images
	# @cp -i .env.docker.example .env
	@docker-compose $(COMPOSE_FILES) build
	@echo "Done"
	@echo "Please update your local configuration at .env"
	@echo "Use 'make start' to start dev stack"
	@echo ""


.PHONY: start
start: ## Start the docker environment
	@docker-compose $(COMPOSE_FILES) up -d
	@docker ps


.PHONY: stop
stop: ## Stop the docker environment
	@docker-compose $(COMPOSE_FILES) stop $(ARGS)


.PHONY: restart
restart: stop start


.PHONY: destroy
destroy:
	@docker-compose $(SHARED_ARGS) down -v


.PHONY: logs
logs: ## Display environment logs (continuous, use CTRL-C to stop)
	@docker-compose $(COMPOSE_FILES) logs -f $(ARGS)
