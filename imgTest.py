
import cv2 as cv
import numpy as np
import m_vision as mv
import glob

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
on_track_bar = False
img_count = 0
ex_circle_img = None
trackWindow = None


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

termination = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

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
    elif k == ord('q'):
        make_img = img.copy()
        cut_img = mv.img_filter(make_img)
    elif k == ord('s'):
        # extract circles in img
        make_img = img.copy()
        cut_img = mv.img_filter(make_img)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=70, param2=50, minRadius=0, maxRadius=0)
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        ex_circle_pos = [1, (0, 0), 0]
        for c in circles[0, :]:
            mask = np.ones((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 0, -1)
            extract_img = np.ma.array(cut_img, mask=mask)
            std = np.std(extract_img)

            if std < ex_circle_pos[0]:
                ex_circle_pos = [std, center, radius]
            cv.circle(circle_img, center, radius, (0, 255, 255), 2)

        if ex_circle_pos[0] is not 1:
            st_point = tuple([i - ex_circle_pos[2] for i in ex_circle_pos[1]])
            ed_point = tuple([i + ex_circle_pos[2] for i in ex_circle_pos[1]])
            trackWindow = (st_point[0], st_point[1],
                           ed_point[0] - st_point[0],
                           ed_point[1] - st_point[1])
            ex_circle_img = img[st_point[1]:ed_point[1], st_point[0]:ed_point[0]]
            cv.imshow('rect', ex_circle_img)

            # ex_circle_img = cv.cvtColor(ex_circle_img, cv.COLOR_BGR2HSV)
            # ex_circle_img = cv.calcHist([ex_circle_img], [0, 1], None, [180, 256], [0, 180, 0, 256])
            # cv.normalize(ex_circle_img, ex_circle_img, 0, 255, cv.NORM_MINMAX)

            """
            # extract circle img
            circle_mask = np.zeros((img_width, img_height), dtype=np.uint8)
            circle_mask = cv.circle(circle_mask, ex_circle_pos[1], ex_circle_pos[2]-5, 255, -1)
            ex_circle_img = cv.bitwise_and(img, img, mask=circle_mask)
            cv.imshow('ex_circle_img', ex_circle_img)
            # extract circle img hsv value
            ex_cut_img = np.zeros((img_width, img_height, 3), dtype=np.uint8)
            hsv_circle_img = cv.cvtColor(ex_circle_img, cv.COLOR_BGR2HSV)
            hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
            a, b = mv.min_max_value(hsv_circle_img[:, :, 0])
            ex_cut_img[:, :, 0] = mv.cut_value(hsv_img[:, :, 0], a, b)
            a, b = mv.min_max_value(hsv_circle_img[:, :, 1])
            ex_cut_img[:, :, 1] = mv.cut_value(hsv_img[:, :, 1], a, b)
            a, b = mv.min_max_value(hsv_circle_img[:, :, 2])
            ex_cut_img[:, :, 2] = mv.cut_value(hsv_img[:, :, 2], a, b)
            ex_cut_img = cv.cvtColor(ex_cut_img, cv.COLOR_HSV2BGR)
            cv.imshow('ex_cut_img', ex_cut_img)
            """

        cv.imshow('all circles', circle_img)
    elif k == ord('c'):
        # trace rect
        if ex_circle_img is not None:
            hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
            dst = cv.calcBackProject([hsv], [0, 1], ex_circle_img, [0, 180, 0, 255], 1)
            cv.imshow('dst', dst)
            ret, trackWindow = cv.meanShift(dst, trackWindow, termination)
            x, y, w, h = trackWindow
            cv.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
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
        cv.destroyAllWindows()

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
        elif k == ord('3'):
            # yuv track bar
            mv.yuv_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
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
