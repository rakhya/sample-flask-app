from app import create_app
from app.models import add_sample_data

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Add sample data
    add_sample_data()
    
    # Run the application
    app.run(debug=True)