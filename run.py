"""Point d'entrée local : `python run.py` ou `flask --app run.py run`."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
