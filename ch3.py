
# 메디안 플로우 객체 추적기
"""
import cv2
import numpy as np

cap = cv2.VideoCapture("D:/[doc]/video/BLACKPINK - 'Kill This Love' DANCE PRACTICE VIDEO (MOVING VER.).mp4")

cap.set(cv2.CAP_PROP_POS_FRAMES, 100)

_, frame = cap.read()

bbox = cv2.selectROI(frame, False, True)

cv2.destroyAllWindows()

tracker = cv2.TrackerMedianFlow_create()
status_tracker = tracker.init(frame, bbox)
fps = 0

while True:
    status_cap, frame = cap.read()
    if not status_cap:
        break

    if status_tracker:
        timer = cv2.getTickCount()
        status_tracker, bbox = tracker.update(frame)
    if status_tracker:
        x, y, w, h = [int(i) for i in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 15)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(frame, "FPS: %.0f" % fps, (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 0, 0), 8)
    else:
        cv2.putText(frame, "Tracking failure detected", (0, 80), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 0, 255), 8)
    cv2.imshow("Medianflow tracker", frame)

    k = cv2.waitKey(1)
    if k == 27:
        break
cv2.destroyAllWindows()
"""

# 추적 API의 다양한 알고리즘을 사용해 객체 추적
"""
import time
import cv2

cv2.namedWindow('frame')

for name, tracker in (('KCF', cv2.TrackerKCF_create), ('MIL', cv2.TrackerMIL_create), ('TLD', cv2.TrackerTLD_create)):
    tracker = tracker()
    initialized = False

video = cv2.VideoCapture("D:/[doc]/video/BLACKPINK - 'Kill This Love' DANCE PRACTICE VIDEO (MOVING VER.).mp4")
bbox = (878, 266, 1153-878, 475-266)

while True:
    t0 = time.time()
    ok, frame = video.read()
    if not ok:
        break
    if initialized:
        tracked, bbox = tracker.update(frame)
    else:
        cv2.imwrite('D:/[doc]/pic/frame.png', frame)
        tracked = tracker.init(frame, bbox)
        initialized = True

    fps = 1 / (time.time() - t0)
    cv2.putText(frame, 'tracker: {}, fps: {:.1f}'.format(name, fps), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    if tracked:
        bbox = tuple(map(int, bbox))
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 3)

    cv2.imshow('frame', frame)
    if cv2.waitKey(3) == 27:
        break

    cv2.destroyAllWindows()
"""