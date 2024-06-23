# run.py

from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/*": {"origins": "*", "methods": "*", "allow_headers": "*"}})


if __name__ == '__main__':
    from waitress import serve
    app.run(port=8080, debug=False)