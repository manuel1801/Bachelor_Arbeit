import connection

conn = connection.RaspyConnection()

conn.start_client()
conn.send_data('hi', 'text')
conn.end_connection()
