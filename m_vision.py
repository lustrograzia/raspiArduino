
import cv2 as cv
import numpy as np


def num_zeros(img):
    n = img.shape[0] * img.shape[1]
    if n == 307200:
        img_average = np.mean(img)
        inv_img = np.where(img == 0, 150, img)
        inv_img_average = np.mean(inv_img)
        num = (inv_img_average - img_average) / (150/n)


def cut_value(img, low_value, high_value):
    img = np.where(img < low_value, 0, img)
    img = np.where(img > high_value, 0, img)
    return img


def overlap_block(low_value, high_value):
    if low_value >= high_value:
        if low_value == 0:
            high_value = low_value + 1
        else:
            low_value = high_value - 1
    return low_value, high_value


def hsv_cut_v(img, low_v=0, high_v=255):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_img)

    low_v, high_v = overlap_block(low_v, high_v)
    v_img = cut_value(v, low_v, high_v)
    return v_img


def create_track_bar(window):
    def nothing(x):
        pass

    cv.createTrackbar('low_a', window, 0, 255, nothing)
    cv.createTrackbar('high_a', window, 0, 255, nothing)
    cv.createTrackbar('low_b', window, 0, 255, nothing)
    cv.createTrackbar('high_b', window, 0, 255, nothing)
    cv.createTrackbar('low_c', window, 0, 255, nothing)
    cv.createTrackbar('high_c', window, 0, 255, nothing)
    cv.setTrackbarPos('low_a', window, 0)
    cv.setTrackbarPos('high_a', window, 0)
    cv.setTrackbarPos('low_b', window, 0)
    cv.setTrackbarPos('high_b', window, 0)
    cv.setTrackbarPos('low_c', window, 0)
    cv.setTrackbarPos('high_c', window, 0)


def get_track_bar_pos(window):
    low_a = cv.getTrackbarPos('low_a', window)
    high_a = cv.getTrackbarPos('high_a', window)
    low_b = cv.getTrackbarPos('low_b', window)
    high_b = cv.getTrackbarPos('high_b', window)
    low_c = cv.getTrackbarPos('low_c', window)
    high_c = cv.getTrackbarPos('high_c', window)
    return low_a, high_a, low_b, high_b, low_c, high_c


def rgb_track_bar(img, low_r=0, high_r=255, low_g=0, high_g=255, low_b=0, high_b=255):
    b, g, r = cv.split(img)

    low_b, high_b = overlap_block(low_b, high_b)
    low_g, high_g = overlap_block(low_g, high_g)
    low_r, high_r = overlap_block(low_r, high_r)
    b = cut_value(b, low_b, high_b)
    g = cut_value(g, low_g, high_g)
    r = cut_value(r, low_r, high_r)

    cv.imshow('b', b)
    cv.imshow('g', g)
    cv.imshow('r', r)

    bgr = cv.merge([b, g, r])
    cv.imshow('bgr', bgr)


def hsv_track_bar(img, low_h=0, high_h=180, low_s=0, high_s=180, low_v=0, high_v=180):
    if low_h > 180:
        low_h = 180
    if high_h > 180:
        high_h = 180
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_img)

    low_h, high_h = overlap_block(low_h, high_h)
    low_s, high_s = overlap_block(low_s, high_s)
    low_v, high_v = overlap_block(low_v, high_v)
    h = cut_value(h, low_h, high_h)
    s = cut_value(s, low_s, high_s)
    v = cut_value(v, low_v, high_v)

    cv.imshow('h', h)
    cv.imshow('s', s)
    cv.imshow('v', v)

    hsv = cv.merge([h, s, v])
    hsv = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    cv.imshow('hsv', hsv)


def img_filter(img):
    yuv_img = cv.cvtColor(img, cv.COLOR_BGR2YUV)
    hist_img = cv.equalizeHist(yuv_img[:, :, 0])
    blur_img = cv.bilateralFilter(hist_img, 9, 75, 75)
    #cut_img = cut_value(hist_img, 50, 255)
    return blur_img


def easy_circle(img, img_width=640, img_height=480):
    make_img = img.copy()
    cut_img = img_filter(make_img)

    # extract circles
    circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                              param1=70, param2=50, minRadius=0, maxRadius=0)
    if circles is None:
        print('Not detected circles')
        return img
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
        cv.circle(circle_img, center, radius, (0, 255, 255), 2)

    cv.rectangle(img, [i - best_circle[2] for i in best_circle[1]], [i + best_circle[2] for i in best_circle[1]], (255, 0, 0), 2)

    cv.imshow('all circles', circle_img)
