start-docs-dev:
	docker-compose up

build-docs:
	docker-compose run vitepress python3 ./generate-types-doc.py > specification/generated-types.md && npm run docs:build

