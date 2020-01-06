import connection
import cv2

# starte socket connection als server
conn = connection.MySocket()
conn.start_server()

while True:

    # warte auf text
    msg = conn.receive_text().decode('utf-8')
    print(msg + ' detected')
    conn.receive_ok()

    # warte auf bild
    img = conn.receive_image()
    cv2.imwrite('/home/manuel/Bachelor_Arbeit/output/' + msg + '.jpg', img)
    conn.receive_ok()

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

conn.end_server()
