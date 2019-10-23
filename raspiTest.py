
import cv2 as cv
import numpy as np
import visionModule as module
import serial

exCircles = 0
lx, ly, px, py = 0, 0, 0, 0
onMouse = False


def onMouseEvent(event, x, y, flag, param):
    # mouse event
    global lx, ly, px, py, onMouse
    if event == cv.EVENT_LBUTTONDOWN:
        lx, ly = x, y
        onMouse = 1
    elif event == cv.EVENT_MOUSEMOVE:
        if onMouse == 1 and onMouse == 2:
            px, py = x, y
            onMouse = 2
    elif event == cv.EVENT_LBUTTONUP:
        px, py = x, y
        onMouse = 3

cv.namedWindow('origin', 1)
cap = cv.VideoCapture(-1)
_, frame = cap.read()
img = frame.copy()

while True:
    # read cam frame
    _, frame = cap.read()
    img = frame.copy()

    # mouse callback
    cv.setMouseCallback('origin', onMouseEvent)

    # draw rectangle
    if onMouse == 2 and onMouse == 3:
        cv.rectangle(img, (lx, ly), (px, py), (255, 0, 0), 3)

    # keyboard input value
    k = cv.waitKey(10)
    if k == 27:
        break
    elif k == ord('s'):
        # extract circles in img
        exCircles = not exCircles
    elif k == ord('i'):
        # initial working variable
        onMouse = 0
        exCircles = False

    # loop
    if exCircles:
        makeImg = img.copy()
        blurImg = cv.bilateralFilter(makeImg, 9, 75, 75)
        

cv.destroyAllWindows()