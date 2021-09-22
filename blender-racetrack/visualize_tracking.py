import matplotlib.pyplot as plt
import os
import numpy as np

# load results
directory_name = os.path.abspath(os.path.dirname(__file__))

# load position data from blender
tracking_result_path1 = os.path.join(directory_name, 'tracking-result-01.p2d')
tracking_result_path2 = os.path.join(directory_name, 'tracking-result-02.p2d')
tracking_result_path3 = os.path.join(directory_name, 'tracking-result-03.p2d')
tracking_result1 = np.loadtxt(tracking_result_path1, delimiter=';')
tracking_result2 = np.loadtxt(tracking_result_path2, delimiter=';')
tracking_result3 = np.loadtxt(tracking_result_path3, delimiter=';')

plt.plot(tracking_result1[:,0], tracking_result1[:,1])
plt.plot(tracking_result2[:,0], tracking_result2[:,1])
plt.plot(tracking_result3[:,0], tracking_result3[:,1])

# smooth the curve
# def smooth(y, box_pts):
#     box = np.ones(box_pts)/box_pts
#     y_smooth = np.convolve(y, box, mode='same')
#     return y_smooth

# value = 19
# tracking_result1[:,0] = smooth(tracking_result1[:,0], value)
# tracking_result1[:,1] = smooth(tracking_result1[:,1], value)
# tracking_result2[:,0] = smooth(tracking_result2[:,0], value)
# tracking_result2[:,1] = smooth(tracking_result2[:,1], value)
# tracking_result3[:,0] = smooth(tracking_result3[:,0], value)
# tracking_result3[:,1] = smooth(tracking_result3[:,1], value)

# plt.plot(tracking_result1[:,0], tracking_result1[:,1])
# plt.plot(tracking_result2[:,0], tracking_result2[:,1])
# plt.plot(tracking_result3[:,0], tracking_result3[:,1])

plt.show()