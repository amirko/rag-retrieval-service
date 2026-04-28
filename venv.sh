# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

export $(cat .env | xargs)

# Run migrations
alembic upgrade head

# Start the app
uvicorn app.main:app --reload