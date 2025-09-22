# Use an official Node.js image
FROM node:24-bullseye-slim

# Python is no longer needed in this image since type generation is handled separately

# Set the working directory
WORKDIR /app

# Copy the package.json and package-lock.json (if available)
COPY package*.json ./

# Clean npm cache and install dependencies
RUN npm cache clean --force && npm install --legacy-peer-deps

# Copy the rest of the documentation files
COPY . .

# Run the Python script to generate the Markdown file
# RUN python3 generate-types-doc.py > specification/generated-types.md

# Expose the port VitePress uses
EXPOSE 5173

# Default command to run VitePress in dev mode
CMD ["npm", "run", "docs:dev", "--", "--host", "0.0.0.0", "--port", "5173"]