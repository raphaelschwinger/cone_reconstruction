import matplotlib.pyplot as plt
import os
import numpy as np

color = ['blue', 'green', 'orange']


plt.figure(1)

# load results
directory_name = os.path.abspath(os.path.dirname(__file__))
results = sorted([os.path.join(directory_name, frame_dir)
                 for frame_dir in os.listdir(directory_name)])

# load position data from blender
blender_cone_path = os.path.join(directory_name, 'cone_position.p3d')
blender_cone_points_3D = np.loadtxt(blender_cone_path, delimiter=';')

# load car position data from blender
blender_car_path = os.path.join(directory_name, 'car_position.p3d')
blender_car_points_3D = np.loadtxt(blender_car_path, delimiter=';')


# add cone position to results
blender_position_path = os.path.join(directory_name, 'blender-position')
cone_points_3D = np.loadtxt(os.path.join(
    blender_position_path, 'cone_transformation.p3d'), delimiter=';')
transformed_cone_points_2D = cone_points_3D[:, :2]


i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # strip last dimension of points to make 2D points
        points_2D = points_3D[:, :2]

        # dir_name
        dir_name = os.path.basename(result_path)

        # plot points
        plt.plot(points_2D[:, 0], points_2D[:, 1],
                 label=dir_name, color=color[i % 3])
        plt.legend(loc='best')

# add "real position" to plot
plt.plot(blender_car_points_3D[:, 0],
         blender_car_points_3D[:, 1], label='real position'.format('r'))
plt.plot(blender_cone_points_3D[:, 0], blender_cone_points_3D[:, 1], 'r^')
# add reconstucted cone points to plot
plt.plot(transformed_cone_points_2D[:, 0],
         transformed_cone_points_2D[:, 1], 'y^')
plt.ylabel("Y position", labelpad=15)
plt.xlabel("X position", labelpad=15)


# "normalize points"

# add cone position to results
plt.figure(2)
i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
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
                 label=dir_name, color=color[i % 3])
        plt.legend(loc='best')

# add "real position" to plot
plt.plot(blender_car_points_3D[:, 0],
         blender_car_points_3D[:, 1], label='real position'.format('r'))
plt.plot(blender_cone_points_3D[:, 0], blender_cone_points_3D[:, 1], 'r^')
# add reconstucted cone points to plot
plt.plot(transformed_cone_points_2D[:, 0],
         transformed_cone_points_2D[:, 1], 'y^')
plt.ylabel("Y position", labelpad=15)
plt.xlabel("X position", labelpad=15)


# Calculate MSE
fig = plt.figure(3)
i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # calculate MSE
        # print distance to blender_car_points_3D
        print(np.linalg.norm(
            points_3D - blender_car_points_3D))
        mse = np.mean(np.square(np.linalg.norm(
            points_3D - blender_car_points_3D, ord=2, axis=1)))
        # dir_name
        dir_name = os.path.basename(result_path)
        print(dir_name, mse)
        plt.text(i + 0.45, mse + 1, str(round(mse, 2)), fontweight='bold')
        plt.bar(i, mse, 1, label=dir_name, color=color[i % 3])
        plt.legend(loc='best')
        plt.ylabel("Mean squared error", labelpad=15)
        plt.xticks([])


# MSE for normalized points
fig = plt.figure(4)
i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # normalize points in relation to first car position
        # calculate delta to first car position
        delta_points_3D = blender_car_points_3D[0] - points_3D[0]
        for point_3D in points_3D:
            point_3D += delta_points_3D

        # calculate MSE
        mse = np.mean(np.square(np.linalg.norm(
            points_3D - blender_car_points_3D, ord=2, axis=1)))
        # dir_name
        dir_name = os.path.basename(result_path)
        print(dir_name, mse)
        plt.text(i + 0.45, mse + 0.01, str(round(mse, 2)), fontweight='bold')
        plt.bar(i, mse, 1, label=dir_name, color=color[i % 3])
        plt.legend(loc='best')
        plt.ylabel("Mean squared error", labelpad=15)
        plt.xticks([])

# Display euclidean distance to blender_car_points_3D
fig = plt.figure(5)
i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # normalize points in relation to first car position
        # calculate delta to first car position
        delta_points_3D = blender_car_points_3D[0] - points_3D[0]
        for point_3D in points_3D:
            point_3D += delta_points_3D

        # calculate distances
        distances = np.linalg.norm(
            points_3D - blender_car_points_3D, ord=2, axis=1)
        # dir_name
        dir_name = os.path.basename(result_path)
        plt.plot(distances, label=dir_name, color=color[i % 3])
        plt.legend(loc='best')
        plt.ylabel("euclidean distances", labelpad=15)
        plt.xlabel("frame")


# plot optimization error
fig = plt.figure(6)
i = 0
for result_path in results:
    # check if result is a directory
    if os.path.isdir(result_path):
        i += 1
        error = np.loadtxt(os.path.join(
            result_path, 'optimization_errors.txt'), delimiter=';')
        dir_name = os.path.basename(result_path)
        plt.plot(error, label=dir_name, color=color[i % 3])
        plt.legend(loc='best')
        plt.ylabel("optimization error", labelpad=15)
        plt.xlabel("frame")


plt.show()
