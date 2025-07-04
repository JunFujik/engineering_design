FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Remove existing node_modules and package-lock.json
RUN rm -rf node_modules package-lock.json

# Install dependencies
RUN npm install

# Copy application code
COPY . .

EXPOSE 3001

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]