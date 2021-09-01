import re
import numpy as np
import cv2
from track_reconstruction.optimize_g2o import optimizeMap
from track_reconstruction.utils import normalize, rotation_matrix_from_vectors

LOCAL_WINDOW = 20
CULLING_ERR_THRES = 0.02


class Camera(object):
    def __init__(self, K=None, R=None, t=None, img=None, points_2D=None):
        self.K = K
        self.R = R
        self.t = t
        self.img = img
        self.points_2D = points_2D


    def setPose(self, R, t):
        """Setter function for extrensic Parameters R and t"""
        self.R = R

        # remove dimensions which are 1
        t = np.squeeze(t)
        # if t has 4 elements we need to normalize
        if t.shape[0] == 4:
            self.t = (t/t[3])[:3]
        else:
            self.t = t


    def getPose(self, square=False):
        Rt = np.eye(4 if square else 3, 4)
        Rt[:3, :3] = self.R
        Rt[:3, 3] = self.t
        return Rt


    def getP(self):
        """ 
        composes the Projection-Matrix P from K, R and t
        for this, the pose of the camera need to be set beforehand.
        """
        return np.dot(self.K, self.getPose())


    # normalized keypoints
    @property
    def normalized_points_2D(self):
        if not hasattr(self, '_kps'):
            self._normalized_points_2D = normalize(self.Kinv, self.points_2D)
        return self._normalized_points_2D

    
      # inverse of intrinsics matrix
    @property
    def Kinv(self):
        if not hasattr(self, '_Kinv'):
            self._Kinv = np.linalg.inv(self.K)
        return self._Kinv


class Point3D(object):
    def __init__(self, id, position, color):
        self.id = id
        self.position = position
        self.color = color


class Map(object):
    def __init__(self):
        self.points_3D = []

    def addPoint(self, position, color):
        print(f'added 3Dpoint to map at {position}')
        pt = Point3D(len(self.points_3D), position, color)
        self.points_3D.append(pt)

    def getPointsAs3DArray(self):
        return np.array([pt.position for pt in self.points_3D])

    def setPointsFrom3DArray(self, points3D):
        """
        Sets the internal stored 3D points to the values supplied to this function
        """
        assert points3D.shape == (len(self.points_3D), 3)
        for i in range(len(self.points_3D)):
            self.points_3D[i].position = points3D[i, :]
    
    # Print every points_3D
    def print3DPoints(self):
        open('reconstruction.p3d', 'w').close()
        for pt in self.points_3D:
            with open('reconstruction.p3d', 'a') as f:
                print(f'{pt.position[0]};{pt.position[1]};{pt.position[2]}', file=f)





