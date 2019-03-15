import numpy
import sklearn.cluster
from CVBackwardCompat import cv2

import ColorUtils
import ResizeUtils


ROTATION_0 = 0
ROTATION_CCW_90 = 1
ROTATION_180 = 2
ROTATION_CCW_270 = 3

DIRECTION_UP = 0
DIRECTION_LEFT = 1
DIRECTION_DOWN = 2
DIRECTION_RIGHT = 3

SQUARE_STATUS_UNKNOWN = -1
SQUARE_STATUS_EMPTY = 0
SQUARE_STATUS_PAWN_PLAYER_1 = 1
SQUARE_STATUS_KING_PLAYER_1 = 11
SQUARE_STATUS_PAWN_PLAYER_2 = 2
SQUARE_STATUS_KING_PLAYER_2 = 22


class CheckersModel(object):


    @property
    def sceneSize(self):
        return self._sceneSize


    @property
    def scene(self):
        return self._scene


    @property
    def sceneGray(self):
        return self._sceneGray


    @property
    def boardSize(self):
        return self._boardSize


    @property
    def board(self):
        return self._board


    @property
    def squareStatuses(self):
        return self._squareStatuses


    @property
    def boardRotation(self):
        return self._boardRotation


    @boardRotation.setter
    def boardRotation(self, value):
        self._boardRotation = value % 4


    @property
    def shadowDirection(self):
        return self._shadowDirection


    @shadowDirection.setter
    def shadowDirection(self, value):
        self._shadowDirection = value % 4


    def __init__(self, patternSize=(7, 7), cameraDeviceID=0,
                 sceneSize=(800, 600)):

        self.emptyFreqThreshold = 0.3
        self.playerDistThreshold = 0.4
        self.shadowDistThreshold = 0.45

        self._boardRotation = ROTATION_0
        self.flipBoardX = False
        self.flipBoardY = False
        self._shadowDirection = DIRECTION_UP

        self._scene = None
        self._sceneGray = None
        self._board = None

        self._patternSize = patternSize
        self._numCorners = patternSize[0] * patternSize[1]

        self._squareFreqs = numpy.empty(
                (patternSize[1] + 1, patternSize[0] + 1),
                numpy.float32)
        self._squareDists = numpy.empty(
                (patternSize[1] + 1, patternSize[0] + 1),
                numpy.float32)
        self._squareStatuses = numpy.empty(
                (patternSize[1] + 1, patternSize[0] + 1),
                numpy.int8)
        self._squareStatuses.fill(SQUARE_STATUS_UNKNOWN)

        self._clusterer = sklearn.cluster.MiniBatchKMeans(2)

        self._capture = cv2.VideoCapture(cameraDeviceID)
        self._sceneSize = ResizeUtils.cvResizeCapture(
                self._capture, sceneSize)
        w, h = self._sceneSize

        self._lastCorners = None
        self._lastCornersSceneGray = numpy.empty(
               (h, w), numpy.uint8)
        self._boardHomography = None

        self._squareWidth = min(w, h) // (max(patternSize) + 1)
        self._squareArea = self._squareWidth ** 2

        self._boardSize = (
            (patternSize[0] + 1) * self._squareWidth,
            (patternSize[1] + 1) * self._squareWidth
        )

        self._referenceCorners = []
        for x in range(patternSize[0]):
            for y in range(patternSize[1]):
                self._referenceCorners += [[x, y]]
        self._referenceCorners = numpy.array(
                self._referenceCorners, numpy.float32)
        self._referenceCorners *= self._squareWidth
        self._referenceCorners += self._squareWidth


    def update(self, drawCorners=False,
               drawSquareStatuses=True):

        if not self._updateScene():
            return False  # Failure

        self._updateBoardHomography()
        self._updateBoard()

        if drawCorners and self._lastCorners is not None:
            # Draw the board's grid.
            cv2.drawChessboardCorners(
                    self._scene, self._patternSize,
                    self._lastCorners, True)

        if drawSquareStatuses:
            for i in range(self._patternSize[0] + 1):
                for j in range(self._patternSize[1] + 1):
                    self._drawSquareStatus(i, j)

        return True  # Success


    def _updateScene(self):

        success, self._scene = self._capture.read(self._scene)
        if not success:
            return False  # Failure

        # Use the red channel as grayscale.
        self._sceneGray = ColorUtils.extractChannel(
                self._scene, 2, self._sceneGray)

        return True  # Success


    def _updateBoardHomography(self):

        if self._lastCorners is not None:
            corners, status, error = cv2.calcOpticalFlowPyrLK(
                    self._lastCornersSceneGray,
                    self._sceneGray, self._lastCorners, None)
            # Status is 1 if tracked, 0 if not tracked.
            numCornersTracked = sum(status)
            # If not tracked, error is invalid so set it to 0.
            error[:] = error * status
            meanError = (sum(error) / numCornersTracked)[0]
            if meanError < 4.0:
                # The board's old corners and homography are
                # still good enough.
                return

        # Find the corners in the board's grid.
        cornersWereFound, corners = cv2.findChessboardCorners(
                self._sceneGray, self._patternSize,
                flags=cv2.CALIB_CB_ADAPTIVE_THRESH)

        if cornersWereFound:

            # Find the homography.
            corners = numpy.array(corners, numpy.float32)
            corners = corners.reshape(self._numCorners, 2)
            self._boardHomography, matches = cv2.findHomography(
                    corners, self._referenceCorners, cv2.RANSAC)

            # Record the corners and their image.
            self._lastCorners = corners
            self._lastCornersSceneGray[:] = self._sceneGray


    def _updateBoard(self):

        if self._boardHomography is not None:

            # Warp the board to obtain a bird's-eye view.
            self._board = cv2.warpPerspective(
                    self._scene, self._boardHomography,
                    self._boardSize, self._board)

            # Rotate and flip the board.
            flipX = self.flipBoardX
            flipY = self.flipBoardY
            if self._boardRotation == ROTATION_CCW_90:
                cv2.transpose(self._board, self._board)
                flipX = not flipX
            elif self._boardRotation == ROTATION_180:
                flipX = not flipX
                flipY = not flipY
            elif self._boardRotation == ROTATION_CCW_270:
                cv2.transpose(self._board, self._board)
                flipY = not flipY
            if flipX:
                if flipY:
                    cv2.flip(self._board, -1, self._board)
                else:
                    cv2.flip(self._board, 1, self._board)
            elif flipY:
                cv2.flip(self._board, 0, self._board)

            for i in range(self._patternSize[0] + 1):
                for j in range(self._patternSize[1] + 1):
                    self._updateSquareData(i, j)
            for i in range(self._patternSize[0] + 1):
                for j in range(self._patternSize[1] + 1):
                    self._updateSquareStatus(i, j)


    def _updateSquareData(self, i, j):

        x0 = i * self._squareWidth
        x1 = x0 + self._squareWidth
        y0 = j * self._squareWidth
        y1 = y0 + self._squareWidth

        # Find the two dominant colors in the square.
        self._clusterer.fit(
                self._board[y0:y1, x0:x1].reshape(
                        self._squareArea, 3))

        # Find the proportion of the square's area that is
        # occupied by the less dominant color.
        freq = numpy.mean(self._clusterer.labels_)
        if freq > 0.5:
            freq = 1.0 - freq

        # Find the distance between the dominant colors.
        dist = ColorUtils.normColorDist(
                self._clusterer.cluster_centers_[0],
                self._clusterer.cluster_centers_[1])

        self._squareFreqs[j, i] = freq
        self._squareDists[j, i] = dist


    def _updateSquareStatus(self, i, j):

        freq = self._squareFreqs[j, i]
        dist = self._squareDists[j, i]

        if self._shadowDirection == DIRECTION_UP:
            if j > 0:
                neighborFreq = self._squareFreqs[j - 1, i]
                neighborDist = self._squareDists[j - 1, i]
            else:
                neighborFreq = None
                neighborDist = None
        elif self._shadowDirection == DIRECTION_LEFT:
            if i > 0:
                neighborFreq = self._squareFreqs[j, i - 1]
                neighborDist = self._squareDists[j, i - 1]
            else:
                neighborFreq = None
                neighborDist = None
        elif self._shadowDirection == DIRECTION_DOWN:
            if j < self._patternSize[1]:
                neighborFreq = self._squareFreqs[j + 1, i]
                neighborDist = self._squareDists[j + 1, i]
            else:
                neighborFreq = None
                neighborDist = None
        elif self._shadowDirection == DIRECTION_RIGHT:
            if i < self._patternSize[0]:
                neighborFreq = self._squareFreqs[j, i + 1]
                neighborDist = self._squareDists[j, i + 1]
            else:
                neighborFreq = None
                neighborDist = None
        else:
            neighborFreq = None
            neighborDist = None

        castsShadow = \
                neighborFreq is not None and \
                neighborFreq < self.emptyFreqThreshold and \
                neighborDist is not None and \
                neighborDist > self.shadowDistThreshold

        if freq < self.emptyFreqThreshold:
            squareStatus = SQUARE_STATUS_EMPTY
        else:
            if dist < self.playerDistThreshold:
                if castsShadow:
                    squareStatus = SQUARE_STATUS_KING_PLAYER_1
                else:
                    squareStatus = SQUARE_STATUS_PAWN_PLAYER_1
            else:
                if castsShadow:
                    squareStatus = SQUARE_STATUS_KING_PLAYER_2
                else:
                    squareStatus = SQUARE_STATUS_PAWN_PLAYER_2
        self._squareStatuses[j, i] = squareStatus


    def _drawSquareStatus(self, i, j):

        x0 = i * self._squareWidth
        y0 = j * self._squareWidth

        squareStatus = self._squareStatuses[j, i]
        if squareStatus > 0:
            text = str(squareStatus)
            textSize, textBaseline = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_PLAIN, 1.0, 1)
            xCenter = x0 + self._squareWidth // 2
            yCenter = y0 + self._squareWidth // 2
            textCenter = (xCenter - textSize[0] // 2,
                          yCenter + textBaseline)
            cv2.putText(self._board, text, textCenter,
                        cv2.FONT_HERSHEY_PLAIN, 1.0,
                        (0, 255, 0), 1, cv2.LINE_AA)
