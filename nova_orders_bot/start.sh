cd /Nova-orders-bot/nova_orders_bot
source venv/bin/activate

# Set the path to your FastAPI application's main module
APP_MODULE="fast_api:app"

# Set the host and port for Uvicorn to listen on
HOST="0.0.0.0"
PORT="8000"

# Start the Uvicorn server
uvicorn $APP_MODULE --host $HOST --port $PORT --reload
