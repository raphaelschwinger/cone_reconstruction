import sys
import os
import cv2
import numpy as np
import argparse
sys.path.append('/opt/app/lib')
sys.path.append('/usr/local/lib/')
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'lib')))
from track_reconstruction.display import Display3D
from track_reconstruction.track import Track


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Enter the image folder')
    parser.add_argument('dir_name', metavar='dir_name', type=str,
                        help='Directory of images')

    args = parser.parse_args()

    directory_name = args.dir_name  # 'blender-house' or cone-track

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), directory_name))


    disp3d = Display3D()

    # save reconstructed points in array
    reconstruction = []
    # all reconstructed points are the points from every camera
    allReconstructedPoints = []

    # iterate through all frames
    frame_dir_path = os.path.join(path, 'frames') 
    frames = sorted([os.path.join(frame_dir_path, frame_dir)
                     for frame_dir in os.listdir(frame_dir_path)])

    for frame_path in frames:
        track = Track()

        #  load image paths and point paths
        image_paths = sorted([os.path.join(frame_path, file)
                         for file in os.listdir(frame_path) if file.endswith(".png")])[:3]
        points_paths = sorted([os.path.join(frame_path, file)
                          for file in os.listdir(frame_path) if file.endswith(".p2d")])[:3]

        for image_path, points_path in zip(image_paths, points_paths):
            print(f'adding image {image_path}')

            # load image
            img = cv2.imread(image_path)
            # load point of car
            car_2D = np.loadtxt(points_path)
            
            # add cone positions
            filename = points_path.split(os.sep)[-1]
            points_2D = np.loadtxt(os.path.join(path, filename))
            points_2D = np.append(points_2D, [car_2D], axis=0)
            H, W = img.shape[:2]
            # Focal Length of camera, see README of how to calculate
            F = 1707

            # camera intrinsics
            K = np.array([[F, 0, W//2], [0, F, H//2], [0, 0, 1]], dtype=np.float32)

            positions = track.processFrame(img, points_2D, K)
            allReconstructedPoints.append(positions)

    # disp3d.paint(track)

    # track.printMap()

    # get every third point in reconstruction as the last camera improves the results of the ones before only every third is interesting
    for i in range(0, len(allReconstructedPoints), 3):
        reconstruction.append(allReconstructedPoints[i+2])
            
    # save cone reconstruction
    # reset reconstruction file
    open(os.path.join(frame_path, 'cone_reconstruction.p3d'), 'w').close()
    # save reconstructed points in file
    with open(os.path.join(frame_path, 'cone_reconstruction.p3d'), 'a') as f:
        for pts in reconstruction:
            for p in pts:
                print(f'{p[0]};{p[1]};{p[2]}', file=f)

    # save car reconstruction
    # reset reconstruction file
    open(os.path.join(frame_path, 'car_reconstruction.p3d'), 'w').close()
    # save reconstructed points in file
    with open(os.path.join(frame_path, 'car_reconstruction.p3d'), 'a') as f:
        for pts in reconstruction:
            print(f'{pts[-1][0]};{pts[-1][1]};{pts[-1][2]}', file=f)

    input('Press enter to exit...')

