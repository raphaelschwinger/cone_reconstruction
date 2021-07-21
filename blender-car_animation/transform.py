import os
import cv2
import numpy as np
import argparse

if __name__ == "__main__":

    # known 3d points

    known_points_3d = np.loadtxt('./known_points', delimiter=';')
    print(known_points_3d)

	# load 3d points from file
    parser = argparse.ArgumentParser(description='Enter the 3d point file')
    parser.add_argument('file_name', metavar='file_name', type=str,
                        help='name of the 3d pint file')

    args = parser.parse_args()

    file_name = args.file_name

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), file_name))
    
    points_3D = np.loadtxt(path, delimiter=';')

    print(points_3D)

    # getAffineTransformation
    (retval, aff, inliers) = cv2.estimateAffine3D(points_3D[:3], known_points_3d)
    print(retval)
    print(aff)
    print(inliers)

    