class Track(object):
    def __init__(self, ):
        self.map = Map()
        self.cameras = []


    def processFrame(self, img, points_2D, K):
        # First Camera is set to the origin by definition
        # Other cameras are overwritten later
        cam = Camera(K=K, R=np.eye(3), t=np.array([0, 0, 0]), img=img, points_2D=points_2D)
        self.cameras.append(cam)
        cam_id = len(self.cameras) - 1

        colors = [(255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 128, 0)]

        # debug Bild
        # for i, point in enumerate(points_2D):
        #     cv2.circle(img, (int(point[0]), int(point[1])), 1, (255, 0, 0), -1)
        #     cv2.putText(img, str(i+1), (int(point[0]) + 10, int(point[1]) + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
        # cv2.imshow('debug', img)
        # cv2.waitKey(0)


        # Wenn es der erste Frame ist, können wir noch nichts tun
        if cam_id == 0:
            return

        if cam_id == 1:
            # get relative Pose from the current camera to reference camera
            E, mask = cv2.findEssentialMat(self.cameras[0].points_2D, self.cameras[cam_id].points_2D, cameraMatrix=K)
            inliers, R, t, mask = cv2.recoverPose(E, self.cameras[0].points_2D, self.cameras[cam_id].points_2D, cameraMatrix=K, mask=mask)
            print(f'recovered pose with {inliers} inliers')

            # https://docs.opencv.org/4.4.0/d9/d0c/group__calib3d.html
            # this matrix makes up a tuple that performs a change of basis from the first camera's coordinate system to the second camera's coordinate system.

            self.cameras[cam_id].setPose(R=R, t=t)
            # absolute_Rt = np.dot(self.cameras[cam_id].get_Pose(), self.cameras[ref_cam_id].get_Pose(square=True))
            # self.cameras[cam_id].set_Pose(absolute_Rt[:, :3], absolute_Rt[:, 3])

            points_3D = cv2.triangulatePoints(self.cameras[0].getP(), self.cameras[cam_id].getP(), self.cameras[0].points_2D.T, self.cameras[cam_id].points_2D.T).T
            points_3D /= points_3D[:, 3:]

            for i, p in enumerate(points_3D):
                # check points are in front of both cameras
                pl1 = np.dot(self.cameras[0].getP(), p)
                pl2 = np.dot(self.cameras[cam_id].getP(), p)
                if pl1[2] < 0 or pl2[2] < 0:
                    print('not in front', i)
                    continue

                # check reprojection error
                pp1 = (pl1[0:2] / pl1[2]) - self.cameras[0].points_2D[i]
                pp2 = (pl2[0:2] / pl2[2]) - self.cameras[cam_id].points_2D[i]
                pp1 = np.sum(pp1**2)
                pp2 = np.sum(pp2**2)
                # if pp1 > 2 or pp2 > 2:
                #     print(f'reproject error {pp1}, {pp2} for cone {names[i]}')

                # add the point
                if i < len(colors):
                    color = colors[i]
                else:
                    color = (100, 100, 100)
                # try:
                #     color = img[int(round(self.cameras[cam_id].points_2D[i, 1])), int(round(self.cameras[cam_id].points_2D[i, 0]))]
                # except IndexError:
                #     print('pixel ausserhalb des bildes')
                #     color = (255, 0, 0)

                self.map.addPoint(p[0:3], color)
        else:
            _, rvecs, tvecs, _ = cv2.solvePnPRansac(self.map.getPointsAs3DArray(), self.cameras[cam_id].points_2D, cameraMatrix=K, distCoeffs=None)
            R, _ = cv2.Rodrigues(rvecs)
            t = tvecs[:, 0]
            self.cameras[cam_id].setPose(R, t)

        if cam_id > 1:
            print(f'error before optimization: {self.calculateReprojectionError()}')
            err = self.optimize(fix_points=False)
            print(f'error after optimization: {self.calculateReprojectionError()}')
        
        # return 3DPoint of last point
        return self.map.getPointsAs3DArray()

    
    def optimize(self, local_window=LOCAL_WINDOW, fix_points=False, verbose=False, rounds=50):
        err = optimizeMap(self.cameras, self.map, local_window, fix_points, verbose, rounds)

        # # prune points
        # culled_pt_count = 0
        # for p in self.points:
        #     # <= 4 match point that's old
        #     old_point = len(p.frames) <= 4 and p.frames[-1].id+7 < self.max_frame

        #     # compute reprojection error
        #     errs = []
        #     for f,idx in zip(p.frames, p.idxs):
        #         uv = f.kps[idx]
        #         proj = np.dot(f.pose[:3], p.homogeneous())
        #         proj = proj[0:2] / proj[2]
        #         errs.append(np.linalg.norm(proj-uv))

        #     # cull
        #     if old_point or np.mean(errs) > CULLING_ERR_THRES:
        #         culled_pt_count += 1
        #         self.points.remove(p)
        #         p.delete()
        # print("Culled:   %d points" % (culled_pt_count))

        return err


    def calculateReprojectionError(self):
        err = 0.
        for i, p in enumerate(self.map.getPointsAs3DArray()):
            for c in self.cameras:
                pl1 = np.dot(c.getP(), np.append(p, 1.))
                pp1 = (pl1[0:2] / pl1[2]) - c.points_2D[i]
                err += np.sum(pp1**2)
        return err


    def reorientate(self):
        # move the yellow point to the origin
        points3D = self.map.getPointsAs3DArray()
        t_global = np.copy(points3D[0])
        points3D -= t_global

        R_global = rotation_matrix_from_vectors(points3D[1], np.array([1, 0, 0]))
        R_global_inv = np.linalg.inv(R_global)
        print(R_global)

        self.map.setPointsFrom3DArray(np.dot(R_global, points3D.T).T)

        for c in self.cameras:
            Rt = c.getPose()
            R = Rt[:3, :3]
            t = Rt[:3, 3]

            c.setPose(R=np.dot(R_global_inv, R), t=np.dot(R_global_inv, (t + t_global)))
    
    def printMap(self):
        self.map.print3DPoints()


