import sys
import argparse
import os
sys.path.append('/opt/app/lib')
sys.path.append('/usr/local/lib/')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))



import cv2
from track_reconstruction.track import Track
from track_reconstruction.display import Display3D
import os
import numpy as np

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Enter the image folder') 
	parser.add_argument('dir_name', metavar='dir_name', type=str,
                    help='Directory of images')

	args = parser.parse_args()
 
	directory_name= args.dir_name  #'blender-house' or cone-track



	path = os.path.abspath(os.path.join(os.path.dirname(__file__), directory_name))
	image_paths = sorted([os.path.join(path, file) for file in os.listdir(path) if file.endswith(".png")])[:6]
	points_paths = sorted([os.path.join(path, file) for file in os.listdir(path) if file.endswith(".p2d")])[:6]

	disp3d = Display3D()
	track = Track()

	for image_path, points_path in zip(image_paths, points_paths):
		print(f'adding image {image_path}')

		img = cv2.imread(image_path)
		points_2D = np.loadtxt(points_path)
		H, W = img.shape[:2]
		F = 2400

		# if W > 1024:
		# 	downscale = 1024.0 / W
		# 	F *= downscale
		# 	H = int(H * downscale)
		# 	W = 1024
		# 	print(f'scaled img down to {W}x{H}')

			# camera intrinsics
		K = np.array([[F, 0, W//2], [0, F, H//2], [0, 0, 1]], dtype=np.float32)

		track.processFrame(img, points_2D , K)

	disp3d.paint(track)
	track.printMap()


	input('Press enter to exit...')