
import cv2 as cv
import numpy as np
import m_vision as mv
import glob

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
# press 't' show track bar
on_track_bar = False
# press 'n' change img
img_count = 0
ex_circle_img = None
trackWindow = None
circle_center = None


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
img_width = o_img.shape[1]
img_height = o_img.shape[0]

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
        # clahe histogram equalization
        make_img = img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        # adaptive histogram equalization
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hist_img = clahe.apply(gray_img)
        # bilateral filtering
        hist_img = cv.bilateralFilter(hist_img, 9, 75, 75)
        cut_img = hist_img
        cv.imshow('hist_img', hist_img)

        param_value = 200
        while True:
            circle_img = make_img.copy()
            circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                      param1=100, param2=param_value, minRadius=0, maxRadius=100)
            if circles is None:
                print(param_value, 'circle is None')
                param_value -= 1
                continue
            else:
                circles = np.uint16(np.around(circles))
                print(param_value, 'circle:', len(circles[0]))
                for c in circles[0, :]:
                    center = (c[0], c[1])
                    radius = c[2]
                    cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                cv.imshow('circles', circle_img)
                cv.waitKey()
            param_value -= 1
            if param_value < 50:
                break
    elif k == ord('q'):
        # 주위 pixel 값과 중앙 pixel 값의 차이가 일정 값 이상인 pixel 추출
        make_img = o_img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        cv.imshow('gray', gray_img)
        # adaptive histogram equalization
        """
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hist_img = clahe.apply(gray_img)
        cv.imshow('hist', hist_img)
        """
        # bilateral filtering
        """
        hist_img = cv.bilateralFilter(hist_img, 9, 75, 75)
        """
        # canny
        """
        edge1 = cv.Canny(hist_img, 30, 100)
        edge2 = cv.Canny(hist_img, 50, 100)
        cv.imshow('edge1', edge1)
        cv.imshow('edge2', edge2)
        """
        # compare to around pixel
        value_img = np.zeros((img_height, img_width), dtype=np.uint8)
        for i in range(1, img_width - 1):
            for j in range(1, img_height - 1):
                img_values = [gray_img[j, i - 1], gray_img[j + 1, i], gray_img[j, i + 1], gray_img[j - 1, i],
                              gray_img[j - 1, i - 1], gray_img[j - 1, i + 1], gray_img[j + 1, i + 1],
                              gray_img[j + 1, i - 1]]
                for v in img_values:
                    if gray_img[j, i] > v:
                        compare_value = gray_img[j, i] - v
                    else:
                        compare_value = v - gray_img[j, i]
                    if compare_value > 10:
                        value_img[j, i] = 255
                        break
        cv.imshow('value', value_img)
        # erode dilate img
        kernel = np.ones((3, 3), np.uint8)
        cut_img = cv.erode(value_img, kernel, iterations=1)
        cut_img = cv.dilate(cut_img, kernel, iterations=1)
        cv.imshow('erode', cut_img)
        # contour area
        contour_img = np.zeros((img_height, img_width, 3), np.uint8)
        contours, hierarchy = cv.findContours(cut_img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cv.drawContours(contour_img, [cnt], 0, (0, 0, 255), 1)
            x, y, w, h = cv.boundingRect(cnt)
            area = cv.contourArea(cnt)
            if area > 100:
                cv.rectangle(contour_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv.imshow('contour_img', contour_img)

        """
        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=50, param2=50, minRadius=20, maxRadius=200)
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = o_img.copy()
        for c in circles[0, :]:
            center = (c[0], c[1])
            radius = c[2]
            cv.circle(circle_img, center, radius, (0, 255, 255), 2)
        cv.imshow('circles', circle_img)
        """
    elif k == ord('o'):
        # test field
        make_img = o_img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
        h, s, v = cv.split(hsv_img)

        h_mask = cv.inRange(h, 165, 180)

        sv = np.where(s >= 0, np.uint8(s/2 + v/2), 0)
        sv_mask = cv.inRange(sv, 140, 255)

        # erode dilate img
        kernel = np.ones((7, 7), np.uint8)
        h_mask = cv.erode(h_mask, kernel, iterations=1)
        h_mask = cv.dilate(h_mask, kernel, iterations=1)
        sv_mask = cv.erode(sv_mask, kernel, iterations=1)
        sv_mask = cv.dilate(sv_mask, kernel, iterations=1)

        value_mask = cv.bitwise_and(gray_img, gray_img, mask=h_mask)
        value_mask = cv.bitwise_and(value_mask, value_mask, mask=sv_mask)
        """
        contours, hierarchy = cv.findContours(value_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contour = contours[0]
        mmt = cv.moments(contour)
        cx = int(mmt['m10'] / mmt['m00'])
        cy = int(mmt['m01'] / mmt['m00'])
        cv.circle(make_img, (cx, cy), 3, (255, 0, 255))
        cv.drawContours(make_img, contours, 0, (255, 255, 0), 3)
        cv.imshow('make', make_img)
        """

        # cv.imshow('h', h)
        # cv.imshow('s', s)
        # cv.imshow('v', v)
        cv.imshow('h_mask', h_mask)
        cv.imshow('sv_mask', sv_mask)
        cv.imshow('sv', sv)
        cv.imshow('value_img', value_mask)
    elif k == ord('s'):
        # extract circles in img
        make_img = o_img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
        h, s, v = cv.split(hsv_img)



        sv = np.where(s >= 0, np.uint8(s / 2 + v / 2), 0)
        value_img = np.where(h >= 0, np.uint8(h / 2 + sv / 2), 0)
        value_mask = cv.inRange(value_img, 150, 255)

        # erode dilate img
        kernel = np.ones((5, 5), np.uint8)
        # cut_img = cv.erode(value_img, kernel, iterations=1)
        value_mask = cv.dilate(value_mask, kernel, iterations=2)

        value_img = cv.bitwise_and(v, v, mask=value_mask)
        cv.imshow('cut_value', value_img)

        # extract circles
        circles = cv.HoughCircles(value_img, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=50, param2=50, minRadius=0, maxRadius=200)
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        ex_circle_pos = [1, (0, 0), 0]
        for c in circles[0, :]:
            center = (c[0], c[1])
            radius = c[2]
            cv.circle(circle_img, center, radius, (0, 255, 255), 2)
        cv.imshow('all circles', circle_img)
    elif k == ord('c'):
        # gray img color value table
        if lx > px:
            lx, px = px, lx
        if ly > py:
            ly, py = py, ly
        if lx == px or ly == py:
            print('Not drag rectangle')
        else:
            color_img = o_img.copy()
            rec_img = color_img[ly:py, lx:px]
            gray_img = cv.cvtColor(rec_img, cv.COLOR_BGR2GRAY)
            gray_table = mv.print_img_value(gray_img)
            cv.imshow('gray_table', gray_table)

            hsv_cut_img = cv.cvtColor(rec_img, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_cut_img)
            # s = cv.bitwise_not(s)
            h_table = mv.print_img_value(h)
            s_table = mv.print_img_value(s)
            v_table = mv.print_img_value(v)
            cv.imshow('h_table', h_table)
            cv.imshow('s_table', s_table)
            cv.imshow('v_table', v_table)

            sv = np.where(s >= 0, np.uint8(s/2 + v/2), 0)

            a_table = mv.print_img_value(sv)
            cv.imshow('a_table', a_table)
    elif k == ord('n'):
        # change image
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
    elif k == ord('b'):
        # 밝기 범위를 분할해서 원 추출
        s_img = o_img.copy()
        gray_img = cv.cvtColor(s_img, cv.COLOR_BGR2GRAY)
        # adaptive histogram equalization
        """
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hist_img = clahe.apply(gray_img)
        cv.imshow('hist_img', hist_img)
        """
        # bilateral filtering
        blur_img = cv.bilateralFilter(gray_img, 9, 75, 75)
        cv.imshow('blur_img', blur_img)

        # 0 ~ 255 value
        c_value = 245
        while c_value > 0:
            print('c_value:', c_value)
            # value area extractw
            cut_img = cv.inRange(blur_img, c_value, c_value + 10)
            # extract contour
            contour_img = cv.cvtColor(cut_img, cv.COLOR_GRAY2BGR)
            contours, hierarchy = cv.findContours(cut_img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cv.drawContours(contour_img, [cnt], 0, (0, 0, 255), 1)
                x, y, w, h = cv.boundingRect(cnt)
                area = cv.contourArea(cnt)
                if area > 100:
                    cv.rectangle(contour_img, (x, y), (x + w, y + h), (0, 255, 0), 1)

            c_value -= 5
            cv.imshow('cut_img', cut_img)
            cv.imshow('contour_img', contour_img)
            cv.waitKey()
        cv.destroyWindow('cut_img')
        cv.destroyWindow('contour_img')
    # bgr color value 편차 10 이내 값 추출
    elif k == ord('u'):
        color_img = o_img.copy()
        mask_img = np.zeros((img_height, img_width), np.uint8)
        # std < 5 pixel 255
        for i in range(img_width):
            for j in range(img_height):
                color_value = color_img[j, i]
                if np.std(color_value) < 5:
                    mask_img[j, i] = 255
        cv.imshow('mask_img', mask_img)
        # erode mask_img
        kernel = np.ones((3, 3), np.uint8)
        mask_img = cv.erode(mask_img, kernel, iterations=1)
        cv.imshow('erode_mask_img', mask_img)
        # color_img masked mask_img
        extract_img = cv.bitwise_and(color_img, color_img, mask=mask_img)
        cv.imshow('extract_img', extract_img)
        # gray img to 0 less than 100
        gray_img = cv.cvtColor(extract_img, cv.COLOR_BGR2GRAY)
        gray_mask = cv.inRange(gray_img, 100, 255)
        result_img = cv.bitwise_and(extract_img, extract_img, mask=gray_mask)
        cv.imshow('result_img', result_img)
    # std value
    elif k == ord('y'):
        make_img = o_img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
        h, s, v = cv.split(hsv_img)
        x_img = np.zeros((img_height, img_width), np.uint8)
        kernel = np.zeros((3, 3), np.uint8)
        for i in range(img_width - 2):
            for j in range(img_height - 2):
                kernel = h[j:j + 2, i:i + 2]
                std = np.std(kernel)
                if std > 7:
                    x_img[j + 1, i + 1] = 255
        cv.imshow('x_img', x_img)
    # red circle extract
    elif k == ord('k'):
        result = mv.color_object_extract(o_img)
        if result != -1:
            print(result)

    # loop
    if on_track_bar is True:
        # get track bar pos
        low_a, high_a, low_b, high_b, low_c, high_c = mv.get_track_bar_pos('origin')

        # rgb track bar
        if k == ord('1'):
            mv.rgb_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        # hsv track bar
        elif k == ord('2'):
            mv.hsv_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        # yuv track bar
        elif k == ord('3'):
            mv.yuv_track_bar(img, low_a, high_a, low_b, high_b, low_c, high_c)
        # gray track bar use one
        elif k == ord('4'):
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            one_t = low_a
            if one_t >= 255 - 10:
                one_t = 255 - 10
            cut_gray_img = mv.cut_value(gray_img, one_t, one_t + 10)
            cv.imshow('cut_gray', cut_gray_img)
        # image divide into value
        elif k == ord('5'):
            divide_value = 5
            # track bar value
            low_a, high_a = mv.overlap_block(low_a, high_a)
            low_a = low_a - low_a % divide_value
            high_a = high_a - high_a % divide_value
            low_b, high_b = mv.overlap_block(low_b, high_b)
            low_b = low_b - low_b % divide_value
            high_b = high_b - high_b % divide_value
            low_c, high_c = mv.overlap_block(low_c, high_c)
            low_c = low_c - low_c % divide_value
            high_c = high_c - high_c % divide_value
            # h value(hsv) table part
            color_table = mv.create_color_table()
            hsv_color_table = cv.cvtColor(color_table, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_color_table)
            h = np.where(h > 0, h - h % divide_value, h)
            color_table_mask = np.where(h <= high_a, h, -1)
            color_table_mask = np.uint8(np.where(color_table_mask >= low_a, 255, 0))
            color_table = cv.merge((h, s, v))
            color_table = cv.cvtColor(color_table, cv.COLOR_HSV2BGR)
            color_table = cv.bitwise_and(color_table, color_table, mask=color_table_mask)
            cv.imshow('color_table', color_table)
            # image hsv part
            make_img = img.copy()
            hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_img)

            h_part = np.where(h > 0, h - h % divide_value, h)
            s_part = np.where(s > 0, s - s % divide_value, s)
            v_part = np.where(v > 0, v - v % divide_value, v)

            h_mask = np.where(h_part <= high_a, h_part, -1)
            h_mask = np.uint8(np.where(h_mask >= low_a, 255, 0))
            s_mask = np.where(s_part <= high_b, s_part, -1)
            s_mask = np.uint8(np.where(s_mask >= low_b, 255, 0))
            v_mask = np.where(v_part <= high_c, v_part, -1)
            v_mask = np.uint8(np.where(v_mask >= low_c, 255, 0))

            h_img = cv.merge((h_part, s, v))
            h_img = cv.cvtColor(h_img, cv.COLOR_HSV2BGR)
            h_img = cv.bitwise_and(h_img, h_img, mask=h_mask)
            cv.imshow('h_img', h_img)

            s_img = cv.merge((h, s_part, v))
            s_img = cv.cvtColor(s_img, cv.COLOR_HSV2BGR)
            s_img = cv.bitwise_and(s_img, s_img, mask=s_mask)
            cv.imshow('s_img', s_img)

            v_img = cv.merge((h, s, v_part))
            v_img = cv.cvtColor(v_img, cv.COLOR_HSV2BGR)
            v_img = cv.bitwise_and(v_img, v_img, mask=v_mask)
            cv.imshow('v_img', v_img)
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