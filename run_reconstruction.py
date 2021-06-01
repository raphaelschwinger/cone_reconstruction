import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))

import cv2
from track_reconstruction.track import Track
from track_reconstruction.display import Display3D
import os
import numpy as np

if __name__ == "__main__":


	path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'blender-house/'))
	image_paths = sorted([os.path.join(path, file) for file in os.listdir(path) if file.endswith(".png")])[:4]
	points_paths = sorted([os.path.join(path, file) for file in os.listdir(path) if file.endswith(".p2d")])[:4]

	disp3d = Display3D()
	track = Track()

	for image_path, points_path in zip(image_paths, points_paths):
		print(f'adding image {image_path}')

		img = cv2.imread(image_path)
		points_2D = np.loadtxt(points_path)
		H, W = img.shape[:2]
		F = 1050

		if W > 1024:
			downscale = 1024.0 / W
			F *= downscale
			H = int(H * downscale)
			W = 1024
			print(f'scaled img down to {W}x{H}')

			# camera intrinsics
		K = np.array([[F, 0, W//2], [0, F, H//2], [0, 0, 1]], dtype=np.float32)

		track.processFrame(img, points_2D, K)

	disp3d.paint(track)

	input('Press enter to exit...')