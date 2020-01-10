import cv2

static_back = None
video = cv2.VideoCapture(0)


while True:
    check, frame = video.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if static_back is None:
        static_back = gray
        continue

    diff_frame = cv2.absdiff(static_back, gray)
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    cnts, _ = cv2.findContours(thresh_frame.copy(),
                               cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if cnts:
        text = 'motion: TRUE'
    else:
        text = 'motion: FALSE'

    cv2.putText(frame, text, (15, 25), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 255, 0), 1)
    cv2.imshow('motion viewer', frame)

    key = cv2.waitKey(1)

    if key == 113:
        break

    if key == 32:
        static_back = gray

video.release()

# Destroying all the windows
cv2.destroyAllWindows()
