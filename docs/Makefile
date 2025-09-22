# SPDX-FileCopyrightText: Copyright (c) 2025 Mercedes-Benz Tech Innovation GmbH
# SPDX-License-Identifier: MPL-2.0

# IFEX Documentation Development Tools

.PHONY: help dev build generate preview clean

# Default target
help:
	@echo "IFEX Documentation Development Tools"
	@echo ""
	@echo "Available targets:"
	@echo "  dev       Start development server (with auto-generation)"
	@echo "  build     Build production documentation" 
	@echo "  generate  Generate documentation files only"
	@echo "  preview   Build and preview production documentation"
	@echo "  clean     Clean generated files and Docker cache"
	@echo "  help      Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make dev                   # Start development server"
	@echo "  make generate              # Just regenerate docs"
	@echo "  make build                 # Production build"
	@echo "  make preview               # Build and preview production docs"

dev:
	@echo "🚀 Starting IFEX documentation development server..."
	@echo "   This will:"
	@echo "   1. Generate type defintions based on the current specification"
	@echo "   2. Start VitePress dev server on http://localhost:5173"
	@echo ""
	docker compose up --build vitepress

build:
	@echo "🏗️ Building IFEX documentation for production..."
	@echo "   This will:"
	@echo "   1. Generate fresh documentation"
	@echo "   2. Build static VitePress site"
	@echo ""
	docker compose run --rm generate-docs
	docker compose run --rm vitepress npm run docs:build

generate:
	@echo "📝 Generating documentation only..."
	docker compose run --rm generate-docs

preview: build
	@echo "� Starting IFEX documentation preview server..."
	@echo "   Serving built documentation on http://localhost:4173"
	@echo ""
	docker compose up preview

clean:
	@echo "🧹 Cleaning up generated files and Docker resources..."
	rm -f specification/generated-types.generated.md specification/ast-structure.generated.md
	docker compose down --volumes --remove-orphans
	docker compose build --no-cache

