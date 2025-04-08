SHARED_ARGS = --env-file ./.env  -f compose/api.yml -f compose/worker.yml -f compose/localstack.yml -f compose/local.yml -p page
KNOWN_TARGETS = tests unit-tests restart rebuild stop logs install build start stop
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))
EXEC := /bin/bash
COMPOSE_FILES = -f compose/base.yml -f compose/core.yml -f compose/flipt.yml -f compose/analytics.yml -f compose/app.yml -f compose/meet.yml -f compose/local.overwrite.yml
# COMPOSE_FILES = -f compose/base.yml -f compose/core.yml -f compose/flipt.yml -f compose/app.yml -f compose/meet.yml -f compose/local.overwrite.yml
KNOWN_TARGETS = tests func-tests unit-tests restart rebuild stop logs
ARGS := $(filter-out $(KNOWN_TARGETS),$(MAKECMDGOALS))
EXEC := /bin/bash

# turn ARGS into do-nothing targets
ifneq ($(ARGS),$(MAKECMDGOALS))
$(eval $(ARGS):;@:)
endif

.PHONY: install
install: ## Install the environment and docker images
	@git submodule init
	@git submodule update --recursive
	@cp -i .env.docker.example .env
	@cp -i compose/local.overwrite.example.yml compose/local.overwrite.yml
	# @cp -i frontends/packages/app/src/config.example.js frontends/packages/app/src/config.js
	# @cp -i frontends/packages/meet/src/config.example.js frontends/packages/meet/src/config.js
	# @cp -i docker.example.env .env
	# @cp -i compose/local.example.yml compose/local.yml
	# @docker-compose $(SHARED_ARGS) build
	# @echo "Done"
	# @echo "Please update your local configuration at .env"
	# @echo "Use 'make start' to start dev stack"
	# @echo ""


.PHONY: start
start: ## Start the docker environment
	@docker-compose $(SHARED_ARGS) up -d
	@docker ps

.PHONY: stop
stop: ## Stop the docker environment
	@docker-compose $(SHARED_ARGS) stop $(ARGS)


.PHONY: restart
restart: stop start ## Restart docker environment or a single service using stop/up (Ex: make restart api)

.PHONY: logs
logs: ## Display environment logs (continuous, use CTRL-C to stop)
	@docker-compose $(SHARED_ARGS) logs -f $(ARGS)

.PHONY: destroy
destroy:
	@docker-compose $(SHARED_ARGS) down -v

.PHONY: reset
reset: destroy start
