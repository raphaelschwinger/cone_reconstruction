import numpy as np
import OpenGL.GL as gl


# turn [[x,y]] -> [[x,y,1]]
def add_ones(x):
    if len(x.shape) == 1:
        return np.concatenate([x,np.array([1.0])], axis=0)
    else:
        return np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)


def normalize(Kinv, pts):
    return np.dot(Kinv, add_ones(pts).T).T[:, 0:2]



def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix


# pangolin helpers

#   void DrawLines(pybind11::array_t<double> points, pybind11::array_t<double> points2, float point_size=0) {
#       auto r = points.unchecked<2>();
#       auto r2 = points2.unchecked<2>();
#       glBegin(GL_LINES);
#       for (ssize_t i = 0; i < std::min(r.shape(0), r2.shape(0)); ++i) {
#           glVertex3d(r(i, 0), r(i, 1), r(i, 2));
#           glVertex3d(r2(i, 0), r2(i, 1), r2(i, 2));
#       }
#       glEnd();

#       if(point_size > 0) {
#           glPointSize(point_size);
#           glBegin(GL_POINTS);
#           for (ssize_t i = 0; i < std::min(r.shape(0), r2.shape(0)); ++i) {
#               glVertex3d(r(i, 0), r(i, 1), r(i, 2));
#               glVertex3d(r2(i, 0), r2(i, 1), r2(i, 2));
#           }
#           glEnd();
#       }
#   }

def DrawLines(points, points2, point_size=0):
    r = points
    r2 = points2
    gl.glLineWidth(10)
    gl.glColor3f(0.5, 0.6, 0.9)
    gl.glBegin(gl.GL_LINES)
    for i in range(r.shape[0], r2.shape[0]):
        gl.glVertex3d(r[i, 0], r[i, 1], r[i, 2])
        gl.glVertex3d(r2[i, 0], r2[i, 1], r2[i, 2])
    gl.glEnd()
    gl.glBegin(gl.GL_POINTS)
    for i in range(r.shape[0], r2.shape[0]):
        gl.glVertex3d(r[i, 0], r[i, 1], r[i, 2])
        gl.glVertex3d(r2[i, 0], r2[i, 1], r2[i, 2])
    gl.glEnd()