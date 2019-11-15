
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
        make_img = img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        cv.imshow('gray', gray_img)
        # adaptive histogram equalization
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hist_img = clahe.apply(gray_img)
        cv.imshow('clahe', hist_img)
        # bilateral filtering
        hist_img = cv.bilateralFilter(hist_img, 9, 75, 75)
        cut_img = hist_img
        cv.imshow('bilateral', hist_img)
    elif k == ord('s'):
        # extract circles in img
        make_img = img.copy()
        gray_img = cv.cvtColor(make_img, cv.COLOR_BGR2GRAY)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hist_img = clahe.apply(gray_img)

        # extract circles
        circles = cv.HoughCircles(hist_img, cv.HOUGH_GRADIENT, 1, 20,
                                  param1=70, param2=60, minRadius=20, maxRadius=200)
        if circles is None:
            print('Not detected circles')
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        ex_circle_pos = [1, (0, 0), 0]
        for c in circles[0, :]:
            mask = np.ones((img_height, img_width), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 0, -1)
            extract_img = np.ma.array(hist_img, mask=mask)
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
            mv.print_img_value(gray_img)

            hsv_cut_img = cv.cvtColor(rec_img, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_cut_img)
            mv.print_img_value(h)
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
    elif k == ord('u'):
        # bgr color value 편차 10 이내 값 추출
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
    elif k == ord('k'):
        # 붉은 색 공 추출
        result = mv.color_object_extract(o_img)
        if result != -1:
            print(result)

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
            h_value = 5
            # h value(hsv) divide 10 size
            low_a, high_a = mv.overlap_block(low_a, high_a)
            low_value = low_a - low_a % h_value
            high_value = high_a - high_a % h_value
            color_table = mv.create_color_table()
            hsv_color_table = cv.cvtColor(color_table, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_color_table)
            h = np.where(h > 0, h - h % h_value, h)
            color_table_mask = np.where(h <= high_value, h, -1)
            color_table_mask = np.uint8(np.where(color_table_mask >= low_value, 255, 0))
            color_table = cv.merge((h, s, v))
            color_table = cv.cvtColor(color_table, cv.COLOR_HSV2BGR)
            color_table = cv.bitwise_and(color_table, color_table, mask=color_table_mask)
            cv.imshow('color_table', color_table)

            make_img = img.copy()
            hsv_img = cv.cvtColor(make_img, cv.COLOR_BGR2HSV)
            h, s, v = cv.split(hsv_img)
            h = np.where(h > 0, h - h % h_value, h)
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