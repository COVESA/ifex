# Documentation development overview

The documentation, [published](https://covesa.github.io/ifex) on GitHub pages, is using [Vitepress](https://vitepress.dev/) as static site generator. Some parts of the documentation are generated upfront with python scripts. The development setup is docker based and described in the next section:

## Docker-based Development Setup

The documentation system uses Docker to provide a consistent development environment without requiring Python or Node.js to be installed locally:

### Architecture:

The following services are available in the [docker compose file](./docker-compose.yml):

- **`generate-docs` service**: Python container that runs documentation generation scripts. This step has to run before building the vitepress documentation.
- **`vitepress` service**: Node.js container that serves the VitePress development server
- **Service dependency**: VitePress waits for documentation generation to complete before starting

### Generated Files:

These files are used in the documentation:

- `specification/generated-types.generated.md` - Generated from [generate-types-doc.py](./generate-types-doc.py)
- `specification/ast-structure.generated.md` - Generated from [ifex_ast_doc.py](../models/ifex/ifex_ast_doc.py)

### Usage:

```bash
# Start development server (generates docs + starts VitePress)
make dev

# Generate documentation only
make generate

# Build production documentation
make build

# Clean up
make clean
```

The generation process automatically adds headers to indicate the files are auto-generated and includes timestamps.

## Deployment job:

The [GitHub actions workflow](/.github/workflows/docs.yml) encodes the build steps for the Docker-based system.

## Testing new documentation

To preview the production build you can run `make preview`. It will run the [`vitepress preview`](https://vitepress.dev/reference/cli#vitepress-preview) command under the hood.