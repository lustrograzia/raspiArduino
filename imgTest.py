
import cv2 as cv
import numpy as np
import m_vision as mv
import glob
import serial

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
on_track_bar = False
easy_circles = False
img_count = 0


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


images = [cv.imread(file) for file in glob.glob('D:/doc/pic/test/*.jpg')]
o_img = images[0]
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
    elif k == ord('n'):
        img_count += 1
        if img_count == len(images):
            img_count = 0
        o_img = images[img_count]
    elif k == ord('i'):
        # initial working variable
        # initial draw rectangle
        on_mouse = 0
        # initial draw circles
        ex_circles = False
        # initial track bar
        on_track_bar = False
        # initial easy circles
        easy_circles = False
        cv.destroyAllWindows()

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
        cv.imshow('cut_img', cut_img)

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
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        best_circle = [100, 0, 0]
        for c in circles[0, :]:
            mask = np.ones((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 0, -1)
            extract_img = np.ma.array(cut_img, mask=mask)
            std = np.std(extract_img)

            if std < best_circle[0]:
                best_circle = [std, center, radius]
            cv.circle(img, center, radius, (0, 255, 255), 2)

        cv.imshow('circle', circle_img)
        cv.imshow('all circles', img)

    if easy_circles is True:
        mv.easy_circle(img, img_width, img_height)

    if on_track_bar is True:
        # get track bar pos
        low_a, high_a, low_b, high_b, low_c, high_c = mv.get_track_bar_pos('origin')

        if k == ord('1'):
            # rgb track bar
            mv.rgb_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        elif k == ord('2'):
            # hsv track bar
            mv.hsv_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        elif k == ord('3'):
            # rgb track bar use one
            one_t = low_a
            if one_t >= 255 - 10:
                one_t = 255 - 10
            mv.rgb_track_bar(img, one_t, one_t + 10, one_t, one_t + 10, one_t, one_t + 10)
        elif k == ord('4'):
            # gray track bar use one
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            one_t = low_a
            if one_t >= 255 - 10:
                one_t = 255 - 10
            cut_gray_img = mv.cut_value(gray_img, one_t, one_t + 10)
            cv.imshow('cut_gray', cut_gray_img)

    cv.imshow('origin', img)

cv.destroyAllWindows()
