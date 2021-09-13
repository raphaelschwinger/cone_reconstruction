import matplotlib.pyplot as plt
import os
import numpy as np


plt.figure(1)

# load results
directory_name = os.path.abspath(os.path.dirname(__file__))
results = sorted([os.path.join(directory_name, frame_dir)
                 for frame_dir in os.listdir(directory_name)])

# load position data from blender
blender_cone_path = os.path.join(directory_name, 'cone_position.p3d')
blender_cone_points_3D = np.loadtxt(blender_cone_path, delimiter=';')
plt.plot(blender_cone_points_3D[:, 0], blender_cone_points_3D[:, 1], 'r^')

# load car position data from blender
blender_car_path = os.path.join(directory_name, 'car_position.p3d')
blender_car_points_3D = np.loadtxt(blender_car_path, delimiter=';')
plt.plot(blender_car_points_3D[:, 0],
         blender_car_points_3D[:, 1], label='real position'.format('r'))

i = 0
for result_path in results:
    i += 1
    # check if result is a directory
    if os.path.isdir(result_path):
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # strip last dimension of points to make 2D points
        points_2D = points_3D[:, :2]

        # dir_name
        dir_name = os.path.basename(result_path)

        # plot points
        plt.plot(points_2D[:, 0], points_2D[:, 1],
                 label=dir_name.format(i=i))
        plt.legend(loc='best')

# add cone position to results
blender_position_path = os.path.join(directory_name, 'blender-position')
cone_points_3D = np.loadtxt(os.path.join(
    blender_position_path, 'cone_transformation.p3d'), delimiter=';')
cone_points_2D = cone_points_3D[:, :2]
plt.plot(cone_points_2D[:, 0], cone_points_2D[:, 1], 'y^')


# "normalize points"

plt.figure(2)
i = 0
for result_path in results:
    i += 1
    # check if result is a directory
    if os.path.isdir(result_path):
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # normalize points in relation to first car position
        # calculate delta to first car position
        delta_points_3D = blender_car_points_3D[0] - points_3D[0]
        for point_3D in points_3D:
            point_3D += delta_points_3D

        # strip last dimension of points to make 2D points
        points_2D = points_3D[:, :2]

        # dir_name
        dir_name = os.path.basename(result_path)

        # plot points
        plt.plot(points_2D[:, 0], points_2D[:, 1],
                 label=dir_name.format(i=i))
        plt.legend(loc='best')

# add cone position to results
blender_position_path = os.path.join(directory_name, 'blender-position')
cone_points_3D = np.loadtxt(os.path.join(
    blender_position_path, 'cone_transformation.p3d'), delimiter=';')
cone_points_2D = cone_points_3D[:, :2]
plt.plot(cone_points_2D[:, 0], cone_points_2D[:, 1], 'y^')

plt.plot(blender_cone_points_3D[:, 0], blender_cone_points_3D[:, 1], 'r^')
plt.plot(blender_car_points_3D[:, 0],
         blender_car_points_3D[:, 1], label='real position'.format('r'))

plt.show()
