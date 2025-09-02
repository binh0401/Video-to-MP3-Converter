import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config: database credentials
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))  # ensure int

@server.route("/login", methods=["POST"])
def login():
    # Check for auth header
    auth = request.authorization #Use HTTP Basic Auth --> username, password
    if not auth:
        return "Please provide email and password", 401

    # Check the database for user info: email, password
    cur = mysql.connection.cursor()
    result = cur.execute(
        "SELECT email, password FROM users WHERE email=%s", (auth.username,)
    )

    if result > 0:
        # User exists
        user_row = cur.fetchone()
        db_email = user_row[0]
        db_password = user_row[1]

        # Check if password matches
        if auth.username != db_email or auth.password != db_password:
            return "Invalid credentials", 401
        else:
            # Return token to user if credentials are correct
            return createJWT(db_email, os.environ.get("JWT_SECRET"), True), 200
    else:
        # User does not exist
        return "Invalid credentials", 401

@server.route("/validate", methods=["POST"])  # Validate token route
def validate():
    encoded_jwt = request.headers.get("Authorization")

    if not encoded_jwt:
        return "Missing token", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except:
        return "Invalid token", 403

    return decoded, 200

def createJWT(email, secret, authz):
    return jwt.encode(
        {
            "email": email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),  # expires in 1 day
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),  # issued at
            "admin": authz,  # admin: true/false
        },
        secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
