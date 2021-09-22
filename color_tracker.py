import os
import sys
import cv2
import numpy as np
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Enter the image folder')
    parser.add_argument('dir_name', metavar='dir_name', type=str,
                        help='Directory of images')
    parser.add_argument('cam_name', metavar='cam_name', type=str,
                    help='Camera name, e.g. 01')

    args = parser.parse_args()

    directory_name = args.dir_name  # 'blender-house' or cone-track

    cam_name = args.cam_name

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), directory_name))

    frame_dir_path = os.path.join(path, 'frames')

    # Read video
    video_path = os.path.join(path, cam_name + '-video0001-0200.avi')
    video = cv2.VideoCapture(video_path)
    # video = cv2.VideoCapture(0) # for using CAM

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()

    # definig the range of red color
    # lower boundary RED color range values; Hue (0 - 10)
    lower1 = np.array([0, 50, 30])
    upper1 = np.array([5, 255, 255])
    
    # upper boundary RED color range values; Hue (160 - 180)
    lower2 = np.array([180,50,30])
    upper2 = np.array([180,255,255])
    

    open(os.path.join(path, 'tracking-result-'+  cam_name + '.p2d'), 'w').close()

    frame_count = 0

    result_x = 100
    result_y = 100
    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        frame_count += 1

        current_frame_path = os.path.join(
            frame_dir_path, str(frame_count).zfill(4))

        os.makedirs(current_frame_path, exist_ok=True)

        #converting frame(img i.e BGR) to HSV (hue-saturation-value)
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lower_mask = cv2.inRange(hsv, lower1, upper1)
        upper_mask = cv2.inRange(hsv, lower2, upper2)
    
        full_mask = lower_mask + upper_mask;
        # Morphological transformation, Dilation
        kernal = np.ones((5, 5), "uint8")

        red = cv2.dilate(full_mask, kernal)
        res = cv2.bitwise_and(frame, frame, mask=red)

        # Tracking the Red Color
        (contours, hierarchy) = cv2.findContours(
            red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # save car tracking coordinates
        # reset transformation file
        open(os.path.join(current_frame_path, cam_name + '.p2d'), 'w').close()

        # get min and max point values
        min_x = -1
        min_y = -1
        max_x = -1
        max_y = -1

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if(area > 50):
                x, y, w, h = cv2.boundingRect(contour)
                # check if min/max values are set
                if (min_x == -1):
                    min_x = x
                if (min_y == -1):
                    min_y = y
                if (max_x == -1):
                    max_x = x + w
                if (max_y == -1):
                    max_y = y + h
                # update min/max values
                if (x < min_x):
                    min_x = x
                if (y < min_y):
                    min_y = y
                if (x + w > max_x):
                    max_x = x + w
                if (y + h > max_y):
                    max_y = y + h
                if (min_x != -1) and (min_y != -1) and (max_x != -1) and (max_y != -1):
                    result_x = (max_x + min_x) / 2
                    result_y = max_y + 3 * (max_y - min_y)

        # draw rectangle
        img = cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
        cv2.putText(frame, "RED color", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
        # save result
        with open(os.path.join(current_frame_path, cam_name + '.p2d'), 'a') as f:
            # use bottom of reactangle as center
            print(f'{result_x} {result_y}', file=f)
        with open(os.path.join(path, 'tracking-result-'+  cam_name + '.p2d'), 'a') as f:
            print(f'{result_x}; {result_y}', file=f)
        cv2.rectangle(frame, [min_x, min_y], [max_x, max_y], (255, 0, 0), 2, 1)




        # Display result
        cv2.imshow("Tracking", frame)

        # Exit if ESC pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press SPACE bar
            break

    video.release()
    cv2.destroyAllWindows()
