from flask import Flask, request, make_response
import socket
import sys
import datetime
import mysql.connector
from threading import Lock

app = Flask(__name__)

# Global counter and lock
counter = 0
counter_lock = Lock()

# MySQL connection details
db_config = {
    'host' : 'db',
    'user' : 'user',
    'password' : 'password',
    'database' : 'app_db'
}

# Helper function to get internal IP address
def get_internal_ip():
    return socket.gethostbyname(socket.gethostname())


@app.route("/")
def index():
    global counter

    # Increment global counter with thread-safety
    with counter_lock:
        counter += 1

    # Save the counter value to the database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            client_ip VARCHAR(45) NOT NULL,
            server_ip VARCHAR(45) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INT AUTO_INCREMENT PRIMARY KEY,
            value INT NOT NULL
        );
        """)

        # Insert or update the counter value
        cursor.execute("INSERT INTO counter (value) VALUES (%s)", (counter,))

        # Record access log
        client_ip = request.remote_addr
        print('client_ip = ', client_ip, file=sys.stderr)
        server_ip = get_internal_ip()
        print('server_ip = ', server_ip, file=sys.stderr)
        timestamp = datetime.datetime.now()

        cursor.execute(
            "INSERT INTO access_log (timestamp, client_ip, server_ip) VALUES (%s, %s, %s)",
            (timestamp, client_ip, server_ip)
        )
        conn.commit()

    finally:
        cursor.close()
        conn.close()

    # Set a cookie with the server's internal IP for 5 minutes
    server_ip = get_internal_ip()
    response = make_response(f"Internal IP Address of Server: {server_ip}")
    response.set_cookie('srv_id', server_ip, max_age=300)
    
    return response


@app.route("/showcount")
def show_count():
    global counter
    return f"Global Counter: {counter}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
