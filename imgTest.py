
import cv2 as cv
import numpy as np
import m_vision as mv
import serial

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
on_track_bar = False
easy_circles = False


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
img_width = o_img.shape[0]
img_height = o_img.shape[1]

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
    elif k == ord('a'):
        easy_circles = not easy_circles
    elif k == ord('i'):
        # initial working variable
        # initial draw rectangle
        on_mouse = 0
        # initial draw circles
        ex_circles = False
        # initial track bar
        on_track_bar = False
        cv.destroyWindow('origin')

    # loop
    if ex_circles:
        make_img = img.copy()
        blur_img = cv.medianBlur(make_img, 5)
        gray_img = cv.cvtColor(blur_img, cv.COLOR_BGR2GRAY)
        zeros_img = np.zeros((img_width, img_height), dtype=np.uint8)

        # cut img
        cut_img = mv.cut_value(gray_img, 40, 255)
        hist_img = cv.equalizeHist(cut_img)
        cut_img = mv.cut_value(hist_img, 40, 255)
        cv.imshow('cutimg', cut_img)

        # contour
        contours, hierarchy = cv.findContours(cut_img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        # draw contour
        for cnt in contours:
            if cv.contourArea(cnt) > 3000:
                cv.drawContours(zeros_img, [cnt], 0, 255, -1)

        cut_img = cv.bitwise_and(cut_img, cut_img, mask=zeros_img)

        cv.imshow('hist', cut_img)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=50, param2=50, minRadius=0, maxRadius=0)
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        for c in circles[0, :]:
            mask = np.zeros((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 255, -1)
            std_img = cv.bitwise_and(cut_img, cut_img, mask=mask)
            inv_std_img = np.where(std_img == 0, 1, 0)
            extract_img = np.ma.array(std_img, mask=inv_std_img)
            std = np.std(extract_img)
            if std < 20:
                cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                print(std)
            cv.circle(img, center, radius, (0, 255, 255), 2)
        cv.imshow('circle', circle_img)

    if easy_circles is True:
        make_img = img.copy()
        gau_img = cv.GaussianBlur(make_img, (5, 5), 0)
        gray_img = cv.cvtColor(gau_img, cv.COLOR_BGR2GRAY)

        hsv_img = cv.cvtColor(gau_img, cv.COLOR_BGR2HSV)
        h, s, v = cv.split(hsv_img)
        _, s_mask = cv.threshold(s, 50, 255, cv.THRESH_BINARY_INV)
        cut_img = cv.bitwise_and(gray_img, gray_img, mask=s_mask)
        cv.imshow('cuts', cut_img)
        _, v_mask = cv.threshold(v, 50, 255, cv.THRESH_BINARY)
        cut_img = cv.bitwise_and(cut_img, cut_img, mask=v_mask)
        cv.imshow('cut', cut_img)

        """
        # extract circles
        circles = cv.HoughCircles(gray_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=50, param2=50, minRadius=0, maxRadius=0)
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        for c in circles[0, :]:
            mask = np.zeros((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 255, -1)
            std_img = cv.bitwise_and(gray_img, gray_img, mask=mask)
            inv_std_img = np.where(std_img == 0, 1, 0)
            extract_img = np.ma.array(std_img, mask=inv_std_img)
            std = np.std(extract_img)
            if std < 20:
                cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                print(std)
            cv.circle(img, center, radius, (0, 255, 255), 2)
        cv.imshow('circle', circle_img)
        """

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
