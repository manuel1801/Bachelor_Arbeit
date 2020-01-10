import cv2

img = cv2.imread(
    '/home/manuel/Bachelor_Arbeit/workspace/test/20191229_145606.jpg')
#cv2.imshow('normal', img)


def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] -= value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


img_dark = increase_brightness(img, value=50)
cv2.imshow('dark', img_dark)


cv2.waitKey(0)
cv2.destroyAllWindows()
