set -e

echo "Starting deployment..."

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build and deploy
echo "Building containers..."
docker-compose -f docker-compose.prod.yml build

echo "Stopping old containers..."
docker-compose -f docker-compose.prod.yml down

echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "Cleaning up..."
docker system prune -f

echo "Deployment complete!"

# Show logs
echo "Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=50