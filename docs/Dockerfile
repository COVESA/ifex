# SPDX-FileCopyrightText: Copyright (c) 2025 Mercedes-Benz Tech Innovation GmbH
# SPDX-License-Identifier: MPL-2.0

# VitePress documentation server
FROM node:24-bullseye-slim

# Set the working directory
WORKDIR /app

COPY package*.json ./

# Clean npm cache and install dependencies
RUN npm cache clean --force && npm install --legacy-peer-deps

# Copy the rest of the documentation files
COPY . .

# Expose the port VitePress uses
EXPOSE 5173

# Default command to run VitePress in dev mode
CMD ["npm", "run", "docs:dev", "--", "--host", "0.0.0.0", "--port", "5173"]