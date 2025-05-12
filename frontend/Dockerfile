FROM node:20-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json pnpm-lock.yaml ./
# Use pnpm instead of npm
RUN npm install -g pnpm && pnpm install

# Copy project files
COPY . .

# Set environment variables
ENV VITE_API_URL=http://backend:5000/api

# Expose Vite dev server port
EXPOSE 5173

# Start Vite dev server with host option directly
CMD ["sh", "-c", "pnpm exec vite --host 0.0.0.0"]
