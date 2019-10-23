
import cv2 as cv
import numpy as np
import m_vision as mv
import serial

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
on_track_bar = False


def nothing(x):
    pass


def on_mouse_event(event, x, y, flag, param):
    # mouse event
    global lx, ly, px, py, on_mouse
    if event == cv.EVENT_LBUTTONDOWN:
        lx, ly = x, y
        on_mouse = 1
    elif event == cv.EVENT_MOUSEMOVE:
        if on_mouse == 1 or on_mouse == 2:
            px, py = x, y
            on_mouse = 2
    elif event == cv.EVENT_LBUTTONUP:
        px, py = x, y
        on_mouse = 3


o_img = cv.imread('D:/doc/pic/test2.jpg', cv.IMREAD_COLOR)

while True:
    # read cam frame
    img = o_img.copy()

    # mouse callback
    cv.setMouseCallback('origin', on_mouse_event)

    # draw rectangle
    if on_mouse == 2 or on_mouse == 3:
        cv.rectangle(img, (lx, ly), (px, py), (255, 0, 0), 3)

    # keyboard input value
    k = cv.waitKey(10)
    if k == 27:
        break
    elif k == ord('t'):
        if on_track_bar is False:
            on_track_bar = True
            cv.namedWindow('origin', 1)
            mv.create_track_bar('origin')
        else:
            on_track_bar = False
            cv.destroyWindow('origin')
    elif k == ord('s'):
        # extract circles in img
        ex_circles = not ex_circles
    elif k == ord('i'):
        # initial working variable
        # initial draw rectangle
        on_mouse = 0
        # initial draw circles
        ex_circles = False
        # initial track bar
        on_track_bar = False
        cv.destroyWindow('origin')
    if ex_circles:
        make_img = img.copy()
        blur_img = cv.medianBlur(make_img, 5)
        zeros_img = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

        # cut img
        cut_img = mv.hsv_cut_v(blur_img, 50, 255)
        hist_img = cv.equalizeHist(cut_img)
        cut_img = mv.cut_value(hist_img, 50, 255)
        hist_img = cv.equalizeHist(cut_img)
        cut_img = mv.cut_value(hist_img, 50, 255)

        # contour
        contours, hierarchy = cv.findContours(cut_img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        # draw contour
        for cnt in contours:
            if cv.contourArea(cnt) > 1000:
                cv.drawContours(zeros_img, [cnt], 0, 255, -1)

        cut_img = cv.bitwise_and(cut_img, cut_img, mask=zeros_img)

        cv.imshow('hist', cut_img)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=60, param2=60, minRadius=0, maxRadius=0)
        circles = np.uint16(np.around(circles))

        # draw circles
        for c in circles[0, :]:
            center = (c[0], c[1])
            radius = c[2]
            cv.circle(img, center, radius, (0, 255, 255), 2)

        cv.imshow('img', img)

    # loop
    if on_track_bar is True:
        # get track bar pos
        low_a, high_a, low_b, high_b, low_c, high_c = mv.get_track_bar_pos('origin')

        if k == ord('1'):
            # rgb track bar
            mv.rgb_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        elif k == ord('2'):
            # hsv track bar
            mv.hsv_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)

    cv.imshow('origin', img)

cv.destroyAllWindows()
