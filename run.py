from app import create_app
from waitress import serve
import os

# Create the app instance
app = create_app()

if __name__ == "__main__":
    ENV = os.getenv("FLASK_ENV", "development").lower()

    if ENV == "development":
        # Run Flask’s built-in server in development mode
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        # Use Waitress for production
        serve(app, host="0.0.0.0", port=5000)
