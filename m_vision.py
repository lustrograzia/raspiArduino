
import cv2 as cv
import numpy as np
from datetime import datetime


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


def create_color_table():
    table = [[[i, 255, 255] for i in range(180)]]
    img = table*50
    img = np.uint8(np.array(img))
    img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
    return img


def simplify_color(img, simplify_size=10):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    hsv_img = np.where(hsv_img > 0, hsv_img - hsv_img % simplify_size, hsv_img)
    change_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)
    return change_img


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


def img_filter(img, show=False):
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    hist_img = cv.equalizeHist(gray_img)
    blur_img = cv.bilateralFilter(hist_img, 9, 75, 75)
    if show:
        cv.imshow('phase 1', gray_img)
        cv.imshow('phase 2', hist_img)
        cv.imshow('phase 3', blur_img)
    return gray_img


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


def print_img_value(img):
    width = img.shape[1]
    height = img.shape[0]
    if len(img.shape) > 2:
        channel = img.shape[2]
    else:
        channel = 1

    # img size configure
    first_row, first_col = 10, 10
    row, col = 20, 20
    # make background img
    value_img = np.zeros((height * row + first_row * 2, width * col + first_col * 2, 3), np.uint8)
    # make pixel size
    color_pixel = np.zeros((row, col, 3), np.uint8)
    # text size configure
    text_scale = 0.3
    # make img
    text_size = text_scale * 20
    vertical_center = int((text_size + row)/2)
    horizontal_center = int((col - text_size * 3)/2)
    for i in range(width):
        for j in range(height):
            pixel_value = img[j, i]
            color_pixel = np.where(color_pixel >= 0, pixel_value, 0)
            value_img[first_row+row*j:first_row+row*(j+1), first_col+col*i:first_col+col*(i+1)] = color_pixel
            if pixel_value < 128:
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            value_img = cv.putText(value_img, str(img[j, i]),
                                   (first_col+col*i+horizontal_center, first_row+row*j + vertical_center),
                                   cv.FONT_HERSHEY_COMPLEX, text_scale, color, 1)

    i, j = 0, 0
    while i <= width:
        value_img = cv.line(value_img, (first_col + col * i, first_row),
                            (first_col + col * i, first_row + row * height), (255, 255, 255))
        i += 1
    while j <= height:
        value_img = cv.line(value_img, (first_col, first_row + row * j),
                            (first_col + col * width, first_row + row * j), (255, 255, 255))
        j += 1
    return value_img


# color object extract use hough circle
"""
def color_object_extract(img):
    # red ball extract
    color_img = img.copy()
    center = None
    hsv_img = cv.cvtColor(color_img, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_img)
    h_cut = cut_value(h, 160, 180)
    v_cut = cut_value(v, 50, 255)

    result_img = cv.bitwise_and(v, v, mask=h_cut)
    # result_img = cv.bitwise_and(result_img, result_img, mask=v_cut)
    # gray_img = cv.cvtColor(result_img, cv.COLOR_BGR2GRAY)
    cv.imshow('gray', result_img)

    # adaptive histogram equalization
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    hist_img = clahe.apply(result_img)
    # bilateral filtering
    # hist_img = cv.bilateralFilter(hist_img, 9, 75, 75)
    cv.imshow('hist', hist_img)

    # extract circles
    circles = cv.HoughCircles(hist_img, cv.HOUGH_GRADIENT, 1, 20,
                              param1=50, param2=50, minRadius=0, maxRadius=200)
    if circles is None:
        print('Not detected circles')
        return -1
    circles = np.uint16(np.around(circles))

    # draw circles
    circle_img = img.copy()
    if len(circles[0]) > 1:
        print('another ball in frame')
    for c in circles[0, :]:
        center = (c[0], c[1])
        radius = c[2]
        cv.circle(circle_img, center, radius, (0, 255, 255), 2)
    cv.imshow('all circles', circle_img)
    return center
"""


def color_object_extract(img, show=0, area=0):
    make_img = img.copy()
    gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
    hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_img)

    h_mask = cv.inRange(h, 165, 180)

    # s = cv.equalizeHist(s)
    # v = cv.equalizeHist(v)

    # sv = np.where(s >= 0, np.uint8(s / 2 + v / 2), 0)
    # sv_mask = cv.inRange(sv, 140, 255)
    sv_mask = cv.inRange(s, 140, 255)

    # erode dilate img
    """
    kernel = np.ones((7, 7), np.uint8)
    h_mask = cv.erode(h_mask, kernel, iterations=1)
    h_mask = cv.dilate(h_mask, kernel, iterations=1)
    sv_mask = cv.erode(sv_mask, kernel, iterations=1)
    sv_mask = cv.dilate(sv_mask, kernel, iterations=1)
    """

    value_mask = cv.bitwise_and(gray_img, gray_img, mask=h_mask)
    value_mask = cv.bitwise_and(value_mask, value_mask, mask=sv_mask)

    contours, hierarchy = cv.findContours(value_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        o_area = cv.contourArea(contours[0])
        num = 0
        for n, c in enumerate(contours):
            temp_area = cv.contourArea(c)
            if o_area < temp_area:
                o_area = temp_area
                num = n
        contour = contours[num]
        if area:
            return cv.contourArea(contour)
        mmt = cv.moments(contour)

        cx = int(mmt['m10'] / mmt['m00'])
        cy = int(mmt['m01'] / mmt['m00'])
        center = (cx, cy)
        result = center
        cv.circle(make_img, center, 2, (0, 255, 255), 2)
        cv.drawContours(make_img, contours, num, (255, 255, 0), 3)
        if show:
            result = result, make_img
            return result
        return result
    else:
        print('Not find contour')
        return -1


def now_time(string=''):
    now = datetime.now()
    time = now.isoformat(sep=' ')
    string = str(string)
    str_time = string + time
    print(str_time)
    return


def pixel_to_angle(center):
    h_angle = 57.26
    img_width = 640
    img_height = 480
    pixel = center[0]
    left = False
    if pixel > img_width / 2:
        pixel = pixel - img_width / 2
    else:
        left = True
        pixel = img_width / 2 - pixel
    angle = h_angle / img_width * pixel
    return angle, left


def degree_line(img):
    x = 640 / 62.2 * 1
    x0 = 320
    n = 0
    x1 = 320
    while x1 < 640:
        x1 = int(x0 + x * n)
        x2 = int(x0 - x * n)
        if n % 10 is 0:
            cv.line(img, (x1, 0), (x1, 480), (0, 0, 255))
            cv.line(img, (x2, 0), (x2, 480), (0, 0, 255))
        elif n % 10 is 5:
            cv.line(img, (x1, 0), (x1, 480), (255, 0, 0))
            cv.line(img, (x2, 0), (x2, 480), (255, 0, 0))
        else:
            cv.line(img, (x1, 0), (x1, 480), (255, 0, 255))
            cv.line(img, (x2, 0), (x2, 480), (255, 0, 255))
        n += 1
    cv.imshow('ex', img)
