from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import boto3
import json

app = Flask(__name__)
# AWS Secrets Manager client
secrets_manager_client = boto3.client('secretsmanager', region_name='us-east-1',
                                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

def get_mysql_password():
    secret_name = "bmo/ashu/db_pass"  # Name of your secret in AWS Secrets Manager
    secret_key = "ASHU_DB_PASSWORD"  # Key for retrieving the MySQL root password

    try:
        # Retrieve the secret value
        response = secrets_manager_client.get_secret_value(SecretId=secret_name)
        secret_data = response['SecretString']
        secret_value = json.loads(secret_data)[secret_key]
        return secret_value
    except Exception as e:
        raise e

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'db'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=get_mysql_password(),
        database=os.getenv('MYSQL_DATABASE', 'testdb')
    )
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        # Read the remaining result set to avoid "Unread result found" error
        while cursor.nextset():
            pass
        cursor.close()
        connection.close()
        return render_template('success.html', message="Login to database successful!")
    except mysql.connector.Error as err:
        return render_template('index.html', error=str(err))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)