import cv2 as cv
from cv2 import VideoCapture
import numpy as np
import imutils


def cap_video():
    try:
        cap = cv.VideoCapture(1)
        print(f'this is {cap}')
        # cap = cv.VideoCapture('v_1.mp4')
        frame_width, frame_height, fps = (
            int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
            int(cap.get(cv.CAP_PROP_FPS))
        )
        print(frame_height, frame_width)

    except Exception as e:
        print(e)
    return cap


def show_video(cap):

    # Create background
    backSub = cv.createBackgroundSubtractorMOG2()

    if not cap.isOpened():
        print('camera not loaded')
        exit()
    while True:
        # Capture frame by frame
        ret, frame = cap.read()

        frame = imutils.resize(frame, width=720)

        if not ret:
            print('Can`t find rate, Stream exiting...')
            break

        # Color filters for frame
        # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        fgMask = backSub.apply(frame)
        contours, hierarchy = cv.findContours(
            fgMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        # cv.rectangle(frame, (10, 2), (100, 20), (255, 255, 255), -1)

        # Draw contours

        for cnt in contours:
            rect = cv.minAreaRect(cnt)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            area = int(rect[1][0]*rect[1][1])

            if area > 500:
                cv.drawContours(frame, [box], 0, (0, 0, 255), 3, 1)

        cv.imshow('Frame', frame)
        # cv.imshow('FG Mask', fgMask)
        # cv.imshow('frame', gray)
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    show_video(cap_video())
