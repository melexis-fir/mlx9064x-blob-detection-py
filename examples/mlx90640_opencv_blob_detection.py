# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Purspose: demo to use EVB90640 and display with opencv.
# (c) 2019 Melexis

import os, sys
# work-around for having the parent directory added to the search path of packages.
# to make `import mlx.pympt` to work, even EVB pip package itself is not installed!
# note: when installed, it will take the installed version!
# https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html#case-2-syspath-could-change
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "mlx9064x-driver-py"))

import cv2 as cv
import numpy as np
from mlx.mlx90640 import Mlx9064x
import time

# scaling to gray
TMIN = 15.00
TMAX = 35.00

ZOOM = 10 # 20x result in 640x480 image for 90640!
INTERPOLATION = cv.INTER_CUBIC
# INTERPOLATION = cv.INTER_NEAREST

frames_per_second = 8

def print_objects_info(contours):
    print(len(contours), ":")
    if contours is not None:
        i = 1
        for contour in contours:
            area = cv.contourArea(contour)
            if area < 100 :  # skip small objects
                continue
            M = cv.moments(contour)
            cX = -1
            cY = -1
            if M["m00"] != 0: # avoid division by zero
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            print("obj#{} @ {}, {} -- area: {}".format(i, cX, cY, area))
            i += 1


frame_background = None
# fourcc = cv.VideoWriter_fourcc('M', 'J', 'P', 'G')
# avi_input = cv.VideoWriter('mlx90640_input.avi', fourcc, frames_per_second, (16 * 40, 12 * 40))
# avi_processed = cv.VideoWriter('mlx90640_processed.avi', fourcc, frames_per_second, (16 * 40, 12 * 40))


def blob_detection(frame, take_new_background = False):
    global frame_background

    if frame is None:
        return None
    frame_interpol = cv.resize(frame, None, fx=ZOOM, fy=ZOOM, interpolation=cv.INTER_CUBIC)
    frame_nearest = cv.resize(frame, None, fx=ZOOM, fy=ZOOM, interpolation=cv.INTER_NEAREST)
    frame_color = cv.applyColorMap(frame_interpol, cv.COLORMAP_JET)
    frame_color_small = cv.applyColorMap(frame_nearest, cv.COLORMAP_JET)

    if take_new_background or frame_background is None:
        frame_background = frame_interpol

    _, threshold = cv.threshold(frame_interpol, 110, 255, cv.THRESH_BINARY)

    kernel40 = np.ones((20, 20), np.uint8)
    kernel5 = np.ones((5, 5), np.uint8)

    difference = cv.absdiff(frame_background, frame_interpol)
    _, difference_bin = cv.threshold(difference, 30, 255, cv.THRESH_BINARY)

    # Morphology: https://pysource.com/2018/02/27/morphological-transformation-opencv-3-4-with-python-3-tutorial-17/
    dilation = cv.dilate(difference_bin, kernel40)
    dilation5 = cv.dilate(difference_bin, kernel5, iterations=2)
    erode = cv.erode(dilation5, kernel5, iterations=3)

    diff_contours = cv.findContours(difference_bin, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    dilation_contours = cv.findContours(dilation, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    erode_contours = cv.findContours(erode, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    index = 0
    if cv.__version__.startswith ("3"):
      index = 1
    diff_contours = diff_contours[index]
    dilation_contours = dilation_contours[index]
    erode_contours = erode_contours[index]

    print_objects_info(diff_contours)

    if diff_contours is not None:
        for contour in diff_contours:
            area = cv.contourArea(contour)
            if area < 100:  # skip small objects
                continue
            cv.drawContours(difference_bin, contour, -1, 128, -1)

    if erode_contours is not None:
        for contour in erode_contours:
            area = cv.contourArea(contour)
            if area < 100:  # skip small objects
                continue
            cv.drawContours(difference_bin, contour, -1, 200, 2)
            cv.drawContours(frame_interpol, contour, -1, 255, 7)
            cv.drawContours(frame_color, contour, -1, (255, 255, 255), 4)
            cv.drawContours(frame_color_small, contour, -1, (255, 255, 255), 4)

    # update background:
    # 1. create mask to skip detected objects
    # 2. take 10% of current frame to add to background frame

    # 1. create mask to skip detected objects
    background_mask = np.ones(frame_background.shape, np.uint8) * 255

    if dilation_contours is not None:
        for contour in dilation_contours:
            area = cv.contourArea(contour)
            if area < 100:  # skip small objects
                continue
            cv.drawContours(difference_bin, contour, -1, 55, 3)
            cv.fillPoly(background_mask, pts=[contour], color=0)

    # 2. take 10% of current frame to add to background frame
    background_wo_objects = cv.bitwise_and(frame_interpol, background_mask)
    background_at_objects = cv.bitwise_and(frame_background, cv.bitwise_not(background_mask))

    background_wo_objects = cv.add(background_wo_objects, background_at_objects)
    frame_background = cv.addWeighted(frame_background, 0.9, background_wo_objects, 0.1, 0)
    # we might consider to blur the background a bit...

    # avi_input.write(frame_color_small)
    # avi_processed.write(frame_color)

    # cv.imshow("frame", frame)
    # cv.imshow("frame_interpol", frame_interpol)
    # cv.imshow("frame_background", frame_background)
    # cv.imshow("background_mask", background_mask)
    # cv.imshow("threshold", threshold)
    # cv.imshow("diff", difference)
    # cv.imshow("diff bin", difference_bin)
    # cv.imshow("color", frame_color)
    cv.imshow("color_small", frame_color_small)

    return 0


def main():
    port = "auto"
    # port = "I2C-1"
    # port = "I2CBB-03-05"
    port = 'auto'
    if len(sys.argv) >= 2:
        port = sys.argv[1]

    dev = Mlx9064x(port, frame_rate=frames_per_second)
    dev.init()

    take_new_background = True

    while True:
      frame = None
      try:
        frame = dev.read_frame()
      except Exception as e:
        print ("ERROR:", e)
        dev.clear_error(frame_rate)
      if frame is not None:
          array_temp = dev.do_compensation(frame)
          array_gray = [((x - TMIN)/(TMAX-TMIN))*255 for x in array_temp]
          # convert array to an opencv frame (monochrome)
          frame = np.flipud(np.array(array_gray, np.uint8).reshape((24, 32, 1)))
          blob_detection(frame, take_new_background)
          take_new_background = False
      key_pressed = cv.waitKey(1)
      if key_pressed in [27, ord('q'), ord('Q')]:
        break
      if key_pressed in [ord('B'), ord('b')]:
        take_new_background = True
    # avi_processed.release()
    # avi_input.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
