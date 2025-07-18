export PYTHON_VERSIONS := 3.12

.PHONY: dev-build
dev-build: ## Create the docker image for you dev environment.
	docker compose --profile "*" build

.PHONY: dev-clean
dev-clean: ## Remove all the docker containers for this project.
	docker compose --profile "*" down --rmi local --volumes

.PHONY: dev-setup ## Basic environment configuration
dev-setup:
	build-scripts/ca-certs/export-certs

.PHONY: dev-shell
dev-shell: ## Start a shell in the dev container
	docker compose run release sh

.PHONY: dev-test
dev-test: ## Run the tests.
	for PYTHON_VERSION in ${PYTHON_VERSIONS} ; do \
		docker compose run --rm "hubble-shuttle-$$PYTHON_VERSION" python -m unittest discover ; \
	done

.PHONY: build
build: # Build the dist package
	rm -rf /dist && docker compose --profile release run --rm release python -m build

.PHONY: deploy
deploy: # Deploy dist package to testpypi
	make build
	docker compose --profile release run release python -m twine upload --verbose dist/*

.PHONY: test-deploy
test-deploy: # Deploy dist package to testpypi
	make build
	docker compose --profile release run release python -m twine upload --verbose --repository testpypi dist/*

.PHONY: help
help: ## This message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
