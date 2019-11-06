
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


def min_max_value(img):
    width, height = img.shape[0], img.shape[1]
    min_value, max_value = 255, 0
    for i in range(width):
        for j in range(height):
            n = int(img[i, j])
            if n is not 0:
                if n < min_value:
                    min_value = n
                if n > max_value:
                    max_value = n
    return min_value, max_value


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


def hsv_track_bar(img, low_h=0, high_h=180, low_s=0, high_s=255, low_v=0, high_v=255):
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


def yuv_track_bar(img, low_y=0, high_y=255, low_u=0, high_u=255, low_v=0, high_v=255):
    yuv_img = cv.cvtColor(img, cv.COLOR_BGR2YUV)
    y, u, v = cv.split(yuv_img)

    low_y, high_y = overlap_block(low_y, high_y)
    low_u, high_u = overlap_block(low_u, high_u)
    low_v, high_v = overlap_block(low_v, high_v)
    y = cut_value(y, low_y, high_y)
    u = cut_value(u, low_u, high_u)
    v = cut_value(v, low_v, high_v)

    cv.imshow('y', y)
    cv.imshow('u', u)
    cv.imshow('v', v)

    yuv = cv.merge([y, u, v])
    yuv = cv.cvtColor(yuv, cv.COLOR_YUV2BGR)
    cv.imshow('yuv', yuv)


def img_filter(img):
    yuv_img = cv.cvtColor(img, cv.COLOR_BGR2YUV)
    hist_img = cv.equalizeHist(yuv_img[:, :, 0])
    blur_img = cv.bilateralFilter(hist_img, 9, 75, 75)
    return blur_img


def draw_hist(img):
    hist_img = np.zeros((480, 270), dtype=np.uint8)
    hist_item = cv.calcHist([img], [0], None, [256], [0, 255])
    cv.normalize(hist_item, hist_item, 0, 255, cv.NORM_MINMAX)
    hist = np.int32(np.around(hist_item))
    for x, y in enumerate(hist):
        cv.line(hist_img, (x + 0, 0 + 10), (x + 0, y + 10), (255, 255, 255))
    cv.line(hist_img, (0, 0 + 10), (0, 5), (255, 255, 255))
    cv.line(hist_img, (5 + 180, 0 + 10), (5 + 180, 5), (255, 255, 255))
    hist_img = np.flipud(hist_img)
    return hist_img


def extract_circle(img):
    # apply filter
    make_img = img.copy()
    filtered_img = img_filter(make_img)

    img_width = img.shape[0]
    img_height = img.shape[1]

    # extract circles
    circles = cv.HoughCircles(filtered_img, cv.HOUGH_GRADIENT, 1, 30,
                              param1=70, param2=50, minRadius=0, maxRadius=0)
    if circles is None:
        print('Not detected circles')
        return -1
    circles = np.uint32(np.around(circles))

    # extract best circle
    circle_img = img.copy()
    best_circle = [1, (0, 0), 0]
    for c in circles[0, :]:
        mask = np.ones((img_width, img_height), dtype=np.uint8)
        center = (c[0], c[1])
        radius = c[2]
        # extract circle img
        cv.circle(mask, center, radius, 0, -1)
        extract_img = np.ma.array(filtered_img, mask=mask)
        # calculate circle standard deviation
        std = np.std(extract_img)
        # find white circle
        if std < best_circle[0]:
            best_circle = [std, center, radius]
        cv.circle(circle_img, center, radius, (0, 255, 255), 2)

    if best_circle[0] is not 1:
        cv.circle(make_img, best_circle[1], 2, (255, 0, 0), 2)

    cv.imshow('circle_img', circle_img)
    cv.imshow('make_img', make_img)
    cv.waitKey(0)

    return best_circle[1]
