import cv2


CV_MAJOR_VERSION = int(cv2.__version__.split('.')[0])
if CV_MAJOR_VERSION < 3:
    # Create aliases to make OpenCV 2.x code forward-compatible.
    cv2.LINE_AA = cv2.CV_AA
    cv2.CAP_PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
    cv2.CAP_PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
    cv2.FILLED = cv2.cv.CV_FILLED
