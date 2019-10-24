
import cv2 as cv
import numpy as np
import m_vision as mv

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0


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


cap = cv.VideoCapture(-1)
_, frame = cap.read()

img_width = frame.shape[0]
img_height = frame.shape[1]

while True:
    # read cam frame
    _, frame = cap.read()
    img = frame.copy()

    # mouse callback
    cv.setMouseCallback('origin', on_mouse_event)

    # draw rectangle
    if on_mouse == 2 or on_mouse == 3:
        cv.rectangle(img, (lx, ly), (px, py), (255, 0, 0), 3)

    # keyboard input value
    k = cv.waitKey(10)
    if k == 27:
        break
    elif k == ord('s'):
        # extract circles in img
        ex_circles = not ex_circles
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
    if ex_circles:
        make_img = img.copy()
        cut_img = mv.img_filter(make_img)

        # extract circles
        circles = cv.HoughCircles(cut_img, cv.HOUGH_GRADIENT, 1, 30,
                                  param1=50, param2=50, minRadius=0, maxRadius=0)
        if circles is None:
            continue
        circles = np.uint16(np.around(circles))

        # draw circles
        circle_img = img.copy()
        for c in circles[0, :]:
            mask = np.zeros((img_width, img_height), dtype=np.uint8)
            center = (c[0], c[1])
            radius = c[2]

            cv.circle(mask, center, radius, 255, -1)
            std_img = cv.bitwise_and(cut_img, cut_img, mask=mask)
            mask = np.where(mask == 255, 0, 1)
            extract_img = np.ma.array(std_img, mask=mask)
            std = np.std(extract_img)
            if std < 30:
                cv.circle(circle_img, center, radius, (0, 255, 255), 2)
                print(std)
            cv.circle(img, center, radius, (0, 255, 255), 2)
        cv.imshow('circle', circle_img)

    cv.imshow('origin', img)

cv.destroyAllWindows()

