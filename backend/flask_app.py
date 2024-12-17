from flask import Flask, request, jsonify, abort
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import pymysql
import logging

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

db_config = {
    'user': 'admin',
    'password': 'admin123',
    'host': '34.238.115.35',
    'database': 'usersdb'
}

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Flask API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        abort(500, description="Internal Server Error")

@app.route("/users", methods=["POST"])
def add_user():
    try:
        user = request.json
        logging.info(f"Received user data: {user}")
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (user['username'],))
        existing_user = cursor.fetchone()
        if existing_user:
            abort(400, description="Username already exists")
        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (user['username'], user['email']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(user), 201
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        abort(500, description="Internal Server Error")

@app.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        cursor.close()
        conn.close()
        if cursor.rowcount == 0:
            abort(404, description="User not found")
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        abort(500, description="Internal Server Error")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)
