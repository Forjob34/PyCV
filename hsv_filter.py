from __future__ import print_function
import cv2 as cv
import argparse
import imutils
import numpy as np
from imutils import contours
from scipy.spatial import distance as dist

max_value = 255
max_value_H = 360//2
low_H = 0
low_S = 0
low_V = 195
high_H = max_value_H
high_S = max_value
high_V = max_value
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'


def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H-1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)


def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H+1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)


def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S-1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)


def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S+1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)


def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V-1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)


def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V+1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)


parser = argparse.ArgumentParser(
    description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument(
    '--camera', help='Camera divide number.', default=0, type=int)
parser.add_argument(
    '-w', '--width', type=float, help='Pls, input defualt size of object'
)

args = parser.parse_args()
# cap = cv.VideoCapture(args.camera)
cap = cv.VideoCapture('./src/vid_16.mp4')
frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
print('Frame count:', frame_count)
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)

cv.createTrackbar(low_H_name, window_detection_name, low_H,
                  max_value_H, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name, high_H,
                  max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name, low_S,
                  max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name, high_S,
                  max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name, low_V,
                  max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name, high_V,
                  max_value, on_high_V_thresh_trackbar)

frame_width, frame_height = (
    int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
    int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
)
fps = int(cap.get(cv.CAP_PROP_FPS))

#  Codec for video
fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
out = cv.VideoWriter('output.mp4', -1, fps,
                     (frame_width, frame_height))

while True:

    ret, frame = cap.read()
    frame = imutils.resize(frame, height=720)

    if frame is None:
        break

    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(
        frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))

    frame_contours, hierarchy = cv.findContours(
        frame_threshold.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    try:
        (frame_contours, _) = contours.sort_contours(frame_contours)
        pixelsPerMetric = None
    except Exception as e:
        e

    for cnt in frame_contours:
        if cv.contourArea(cnt) < 100:
            continue

        rect = cv.minAreaRect(cnt)
        # print(rect)
        box = cv.boxPoints(
            rect) if imutils.is_cv2() else cv.boxPoints(rect)
        box = np.int0(box)
        area = int(rect[1][0]*rect[1][1])
        # print(area)

        if area > 200000:
            # print(area)
            cv.drawContours(frame, [box], 0, (0, 0, 0), 3, 0)
        # Alt draw

        # box = np.array(box, dtype="int")

        # box = perspective.order_points(box)
        # cv.drawContours(frame, [box.astype('int')], -1, (0, 255, 0), 2)

        # loop over the original points and draw them
            for (x, y) in box:
                cv.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)

            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)

            # compute the midpoint between the top-left and top-right points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)

            # draw the midpoints on the image
            cv.circle(frame, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv.circle(frame, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
            cv.circle(frame, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
            cv.circle(frame, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

            # draw lines between the midpoints
            cv.line(frame, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                    (0, 0, 0), 2)
            cv.line(frame, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                    (0, 0, 0), 2)

            # compute the Euclidean distance between the midpoints
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

            # if the pixels per metric has not been initialized, then
            # compute it as the ratio of pixels to supplied metric
            # (in this case, inches)
            if pixelsPerMetric is None:
                pixelsPerMetric = dB
                pixelsPerMetric = dA

            # compute the size of the object
            dimA = dA
            dimB = dB

            # draw the object sizes on the image
            cv.putText(frame, "{:.1f}cm".format(dimA / 3.0),
                       (int(tltrX), int(tltrY + 50)), cv.FONT_HERSHEY_SIMPLEX,
                       0.65, (0, 0, 0), 2)
            # print(dimA)
            cv.putText(frame, "{:.1f}cm".format(dimB / 3.0),
                       (int(trbrX - 50), int(trbrY)), cv.FONT_HERSHEY_SIMPLEX,
                       0.65, (0, 0, 0), 2)

            height = dimA / 13.0
            lenght = dimB / 13.0

    cv.imshow(window_capture_name, frame)
    # out.write(frame)
    cv.imshow(window_detection_name, frame_threshold)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break

cap.release()
out.release()
cv.destroyAllWindows()
