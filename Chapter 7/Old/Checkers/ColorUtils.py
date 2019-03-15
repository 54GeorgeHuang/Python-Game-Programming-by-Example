import math
import numpy


def extractChannel(src, channel, dst):
    dstShape = src.shape[:2]
    if dst is None or dst.shape != dstShape or \
            dst.dtype != numpy.uint8:
        dst = numpy.empty(dstShape, numpy.uint8)
    dst[:] = src.flatten()[channel::3].reshape(dstShape)
    return dst


def colorDist(color0, color1):
    # Calculate a red-weighted color distance, as described
    # here: http://www.compuphase.com/cmetric.htm
    rMean = int((color0[2] + color1[2]) / 2)
    rDiff = int(color0[2] - color1[2])
    gDiff = int(color0[1] - color1[1])
    bDiff = int(color0[0] - color1[0])
    return math.sqrt(
        (((512 + rMean) * rDiff * rDiff) >> 8) +
        4 * gDiff * gDiff +
        (((767 - rMean) * bDiff * bDiff) >> 8))


def normColorDist(color0, color1):
    # Normalize based on the distance between (0, 0, 0) and
    # (255, 255, 255).
    return colorDist(color0, color1) / 764.8333151739665
