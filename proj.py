import cv2 as cv

img = cv.imread('D:/[doc]/pic/test.jpg')

def nothing(x):
    pass


cv.namedWindow('img', 1)
cv.createTrackbar('thresh', 'img', 0, 255, nothing)
cv.createTrackbar('h', 'img', 0, 180, nothing)
cv.createTrackbar('s', 'img', 0, 255, nothing)
cv.createTrackbar('v', 'img', 0, 255, nothing)
cv.setTrackbarPos('thresh', 'img', 70)
cv.setTrackbarPos('h', 'img', 0)
cv.setTrackbarPos('s', 'img', 0)
cv.setTrackbarPos('v', 'img', 0)


while True:
    nImg = img.copy()

    threshValue = cv.getTrackbarPos('thresh', 'img')
    hValue = cv.getTrackbarPos('h', 'img')
    sValue = cv.getTrackbarPos('s', 'img')
    vValue = cv.getTrackbarPos('v', 'img')

    gImg = cv.cvtColor(nImg, cv.COLOR_BGR2GRAY)
    _, tImg = cv.threshold(gImg, threshValue, 255, cv.THRESH_BINARY)

    hsvImg = cv.cvtColor(nImg, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsvImg)
    h = cv.inRange(h, hValue, hValue+10)
    s = cv.inRange(s, sValue, sValue+10)
    v = cv.inRange(v, vValue, vValue+10)
    h = cv.bitwise_and(nImg, nImg, mask=h)
    s = cv.bitwise_and(nImg, nImg, mask=s)
    v = cv.bitwise_and(nImg, nImg, mask=v)

    k = cv.waitKey(10)
    if k == 27:
        break

    cv.imshow('img', nImg)
    cv.imshow('t', tImg)
    cv.imshow('h', h)
    cv.imshow('s', s)
    cv.imshow('v', v)

cv.destroyAllWindows()