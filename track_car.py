import os
import sys
import cv2
import numpy as np
import argparse
 
if __name__ == '__main__' :

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
 
    tracker_types = ['KCF', 'CSRT']
    tracker_type = tracker_types[1]
 
#  two trackers that can be tested, CSRT seems to perform better  
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    elif tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()

    # Read video
    video_path = os.path.join(path, cam_name + '-video0001-0080.avi') 
    video = cv2.VideoCapture(video_path)
    # video = cv2.VideoCapture(0) # for using CAM
 
    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()
 
    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()
     
    # Define an initial bounding box
    bbox = (287, 23, 86, 320)
 
    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False)
 
    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    frame_count = 0
 
    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        frame_count += 1

        current_frame_path = os.path.join(frame_dir_path,str(frame_count).zfill(5))

        os.makedirs(current_frame_path, exist_ok=True)
         
        # Start timer
        timer = cv2.getTickCount()
 
        # Update tracker
        ok, bbox = tracker.update(frame)
 
        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

        # save car tracking coordinates
        # reset transformation file
        open(os.path.join(current_frame_path, cam_name +  '.p3d'), 'w').close()
 
        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            print(p1,p2)
            # save reconstructed points in file
            with open(os.path.join(current_frame_path, cam_name +  '.p3d'), 'a') as f:
                print(f'{(p1[0] + p2[0]) / 2 } {(p1[1] + p2[1]) / 2 }', file=f)
            
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        else :
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
            # save reconstructed points in file
            # with open(os.path.join(current_frame_path, cam_name +  '.p3d'), 'a') as f:
            #     print(f' ', file=f)
 
        # Display tracker type on frame
        cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
     
        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
 
        # Display result
        cv2.imshow("Tracking", frame)
 
        # Exit if ESC pressed
        if cv2.waitKey(1) & 0xFF == ord('q'): # if press SPACE bar
            break

    video.release()
    cv2.destroyAllWindows()
   