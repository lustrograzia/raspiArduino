
import cv2 as cv
import m_vision as mv
import serial

ex_circles = False
lx, ly, px, py = 0, 0, 0, 0
on_mouse = 0
serial_communicate = False


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
    elif k == ord('k'):
        # move robotic arm
        serial_communicate = not serial_communicate
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
        # extract red circle
        _ = mv.color_object_extract(make_img)
    if serial_communicate:
        ard = serial.Serial('/dev/ttyACM0', 9600)
        text = raw_input('input: ')
        if text == 'exit':
            serial_communicate = False
            continue
        ard.write(text.encode())

    cv.imshow('origin', img)

cv.destroyAllWindows()


