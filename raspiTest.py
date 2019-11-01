
import cv2 as cv
import numpy as np
import m_vision as mv

ex_circles = False
ex_circle_img = None
trackWindow = None


cap = cv.VideoCapture(-1)
_, frame = cap.read()

img_width = frame.shape[0]
img_height = frame.shape[1]

while True:
    # read cam frame
    _, frame = cap.read()
    img = frame.copy()

    # keyboard input value
    k = cv.waitKey(10)
    if k == 27:
        break
    elif k == ord('s'):
        # extract circles in img
        make_img = img.copy()
        cut_img = mv.img_filter(make_img)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=50, param2=50, minRadius=0, maxRadius=0)
        if circles is None:
            continue
        circles = np.uint16(np.around(circles))

        # extract best circle
        circle_img = img.copy()
        best_circle = [100, (0, 0), 0]
        for c in circles[0, :]:
            mask = np.ones((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]
            # extract circle img
            cv.circle(mask, center, radius, 0, -1)
            extract_img = np.ma.array(cut_img, mask=mask)
            # calculate circle standard deviation
            std = np.std(extract_img)
            # find white circle
            if std < best_circle[0]:
                best_circle = [std, center, radius]
            cv.circle(circle_img, center, radius, (0, 255, 255), 2)

        if best_circle[0] is not 100:
            cv.circle(img, best_circle[1], 2, (255, 0, 0), 2)

        cv.imshow('all circles', circle_img)
    elif k == ord('w'):
        # write img file
        cv.imwrite('circles_img.jpg', img)
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
    cv.imshow('origin', img)

cv.destroyAllWindows()
