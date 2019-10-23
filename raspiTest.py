
import cv2 as cv
import numpy as np
import m_vision as mv
import serial

ex_circles = 0
lx, ly, px, py = 0, 0, 0, 0
on_mouse = False


def on_mouse_event(event, x, y, flag, param):
    # mouse event
    global lx, ly, px, py, on_mouse
    if event == cv.EVENT_LBUTTONDOWN:
        lx, ly = x, y
        on_mouse = 1
    elif event == cv.EVENT_MOUSEMOVE:
        if on_mouse == 1 and on_mouse == 2:
            px, py = x, y
            on_mouse = 2
    elif event == cv.EVENT_LBUTTONUP:
        px, py = x, y
        on_mouse = 3


cv.namedWindow('origin', 1)
cap = cv.VideoCapture(-1)
_, frame = cap.read()
img = frame.copy()

while True:
    # read cam frame
    _, frame = cap.read()
    img = frame.copy()

    # mouse callback
    cv.setMouseCallback('origin', on_mouse_event)

    # draw rectangle
    if on_mouse == 2 and on_mouse == 3:
        cv.rectangle(img, (lx, ly), (px, py), (255, 0, 0), 3)

    # keyboard input value
    k = cv.waitKey(10)
    if k == 27:
        break
    elif k == ord('s'):
        # extract circles in img
        ex_circles = not ex_circles
    elif k == ord('i'):
        # initial working variable
        on_mouse = 0
        ex_circles = False

    # loop
    if ex_circles:
        make_img = img.copy()
        blur_img = cv.bilateralFilter(make_img, 9, 75, 75)
        cut_img = mv.hsv_cut_v(blur_img)


cv.destroyAllWindows()
