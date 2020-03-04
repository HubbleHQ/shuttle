export PROJECT_NAME := hubble-shuttle
export PYTHON_VERSIONS := 3.5 3.6 3.7 3.8

.PHONY: dev-build
dev-build: ## Create the docker image for you dev environment.
	docker-compose build

.PHONY: dev-clean
dev-clean: ## Remove all the docker containers for this project.
	docker-compose down --rmi local --volumes

.PHONY: dev-test
dev-test: ## Run the tests.
	for PYTHON_VERSION in ${PYTHON_VERSIONS} ; do \
		docker-compose run --rm "${PROJECT_NAME}-$$PYTHON_VERSION" python -m unittest discover ; \
	done

.PHONY: help
help: ## This message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
