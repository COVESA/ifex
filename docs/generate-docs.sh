#!/bin/bash

# SPDX-FileCopyrightText: Copyright (c) 2025 Mercedes-Benz Tech Innovation GmbH
# SPDX-License-Identifier: MPL-2.0

# Simple documentation generation script

set -e  # Exit on any error

echo "🔍 Generating IFEX documentation..."

# Ensure target directory exists
mkdir -p specification

# Clean up any existing files on error
cleanup() {
    echo "❌ Generation failed. Cleaning up partial files..."
    rm -f specification/generated-types.generated.md specification/ast-structure.generated.md
    exit 1
}
trap cleanup ERR

# Generate header comment
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
HEADER="<!-- This file is auto-generated. Do not edit manually. -->
<!-- Generated on: $TIMESTAMP -->
<!-- Generator: generate-docs.sh -->
"

echo "  🔧 Generating types documentation..."
echo -e "$HEADER" > specification/generated-types.generated.md
cd .. && PYTHONPATH=/app python3 docs/generate-types-doc.py >> docs/specification/generated-types.generated.md
cd docs

echo "  🏗️ Generating AST structure documentation..."
echo -e "$HEADER" > specification/ast-structure.generated.md
cd .. && PYTHONPATH=/app python3 -m ifex.models.ifex.ifex_ast_doc >> docs/specification/ast-structure.generated.md
cd docs

echo "✅ Documentation generated successfully!"
echo "   📄 Generated: specification/generated-types.generated.md"
echo "   📄 Generated: specification/ast-structure.generated.md"

echo "🚀 Documentation generation complete!"
