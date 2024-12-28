import os
from flask import Flask, render_template, request, jsonify
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_config = {
    'MYSQL_HOST': os.getenv('MYSQL_HOST'),
    'MYSQL_PORT': int(os.getenv('MYSQL_PORT', 3306)),
    'MYSQL_USER': os.getenv('MYSQL_USER'),
    'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD'),
    'MYSQL_DB': os.getenv('MYSQL_DB', 'chat_db')
}
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=db_config['MYSQL_HOST'],
            port=db_config['MYSQL_PORT'],
            user=db_config['MYSQL_USER'],
            password=db_config['MYSQL_PASSWORD'],
            database=db_config['MYSQL_DB']
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
def init_db():
    db = get_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            message TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )''')
        db.commit()
        cursor.close()
        db.close()

init_db()

@app.route('/live_chat')
def live_chat():
    return render_template('live_chat.html')

@app.route('/get_messages')
def get_messages():
    db = get_db_connection()
    if db:
        cursor = db.cursor(dictionary=True) 
        cursor.execute('SELECT message FROM messages ORDER BY timestamp DESC LIMIT 5')
        messages = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify([msg['message'] for msg in messages])
    return jsonify({'error': 'Unable to fetch messages'}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '')
    if message:
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO messages (message) VALUES (%s)', (message,))
            db.commit()
            cursor.close()
            db.close()
            return jsonify({'status': 'success'}), 200
        return jsonify({'error': 'Unable to send message'}), 500
    return jsonify({'error': 'No message provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
