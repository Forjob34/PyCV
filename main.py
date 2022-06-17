from __future__ import print_function
import json
import cv2 as cv
import argparse
import imutils
import numpy as np
import asyncio
from imutils import contours
from scipy.spatial import distance as dist
from multiprocessing import Process


size_arr = []

radiators = {
    'radiator_type':
    {
        'type': '',
        'sizes': []
    },
}


def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def cap_video(path):

    parser = argparse.ArgumentParser(
        description='Code for Thresholding Operations using inRange tutorial.')
    parser.add_argument(
        '--camera', help='Camera divide number.', default=0, type=int)
    parser.add_argument(
        '-w', '--width', type=float, help='Pls, input defualt size of object'
    )

    args = parser.parse_args()

    try:
        cap = cv.VideoCapture(path)
        # cap = cv.VideoCapture(0)
        frame_width, frame_height, fps = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
            int(cap.get(cv.CAP_PROP_FPS))
        )
        print(frame_height, frame_width)

        frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        print('Frame count:', frame_count)
        cv.namedWindow("Video Capture")
        # cv.namedWindow("Test")

    except Exception as e:
        print(e)
    return cap


def draw_cont(frame_contours, frame, pixelsPerMetric):

    for cnt in frame_contours:
        if cv.contourArea(cnt) < 1000:
            continue

        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(
            rect) if imutils.is_cv2() else cv.boxPoints(rect)
        box = np.int0(box)
        area = int(rect[1][0]*rect[1][1])

        if area > 200000:

            # print(area)
            cv.drawContours(frame, [box], 0, (0, 0, 0), 3, 2)

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
            cv.circle(frame, (int(tltrX), int(tltrY)),
                      5, (255, 0, 0), -1)
            cv.circle(frame, (int(blbrX), int(blbrY)),
                      5, (255, 0, 0), -1)
            cv.circle(frame, (int(tlblX), int(tlblY)),
                      5, (255, 0, 0), -1)
            cv.circle(frame, (int(trbrX), int(trbrY)),
                      5, (255, 0, 0), -1)

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
            dimA = dA / 13.0
            dimB = dB / 13.0

            # draw the object sizes on the image
            cv.putText(frame, "{:.1f}cm".format(dimA),
                       (int(tltrX), int(tltrY + 50)
                        ), cv.FONT_HERSHEY_SIMPLEX,
                       0.65, (0, 0, 0), 2)

            cv.putText(frame, "{:.1f}cm".format(dimB),
                       (int(trbrX - 50), int(trbrY)
                        ), cv.FONT_HERSHEY_SIMPLEX,
                       0.65, (0, 0, 0), 2)

            try:
                height = float('{:.0f}'.format(dimA))
            except:
                height = None
                area = None
            try:
                lenght = float('{:.0f}'.format(dimB))
            except:
                lenght = None

            radiators['radiator_type']['sizes'] = {'height': height,
                                                   'lenght': lenght,
                                                   'area': area}
            radiators['radiator_type']['type'] = f"Тип 22х{int(height * 10)}x{int(lenght * 10)}"

    return radiators


def json_handler(data=radiators):
    for i in data:
        pass


def write_json(data=radiators):
    try:
        with open('sizes.json', 'w', encoding='UTF-8') as file:
            json.dump(radiators, file, indent=4, ensure_ascii=False)
    except Exception as err:
        err


async def show_video(cap):
    hsv_min = np.array((0, 0, 150), np.uint8)
    hsv_max = np.array((255, 255, 255), np.uint8)
    # Create background
    # backSub = cv.createBackgroundSubtractorMOG2()

    if not cap.isOpened():
        print('camera not loaded')
        exit()

    while True:

        ret, frame = cap.read()
        frame = imutils.resize(frame, height=720)

        if frame is None:
            break

        # ++++++++++++ Find conours with HSV_filter ++++++++++++++

        # frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # thresh = cv.inRange(frame_hsv, hsv_min, hsv_max)

        # ++++++++++++ Find conours with Canny ++++++++++++++

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (11, 11), 0)
        edges = cv.Canny(gray, 10, 200)

        frame_contours, hierarchy = cv.findContours(
            edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        try:
            (frame_contours, _) = contours.sort_contours(frame_contours)
            pixelsPerMetric = None
        except Exception as e:
            e

        data = draw_cont(frame_contours, frame, pixelsPerMetric)
        write_data = write_json(data)

        cv.imshow('Video Capture', frame)
        # cv.imshow('Test', edges)

        key = cv.waitKey(30)
        if key == ord('q') or key == 27:
            break

    return size_arr


def get_csv():
    pass


if __name__ == '__main__':
    # Process(target=show_video(cap_video('./src/vid_6.mp4'))).start()
    # Process(target=get_csv()).start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(show_video(cap_video('./src/vid_6.mp4')))
