# Cone reconstruction

Heavily based on https://github.com/geohot/twitchslam


## Dev container setup

Open Folder inside [Dev Container](https://code.visualstudio.com/docs/remote/create-dev-container)
Access GUI at http://localhost:8080/vnc.html

## Install Dependencies and get rendered video files

To install python dependencies run 
```bash
pip install -r ./requirements
```

The rendered image files are to big to version track (and its not a best practise), you can render them localy from in the script tab of the blender file. To open the Blenderfile you can use the `openBlender.py` script inside a blender directory.

## Run Reconstruction

The main python script to start the reconstruction is `run_reconstruction.py`. As a parameter it expects a foldername.
In this folder the following things should be present:
- a `.png` file containing the first frame for every camera, named `01.png` respectivly
- a `.p2d` file containing the 2D points of the cones for every camera, named `01.p2d` respectivly
- a folder called `frames` containing folders for every frame, in each of those:
    -  `.p2d` file representing the 2D coordinates of the car for every camera, named `01.p2d` respectivly

```bash
python run_reconstruction.py blender-racetrack
```

As a result the reconstructed 3D points of the car and the cones are saved in the files `car_reconstruction.p3d` and `cone_reconstruction.p3d`. Those coordinates are in relation to the first camera so they need to be transformed to be human readable.

## Transform points

To transform the reconstructed points back to the coordinate system set in blender use the steps:
* write the coordinates of the first 4 points in `cone_reconstruction.p3d` in a file named `known_points`

```bash
python transform.py blender-racetrack
```

A affine transformation matrix is calculated and applied to the points in `cone_reconstruction.p3d` and saved in `cone_transformation.p3d`.



## Blender

We use [Blender](https://www.blender.org/) to generate test images for reconstruction.
For this task Blender can be scripted with the help of python. Scripts are bundled inside the `.blender` file and can be executed from within the "Scripting" tab.

To start blender with the current directory set use the [script](https://stackoverflow.com/questions/9859404/opening-blender-a-program-from-a-specific-filepath-relative-paths-unix-execu/9940691#9940691) `openBlender` inside the cone-track folder.

### Script to save images and cone tip coordinates in `.p2d`

```python
import bpy
import bpy_extras

scene = bpy.context.scene

# needed to rescale 2d coordinates
render = scene.render
res_x = render.resolution_x
res_y = render.resolution_y



# render cameras and save images

# loop through camera collection
cameraCollection = bpy.data.collections['Cameras']
for camera in cameraCollection.objects:
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = './' + camera.name
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.ops.render.render(use_viewport=False, write_still=True)
    
    # erease content of .p2d file
    open(camera.name + '.p2d', 'w').close()

    # iterate through cones
    coneCollection = bpy.data.collections['Cones']
    for cone in coneCollection.objects:
        # get 3d coordinates of cone
        location = cone.location.copy()
        # location is the bottom of a cone and not the tip, the cone is 25cm high
        location[2] = cone.location[2] + 0.25
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, location)
        # If you want pixel coords
        render_scale = scene.render.resolution_percentage / 100
        render_size = (
                int(scene.render.resolution_x * render_scale),
                int(scene.render.resolution_y * render_scale),
                    )
        with open(camera.name + '.p2d', 'a') as f:
            print(f'{co_2d.x * render_size[0]} {res_y - co_2d.y * render_size[1]}', file=f)
```

### Script to output renderd animation video

```python
import bpy
import bpy_extras

scene = bpy.context.scene

# needed to rescale 2d coordinates
render = scene.render
res_x = render.resolution_x
res_y = render.resolution_y

print('test')

# render cameras and save images

# loop through camera collection
cameraCollection = bpy.data.collections['Cameras']
for camera in cameraCollection.objects:
    print(camera.name)
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = './' + camera.name + '-video'
    bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
    bpy.ops.render.render(animation=True, use_viewport=False)
```

### Script to get camera_matrix from blende

See [Stack Exchange Answer](https://blender.stackexchange.com/a/120063)

```python
import bpy
from mathutils import Matrix, Vector

#---------------------------------------------------------------
# 3x4 P matrix from Blender camera
#---------------------------------------------------------------

# BKE_camera_sensor_size
def get_sensor_size(sensor_fit, sensor_x, sensor_y):
    if sensor_fit == 'VERTICAL':
        return sensor_y
    return sensor_x

# BKE_camera_sensor_fit
def get_sensor_fit(sensor_fit, size_x, size_y):
    if sensor_fit == 'AUTO':
        if size_x >= size_y:
            return 'HORIZONTAL'
        else:
            return 'VERTICAL'
    return sensor_fit

# Build intrinsic camera parameters from Blender camera data
#
# See notes on this in 
# blender.stackexchange.com/questions/15102/what-is-blenders-camera-projection-matrix-model
# as well as
# https://blender.stackexchange.com/a/120063/3581
def get_calibration_matrix_K_from_blender(camd):
    if camd.type != 'PERSP':
        raise ValueError('Non-perspective cameras not supported')
    scene = bpy.context.scene
    f_in_mm = camd.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size(camd.sensor_fit, camd.sensor_width, camd.sensor_height)
    sensor_fit = get_sensor_fit(
        camd.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camd.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camd.shift_y * view_fac_in_px / pixel_aspect_ratio
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((s_u, skew, u_0),
        (   0,  s_v, v_0),
        (   0,    0,   1)))
    return K

# Returns camera rotation and translation matrices from Blender.
# 
# There are 3 coordinate systems involved:
#    1. The World coordinates: "world"
#       - right-handed
#    2. The Blender camera coordinates: "bcam"
#       - x is horizontal
#       - y is up
#       - right-handed: negative z look-at direction
#    3. The desired computer vision camera coordinates: "cv"
#       - x is horizontal
#       - y is down (to align to the actual pixel coordinates 
#         used in digital images)
#       - right-handed: positive z look-at direction
def get_3x4_RT_matrix_from_blender(cam):
    # bcam stands for blender camera
    R_bcam2cv = Matrix(
        ((1, 0,  0),
        (0, -1, 0),
        (0, 0, -1)))

    # Transpose since the rotation is object rotation, 
    # and we want coordinate rotation
    # R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # T_world2bcam = -1*R_world2bcam @ location
    #
    # Use matrix_world instead to account for all constraints
    location, rotation = cam.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # T_world2bcam = -1*R_world2bcam @ cam.location
    # Use location from matrix_world to account for constraints:     
    T_world2bcam = -1*R_world2bcam @ location

    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv@R_world2bcam
    T_world2cv = R_bcam2cv@T_world2bcam

    # put into 3x4 matrix
    RT = Matrix((
        R_world2cv[0][:] + (T_world2cv[0],),
        R_world2cv[1][:] + (T_world2cv[1],),
        R_world2cv[2][:] + (T_world2cv[2],)
        ))
    return RT

def get_3x4_P_matrix_from_blender(cam):
    K = get_calibration_matrix_K_from_blender(cam.data)
    RT = get_3x4_RT_matrix_from_blender(cam)
    return K@RT, K, RT

# ----------------------------------------------------------
if __name__ == "__main__":
    # Insert your camera name here
    cam = bpy.data.objects['Camera']
    P, K, RT = get_3x4_P_matrix_from_blender(cam)
    print("K")
    print(K)
    print("RT")
    print(RT)
    print("P")
    print(P)

    print("==== 3D Cursor projection ====")
    pc = P @ bpy.context.scene.cursor.location
    pc /= pc[2]
    print("Projected cursor location")
    print(pc)

    # Bonus code: save the 3x4 P matrix into a plain text file
    # Don't forget to import numpy for this
    #nP = numpy.matrix(P)
    #numpy.savetxt("/tmp/P3x4.txt", nP)  # to select precision, use e.g. fmt='%.2f'
```

### Car position data from blender

```python
file_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.dirname(file_path)
#path = os.path.split(os.getcwd())[0]
frame_dir_path = os.path.join(path, 'frames') 

scene = bpy.context.scene

# needed to rescale 2d coordinates
# needed to rescale 2d coordinates
render = scene.render
res_x = render.resolution_x
res_y = render.resolution_y

for f in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):
    current_frame_path = os.path.join(frame_dir_path,str(f).zfill(4))
    os.makedirs(current_frame_path, exist_ok=True)

    # go to frame f
    scene.frame_set(f)

    # render cameras and save images

    # loop through cammera collection
    cameraCollection = bpy.data.collections['Cameras']
    for camera in cameraCollection.objects:
        bpy.context.scene.camera = camera
        bpy.context.scene.render.filepath = './frames/' + str(f).zfill(4) + '/' + camera.name
        bpy.context.scene.render.image_settings.file_format='PNG'
        bpy.ops.render.render(use_viewport=False, write_still=False)

        # erease content of .p2d file
        open(os.path.join(current_frame_path, camera.name +  '.p2d'), 'w').close()

        # iterate through cones
        car = bpy.data.objects['whole_car']
        # get 3d coordinates of cone
        location = car.location.copy()
        # location is the bottom of a cone and not the tip, the cone is 25cm high
        location[2] = car.location[2]
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, location)
        # If you want pixel coords
        render_scale = scene.render.resolution_percentage / 100
        render_size = (
                int(scene.render.resolution_x * render_scale),
                int(scene.render.resolution_y * render_scale),
                    )
        with open(os.path.join(current_frame_path, camera.name +  '.p2d'), 'a') as file:
            print(f'{co_2d.x * render_size[0]} {res_y - co_2d.y * render_size[1]}', file=file)
```