import mysql.connector

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
            database="fletapp"
        )
        if connection.is_connected():
            print("Connected to database successfully")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
