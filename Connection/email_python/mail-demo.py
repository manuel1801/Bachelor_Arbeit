import smtplib
import imghdr
from email.message import EmailMessage
import cv2
import os

img_1 = cv2.imread('test.jpg')
img_2 = cv2.imread('test2.jpg')
msg = EmailMessage()
msg['Subject'] = 'subject'
msg['From'] = 'manuel.barkey@gmail.com'
msg['To'] = 'manuelb95@web.de'
msg.set_content = ('some pictures attached')


for f in os.listdir('.'):
    if f[-3:] != 'jpg':
        continue
    img = cv2.imread(f)
    img = cv2.imencode(".jpg", img)
    img = img[1].tobytes()
    print('sending some ', str(type(img)))

    msg.add_attachment(img, maintype='image', subtype='jpg',
                       filename='filename.jpg')


with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

    smtp.login('manuel.barkey@gmail.com', 'stewie55')
    # smtp.send_message(msg)
