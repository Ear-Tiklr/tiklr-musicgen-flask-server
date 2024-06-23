# run.py

from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/*": {"origins": "*", "methods": "*", "allow_headers": "*"}})


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)