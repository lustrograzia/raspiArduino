
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
    elif k == ord('p'):
        make_img = img.copy()
        simplify_img = mv.simplify_color(make_img)
        cut_img = cv.cvtColor(simplify_img, cv.COLOR_BGR2GRAY)

        value1 = 200
        while True:
            last_circle = None
            center = None
            circle_img = make_img.copy()
            circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                      param1=value1, param2=50, minRadius=20, maxRadius=200)
            if circles is None:
                print(value1, 'circle is None')
                value1 -= 1
                continue
            else:
                print(value1, 'circle:', len(circles[0]))
                for c in circles[0, :]:
                    center = (c[0], c[1])
                    radius = c[2]
                    cv.circle(cut_img, center, radius, (0, 0, 0), -1)
                    cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                cv.imshow('circles', circle_img)
                cv.imshow('cut_img', cut_img)
                cv.waitKey()
                print(last_circle, center)
                print(len(circles[0]))
                if last_circle == center:
                    value1 -= 1
                if len(circles[0]) == 1:
                    last_circle = center
                if value1 is 49:
                    break

    elif k == ord('q'):
        # extract circles in img
        make_img = img.copy()
        simplify_img = mv.simplify_color(make_img)
        cut_img = cv.cvtColor(simplify_img, cv.COLOR_BGR2GRAY)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=60, param2=50, minRadius=20, maxRadius=200)
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))
        """
        # draw circles
        circle_img = img.copy()
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
        """
        print(circles[0, 1])
        print(len(circles[0]))

        for i in range(200, 69, -1):
            circle_img = make_img.copy()
            circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                      param1=i, param2=50, minRadius=20, maxRadius=200)
            if circles is None:
                print(i, 'circle is None')
                continue
            else:
                print(i, 'circle:', len(circles[0]))
                for c in circles[0, :]:
                    center = (c[0], c[1])
                    radius = c[2]

                    cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                cv.imshow('circles', circle_img)
                cv.waitKey()

    elif k == ord('o'):
        a = [350, 470]
        b = [470, 350]
        c = [183.642, 142.428]
        print(int(a[0]/c[0]), int(a[1]/c[1]), int(a[0]/c[0])*int(a[1]/c[1]))
        print(int(b[0]/c[0]), int(b[1]/c[1]), int(b[0]/c[0])*int(b[1]/c[1]))
    elif k == ord('s'):
        # extract circles in img
        make_img = img.copy()
        simplify_img = mv.simplify_color(make_img)
        cut_img = mv.img_filter(simplify_img, show=True)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=70, param2=50, minRadius=20, maxRadius=200)
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
            st_point = [i - ex_circle_pos[2] for i in ex_circle_pos[1]]
            ed_point = tuple([i + ex_circle_pos[2] for i in ex_circle_pos[1]])
            if st_point[0] > 1000:
                st_point[0] = 0
            if st_point[1] > 1000:
                st_point[1] = 0
            st_point = tuple(st_point)
            trackWindow = (st_point[0], st_point[1],
                           ed_point[0] - st_point[0],
                           ed_point[1] - st_point[1])
            ex_circle_img = img[st_point[1]:ed_point[1], st_point[0]:ed_point[0]]
            print(trackWindow)
            cv.imshow('rect', ex_circle_img)
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
        elif k == ord('5'):
            # h value(hsv) divide 10 size
            low_a, high_a = mv.overlap_block(low_a, high_a)
            low_value = low_a - low_a % 10
            high_value = high_a - high_a % 10
            color_table = mv.create_color_table()
            hsv_color_table = cv.cvtColor(color_table, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_color_table)
            h = np.where(h > 0, h - h % 10, h)
            color_table_mask = np.where(h <= high_value, h, -1)
            color_table_mask = np.uint8(np.where(color_table_mask >= low_value, 255, 0))
            color_table = cv.merge((h, s, v))
            color_table = cv.cvtColor(color_table, cv.COLOR_HSV2BGR)
            color_table = cv.bitwise_and(color_table, color_table, mask=color_table_mask)
            cv.imshow('color_table', color_table)

            make_img = img.copy()
            hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_img)
            h = np.where(h > 0, h - h % 10, h)
            color_img_mask = np.where(h <= high_value, h, -1)
            color_img_mask = np.uint8(np.where(color_img_mask >= low_value, 255, 0))
            color_img = cv.merge((h, s, v))
            color_img = cv.cvtColor(color_img, cv.COLOR_HSV2BGR)
            color_img = cv.bitwise_and(color_img, color_img, mask=color_img_mask)
            cv.imshow('color_img', color_img)
        elif k == ord('6'):
            if low_a < 50:
                low_a = 50
            if high_a < 50:
                high_a = 50
            # extract circles in img
            make_img = img.copy()
            simplify_img = mv.simplify_color(make_img)
            cut_img = mv.img_filter(simplify_img, show=True)

            # extract circles
            circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                      param1=low_a, param2=high_a, minRadius=20, maxRadius=200)
            if circles is None:
                print('Not detected circles')
                continue
            circles = np.uint16(np.around(circles))

            # draw circles
            circle_img = img.copy()
            for c in circles[0, :]:
                center = (c[0], c[1])
                radius = c[2]
                cv.circle(circle_img, center, radius, (0, 255, 255), 2)
            cv.imshow('circles_img', circle_img)
    cv.imshow('origin', img)
cv.destroyAllWindows()
