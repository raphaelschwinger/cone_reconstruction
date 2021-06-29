from multiprocessing import Process, Queue
from track_reconstruction.utils import DrawLines, DrawPoints, DrawCameras
import numpy as np
import OpenGL.GL as gl
import pypangolin as pangolin
from numpy.core.fromnumeric import squeeze
import pygame
from pygame.locals import DOUBLEBUF


class Display2D(object):
    def __init__(self, W, H):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H), DOUBLEBUF)
        self.surface = pygame.Surface(self.screen.get_size()).convert()

    def paint(self, img):
        # junk
        for event in pygame.event.get():
            pass

        # draw
        #pygame.surfarray.blit_array(self.surface, img.swapaxes(0,1)[:, :, [2,1,0]])

        # RGB, not BGR (might have to switch in twitchslam)
        pygame.surfarray.blit_array(
            self.surface, img.swapaxes(0, 1)[:, :, [0, 1, 2]])
        self.screen.blit(self.surface, (0, 0))

        # blit
        pygame.display.flip()


class Display3D(object):
    def __init__(self):
        self.state = None
        self.q = Queue()
        self.vp = Process(target=self.viewer_thread, args=(self.q,))
        self.vp.daemon = True
        self.vp.start()

    def viewer_thread(self, q):
        self.viewer_init(1024, 768)
        while not pangolin.ShouldQuit():
            self.viewer_refresh(q)

    def viewer_init(self, w, h):
        pangolin.CreateWindowAndBind('Map Viewer', w, h)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.scam = pangolin.OpenGlRenderState(
            pangolin.ProjectionMatrix(w, h, 420, 420, w//2, h//2, 0.2, 10000),
            pangolin.ModelViewLookAt(-2, 2, -2, 0, 0, 0, pangolin.AxisY))
        self.handler = pangolin.Handler3D(self.scam)

        # Create Interactive View in window
        self.dcam = pangolin.CreateDisplay()
        self.dcam.SetBounds(pangolin.Attach(0.0), pangolin.Attach(
            1.0), pangolin.Attach(0.0), pangolin.Attach(1.0), w/h)
        self.dcam.SetHandler(self.handler)
        # hack to avoid small Pangolin, no idea why it's *2
        self.dcam.Resize(pangolin.Viewport(0, 0, w*2, h*2))
        self.dcam.Activate()

    def viewer_refresh(self, q):
        while not q.empty():
            self.state = q.get()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.dcam.Activate(self.scam)

        # draw coordinate-System
        gl.glLineWidth(1)
        gl.glColor3f(1.0, 0.0, 0.0)
        DrawLines(np.array([[0, 0, 0]]), np.array([[1, 0, 0]]))
        gl.glColor3f(0.0, 1.0, 0.0)
        DrawLines(np.array([[0, 0, 0]]), np.array([[0, 1, 0]]))
        gl.glColor3f(0.0, 0.0, 1.0)
        DrawLines(np.array([[0, 0, 0]]), np.array([[0, 0, 1]]))

        if self.state is not None:
            if self.state[0].shape[0] >= 2:
                # draw poses
                gl.glColor3f(0.0, 1.0, 0.0)
                DrawCameras(self.state[0][:-1], 0.1)

            if self.state[0].shape[0] >= 1:
                # draw current pose as yellow
                gl.glColor3f(1.0, 1.0, 0.0)
                DrawCameras(self.state[0][-1:], 0.1)

            if self.state[1].shape[0] != 0:
                # draw keypoints
                gl.glPointSize(5)
                gl.glColor3f(1.0, 0.0, 0.0)
                DrawPoints(self.state[1], self.state[2])

        pangolin.FinishFrame()

    def paint(self, track):
        if self.q is None:
            return

        poses, pts, colors = [], [], []
        for c in track.cameras:
            # invert pose for display only
            poses.append(np.linalg.inv(c.getPose(square=True)))
        for p in track.map.points_3D:
            pts.append(p.position)
            colors.append(p.color)
        self.q.put((np.array(poses), np.array(pts), np.array(colors)/256.0))
