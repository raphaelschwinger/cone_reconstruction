import os
import cv2
import numpy as np
import argparse


"""
Calculate the affine transformation matrix from 4 matching point pairs
and apply the affine transformation matrix to all given points
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Enter the image folder')
    parser.add_argument('dir_name', metavar='dir_name', type=str,
                        help='Directory of images')

    args = parser.parse_args()

    directory_name = args.dir_name  # 'blender-house' or cone-track

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), directory_name))

    # known 3d points

    known_points_3d = np.loadtxt(os.path.join(path, './known_points'), delimiter=';')
    print('known points: ', known_points_3d)

	# load 3d points from file
     
    points_3D = np.loadtxt(os.path.join(path, './cone_reconstruction.p3d'), delimiter=';')

    # print('reconstructed points: ', points_3D)

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
        # print(trans_point)
        # transform (3,1) to 3 and store in array
        trans_points_3D[i] = trans_point.ravel()


    # save cone transformation
    # reset transformation file
    open(os.path.join(path, 'cone_transformation.p3d'), 'w').close()
    # save reconstructed points in file
    with open(os.path.join(path, 'cone_transformation.p3d'), 'a') as f:
        for p in trans_points_3D:
            print(f'{round(float(p[0]), 3)};{round(float(p[1]), 3)};{round(float(p[2]), 3)}', file=f)


    # # load car_reconstruction
    car_points_3D = np.loadtxt(os.path.join(path, 'car_reconstruction.p3d'), delimiter=';')
    car_trans_points_3D = np.zeros(car_points_3D.shape, np.float32)

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
        car_trans_points_3D[i] = trans_point.ravel()
    
    # save cone transformation
    # reset transformation file
    open(os.path.join(path, 'car_transformation.p3d'), 'w').close()
    # save reconstructed points in file
    with open(os.path.join(path, 'car_transformation.p3d'), 'a') as f:
        for p in car_trans_points_3D:
            print(f'{round(float(p[0]), 3)};{round(float(p[1]), 3)};{round(float(p[2]), 3)}', file=f)

  

    