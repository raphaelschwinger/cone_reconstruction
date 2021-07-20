import os
import numpy as np
import argparse

if __name__ == "__main__":
	# load 2d points from file
    parser = argparse.ArgumentParser(description='Enter the 3d point file')
    parser.add_argument('file_name', metavar='dir_name', type=str,
                        help='name of the 3d pint file')

    args = parser.parse_args()

    file_name = args.file_name

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), file_name))
    
    points_3D = np.loadtxt(path, delimiter=';')

    print(points_3D)

    