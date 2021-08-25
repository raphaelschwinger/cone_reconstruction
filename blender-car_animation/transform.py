import os
import cv2
import numpy as np
import argparse


"""
Calculate the affine transformation matrix from 4 matching point pairs
and apply the affine transformation matrix to all given points
"""
if __name__ == "__main__":

    # known 3d points

    known_points_3d = np.loadtxt('./known_points', delimiter=';')
    print('known points: ', known_points_3d)

	# load 3d points from file
     
    points_3D = np.loadtxt('./reconstruction.p3d', delimiter=';')

    print('reconstructed points: ', points_3D)

    # getAffineTransformation
    (retval, mat, out) = cv2.estimateAffine3D(points_3D[:4], known_points_3d)
    print('affine matrix', mat)

    # transform points

    trans_points_3D = np.zeros(points_3D.shape, np.float32)

    for i in range(len(points_3D)):
        # add dimension
        p_4d = np.zeros((4,1), np.float32)
        p_4d[0] = points_3D[i][0]
        p_4d[1] = points_3D[i][1]
        p_4d[2] = points_3D[i][2]
        p_4d[3] = 1.0
        trans_point = np.dot(mat, p_4d)
        print(trans_point)
        # transform (3,1) to 3 and store in array
        trans_points_3D[i] = trans_point.ravel()

    print('Transformed point: ', trans_points_3D)


    # load car_reconstruction
    car_points_3D = np.loadtxt('car_reconstruction.p3d', delimiter=';')
    trans_points_3D = np.zeros(car_points_3D.shape, np.float32)

    for i in range(len(car_points_3D)):
        # add dimension
        p_4d = np.zeros((4,1), np.float32)
        p_4d[0] = car_points_3D[i][0]
        p_4d[1] = car_points_3D[i][1]
        p_4d[2] = car_points_3D[i][2]
        p_4d[3] = 1.0
        trans_point = np.dot(mat, p_4d)
        print(trans_point)
        # transform (3,1) to 3 and store in array
        trans_points_3D[i] = trans_point.ravel()

    # reset reconstruction file
    open('./car_transformed.p3d', 'w').close()
    # save reconstructed points in file
    with open('./car_transformed.p3d', 'a') as f:
        for point in trans_points_3D:
            print(point, file=f)
  

    