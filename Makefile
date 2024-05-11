.PHONY: help

help: ## Display this help screen
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install application
	python3 -m pip install .

envs: ## Create virtual environments
	hatch env create

test: ## Run tests
	hatch test

build: ## Build packages
	pyinstaller src/xamin/__main__.py \
        --name xamin \
        --add-data src/xamin/gui/icons:xamin/gui/icons \
        --add-data src/xamin/gui/styles:xamin/gui/styles \
        --windowed --clean

clear: ## Clean (environments)
	hatch env prune
