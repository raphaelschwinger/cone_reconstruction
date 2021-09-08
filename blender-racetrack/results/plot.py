import matplotlib.pyplot as plt
import os
import numpy as np

# load results
directory_name = os.path.abspath(os.path.dirname(__file__))
results = sorted([os.path.join(directory_name, frame_dir)
                 for frame_dir in os.listdir(directory_name)])

i = 0
for result_path in results:
    i += 1
    # check if result is a directory
    if os.path.isdir(result_path):
        points_3D = np.loadtxt(os.path.join(
            result_path, 'car_transformation.p3d'), delimiter=';')

        # strip last dimension of points to make 2D points
        points_2D = points_3D[:, :2]

        # plot points
        plt.plot(points_2D[:, 0], points_2D[:, 1],
                 label=result_path.format(i=i))
        plt.legend(loc='best')


plt.show()
