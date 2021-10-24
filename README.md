## README

Our source code is heavily based on https://github.com/geohot/twitchslam

### Dev container setup

We bundled all dependencies in a docker container as some dependencies are not available in binary form and the correct python version is necessary to be able to run the code. Take a look at the `Dockerfile` for more information.
With VSCode we are able to develop directly inside the container without any further setup, just install VS Code and Docker, clone this repository and click on "Open Folder inside [Dev Container](https://code.visualstudio.com/docs/remote/create-dev-container)". To access the graphical user interface you can use the VNC client accessible at `http://localhost:8080/vnc.html`.

### Install Dependencies and get rendered video files

To install python dependencies run

```bash
pip install -r ./requirements
```

The rendered image files are to big to version track (and its not a best practise), you can render them localy from in the script tab of the blender file. To open the Blenderfile you can use the `openBlender.py` script inside a blender directory.

### Run Reconstruction

The main python script to start the reconstruction is `run_reconstruction.py`. As a parameter it expects a foldername.
In this folder the following things should be present:

- set correct camera focal length in lines 76, take a look at the related blender script to retrieve the correct value
- a `.png` file containing the first frame for every camera, named `01.png` respectivly
- a `.p2d` file containing the 2D points of the cones for every camera, named `01.p2d` respectivly
- a folder called `frames` containing folders for every frame, in each of those:
  - `.p2d` file representing the 2D coordinates of the car for every camera, named `01.p2d` respectivly

```bash
python run_reconstruction.py blender-racetrack
```

As a result the reconstructed 3D points of the car and the cones are saved in the files `car_reconstruction.p3d` and `cone_reconstruction.p3d`. Those coordinates are in relation to the first camera so they need to be transformed to be human readable.

### Transform points

To transform the reconstructed points back to the coordinate system set in blender use the steps:

- write the coordinates of the first 4 points in `cone_reconstruction.p3d` in a file named `known_points`, take care that the first points are not in one plane

```bash
python transform.py blender-racetrack
```

A affine transformation matrix is calculated and applied to the points in `cone_reconstruction.p3d` and saved in `cone_transformation.p3d`.

### Blender

We use [Blender](https://www.blender.org/) to generate test images for reconstruction.
For this task Blender can be scripted with the help of python. Scripts are bundled inside the `.blender` file and can be executed from within the "Scripting" tab.

To start blender with the current directory set use the [script](https://stackoverflow.com/questions/9859404/opening-blender-a-program-from-a-specific-filepath-relative-paths-unix-execu/9940691#9940691) `openBlender` inside the cone-track folder.

### Miscs

* in `utlis.py` we implemented some functions of (pypangolin)[https://github.com/uoip/pangolin] to avoid using this outdated library

## Project Overview

Autonomous racing is an emerging field within autonomous driving. A few self-racing vehicles have been developed in the last years, both in industrial and academic research. The first known autonomous vehicle competition [[1]](#1) was the DARPA Grand Challenge.

Formula Student Germany organized the first autonomous racing competition in 2017, followed by other countries in 2018. Formula Student (FS) is an international engineering competition where multidisciplinary student teams compete with a self-developed racecar every year.

The main race consists of completing ten laps, as fast as possible, around an unknown track defined by small 228 × 335 mm cones. Blue and yellow cones distinguish the left and the right boundary. The track is a 500m long closed circuit, with a width of 3m, and the cones in the same boundary can be up to 5m apart. The track contains straights, hairpins, chicanes, multiple turns and decreasing radius turns. [[2]](#2)

The master project "Ground Truth Generation"  is a part of the "Rosyard" project to implement a self-driving car for the Formula Student Competition. [[3]](#3)


In order to make the vehicle race fully autonomous, the car uses two modes of operation, Simultaneous Localization and Mapping (SLAM) mode, and Localization mode. [[4]](#4)

- In SLAM mode, the vehicle path has to be computed using the local perception sensors, and a map of the track has to be generated.
- In Localization mode, the goal is to race as fast as possible in an already mapped track.
  
As previously stated, the track is marked with cones, and only cones are considered landmarks, and other potential features are rejected. Cameras detect Cones that mark the racetrack to create a reconstruction of the racetrack.

The objective of our project is to design an algorithm that calculates the corresponding ground truth of the racing environment. With the help of the results of this master project in a test race the SLAM algorithm can then be evaluated and optimized.

This task of ground truth generation for the SLAM algorithm is divided into two subtasks.  

- First, a ground truth of the race track has to be generated.  
- Second, the position of the car has to be recorded during a race.

In order to define the ground truth of the race track, it is therefore sufficient to determine the positions of these cones. 
Once the ground truth is generated, the car can drive in Localization Mode, exploiting the advantage of additional knowledge of the mapped racetrack.

---

### Possible methods

During the project's planning phase, we discussed many ideas that could be used to generate the ground truth of the racecars movement and the track.

- **LiDAR** : LiDAR is the most accurate compared to the other devices, but it is also the most expensive one. Since the budget was one of our limitations, we discarded the idea.
- **GPS** : Commercially available GPSs are highly accurate, but they are also expensive to get.

- **UWB based Triangulation** : After the release of apple AirTag, we were motivated to discuss the possibility of UWB technology. We discussed using UWB to triangulate the car's position, but we do not have enough technical knowledge and expertise with UWB to implement the ideas.
  
- **Image-based 3D Reconstruction** : We can use multiple cameras to record the racecar racing around the racetrack and get the position of cones and the car. After that, we can make a 3D scene reconstruction scene using the data we collected.

We decided to use  3D scene reconstruction using images/videos of the race track since we thought that might be the cheapest way and also scientifically the most interesting one.

---
### 3D Scene Reconstruction
<p align="center">
    <img src="presentation/ComputerVision-682.png"   width="300" alt>
    <em>Fig: Camera matrix</em>
</p>

To reconstruct the position of both cones and the racecar we used a approach called `Structure from Motion`, thereby we were able to simultaneously recover the 3D structure of the racetrack and the poses of the used cameras. As an input only the image coordinates of the cones and the racecar and the camera intrinsics need to be provided. The later consists in particular of the set focal length and the set resolution.

First, the first camera is set as the origin. The task is now to acquire the pose and position of the consecutive cameras to be able to triangulate the position of the cones and racecar as illustrated in the figure above. So we need to obtain the translation $t$ and rotation $R$ of the second camera in relation to the first camera. This can be calculated with the `essential matrix` $E = [t]_x R$. OpenCV provides the following functions that need the 2D input points of both cameras and the camera intrinsics as an input.

```python
  E = cv2.findEssentialMat(points_2D_1, points_2D_2, cameraMatrix )
  R, t = cv2.recoverPose(E, points_2D_1, points2D_2, cameraMatrix)
```

Afterwards the 3D coordinates of the cones and the racecar can be triangulated.[[8]](#8)

```python
   points3D = cv2.triangulatePoints(pose_1, pose_2, points1, points2)
```

For consecutive cameras $R$ and $t$ can be recovered with Random sample consensus `RANSAC` algorithm and the `Rodrigues algorithm` using the already estimated 3D points.

```python
rvecs, t = cv2.solvePnPRansac(points_3D, points_2D, cameraMatrix)
R = cv2.Rodrigues(rvecs)
```

These informations is needed to further improve the 3D points with bundle adjustment. For this purpose we included the `g2o` library.
This results in a list of 3D coordinates of the cones and the position of the racecar in the first frame of the video. To reconstruct the position of the racecar while in motion we repeated the steps for every frame of the video. The figure below shows our initial visualisation of the result for the first frame.


<p align="center">
    <img src="./presentation/reconstructed_racetrack.png"  width="300">
    <em>Fig: Blender Reconstruction</em>
</p>



### Affine transformation

At first glance the result looks like the real racetrack. If we take a closer look at the 3D coordinates of the reconstructed cone points we see that the points are not in the position as expected. That is because the 3D points are in relation to the first camera that is set as the origin of the coordinate system. That means the points need to be translated, rotated and in particular scaled to match the "real world". Transforming the points in all three ways is called an `affine transformation` and can be applied by multiplying every 3D point with a `affine transformation matrix`. This matrix can be estimated with the knowledge of a correct mapping of 4 points, therefore it is necessary to measure the position from at least 4 cones. Thereby it is important that all 4 positions are not on the same plane to be able to transform 3D points that do not lie on this plane. The figures below show the initial recovered 3D coordinates of the first four cones and the 3D coordinates after applying the affine transformation and matching the expected 3D coordinates. [[9]](#9)


```python
    mat = cv2.estimateAffine3D(points_3D[:4], known_points_3d)
    #  [[ 10.19  45.79  -1.93  3.93]
    #   [ 0.26  -100.2  13.86 -18.66]
    #   [ 0.00   0.00   0.00   0.15]]
```

<div style="page-break-after: always;"></div>

## Reconstruction of the race-track using blender

  As mentioned above, to apply our 3D scene reconstruction algorithm we need video files of the car racing around the track filmed from at least 3 angles. Then we need to acquire the car's and cones 2D position for each frame. However, because of Covid-19, it was not possible to make a real-world racing scenario and record  racing videos of the car. So we had to improvise and work on a simulated racing environment which we created on Blender. This gives us also the benefit of directly exporting the 2D coordinates for each frame of the video. Additionally we do not need to worry about any noise in the video files as the cameras in blender are not suffering from physical constraints.

#### Blender environmental elements
  - **Camera**: We set the height of the camera as 1.5 m and focal length to 15 mm. We used a python script for camera calibration which is included in README. The video we exported has a resolution of 4k.
  - **Car**: We used a realistic Rosyard car model with height of 0.90 m , width 1.15 and length 2.45 m.  
  
<p align="center">
  <img src="blender-car.jpeg"  width="300">
  <em>Fig: Blender Car Model</em>
</p>

  - **Track**: To mark the track, we used yellow and blue cones with a height of 0.15 m. We made a circular racetrack with 48 cones.  We added asphalt texture on the ground to make the racetrack look like a real racetrack. Also to make the environment look more realistic, we used a "skydome" to make it look like a sky on the horizon. 


<p style="display: table; align: center">
  <img style="float: left" src="blender-racetrack-1.jpeg"  width="320">
  <img style="float: left"src="blender-racetrack-2.jpeg"  width="320">

  <em>Fig: Circular Racetrack</em>
</p>
  
## Tracking the racecar

Since we can not export the 2D image coordinates from Blender in the real world we need to acquire them differently. For the cones this task can be done manually as since the cameras and cones do not move that needs to be done for only for the first frame. Also the previous group did some research in that area to automate this task and had no satisfying results as not only the cones need to be detected but also correctly mapped from all angles. To get the 2D position of the racecar we tried multiple tracking algorithms. Details and background of the algorithms are included below:



- **OpenCV Tracking Algorithm** :
  - **KCF** [[5]](#5): 
     Kernelized Correlation Filter (KCF) is a novel tracking framework, and it is one of the recent findings which has shown promising results. KCF is based on the idea of the traditional correlational filter. It uses kernel trick and circulant matrices to improve the computation speed significantly.

  - **CSRT** [[6]](#6): 
    Channel and Spatial Reliability Tracking is a constrained filter learning with an arbitrary spatial reliability map. It utilizes a spatial reliability map. CSRT adjusts the filter support to the part of the object suitable for tracking.

  - **GOTRUN** [[7]](#7):
    Generic Object Tracking Using Regression Networks (GOTRUN) is a Deep Learning based tracking algorithm. GOTRUN is significantly faster than previous methods that use neural networks for tracking. The tracker uses a simple feed-forward network without any online training, and it can track generic objects at 100 fps. 

After testing the tracking algorithms extensively we found out that `CSRT` performed best on our generated video files. Since even the results of `CSRT` were not very convincing and we could not get any real world data where further optimization would be required anyway we tried tracking a color object. Therefore we colored ether the whole car red or added a red-colored cylinder on top of the racecar to make the tracking even more accurate. Then we only had to apply a color filter of the image and retrieve the 2D coordinates of the center of the filtered portion. 

<div style="page-break-after: always;"></div>

## Results

We ran our 3D scene reconstruction algorithm with the tracking results of the `blender-position` script, the `CSRT-tracker`,the `color-tacker` tracking the whole car and tracking only a `red-cylinder` on top of the car. To better compare the results we than aligned the starting positions of the racecar. The result is shown in the figure below.

<p align="center">
  <img src="./presentation/normalized.png"  width="600">
  <em>Fig: 2D plot of reconstruction</em>
</p>

As we can see the reconstruction using the `blender-position` is performing very well. Also the `reconstructed cones` are very close to the original cones. `CSRT-tracker` is way off from the `real position` of the racecar and is jumping around a lot. `color-tracker` and `red-cylinder` are able to follow the racecar and almost recover a position of the racecar between the cones all the way around the racetrack.

As shown in the next figure the mean squared error confirms those findings. We did not include the high error of `CSRT-tracker` which is `160.54` in the graphic.  
<p align="center">
  <img src="./presentation/mse2.png"  width="600">
  <em>Fig: mean squared error</em>
</p>

We found a correlation between the optimization error returned by the `g2o` optimizer and substituted those points. Also we applied a convolution filter to smoothen the result as you can see in the figure below. This did not improve the mean squared error tough. For more details take a look at the jupiter notebook `notebook.ipynb` we used to analyse the reconstruction results.

<p align="center">
  <img src="./presentation/smoothend_plot.png"  width="600">
  <em>Fig: smoothened  2D plot</em>
</p>

<div style="page-break-after: always;"></div>

## Real World Guide

1. Set at least 3 cameras which all cover the whole track
2. Get calibration matrix of camera (depends on set focal length)
2. Measure the locations of at least 4 objects which are not on one plane
3. Film racecar with static cameras (fast shutter speed -> no motion blur)
4. Extract first frame from all cameras and annotate cone position (like previous group)
5. Track car in videos to extract 2D position of car
6. Perform 3D Scene Reconstruction run_reconstruction
7. Transform result with affine transformation and the "correct" location of the 4 known objects

## Conclusion

We where able to reconstruct a racetrack and a car driving around the racetrack by applying a 3D scene reconstruction algorithm. We can see that with "perfect" 2D input points as we get them from blender accuracy around $~10cm$ is possible. Therefore our method is in theory suitable to improve the SLAM algorithm driving the car. We experienced that the 3D reconstruction result is highly dependent on valid 2D input points as slight noise results in a high error. That is why precise tracking is important. Also, as our input data is generated by Blender we do not suffer from noise and are using a optically camera with out any distortion or optically imperfections. In the real world those effects will have a negative impact on the accuracy of the reconstruction.

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

### Script to output rendered animation video

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

### Get car 3D position from blenders

```python
import os
import bpy

file_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.dirname(file_path)
#path = os.path.split(os.getcwd())[0]

scene = bpy.context.scene

# needed to rescale 2d coordinates
# needed to rescale 2d coordinates
render = scene.render

car_path = os.path.join(path, 'car_position.p3d')

# erease content of .p2d file
open(car_path, 'w').close()

for f in range(scene.frame_start, scene.frame_end + 1, scene.frame_step):
    # go to frame f
    scene.frame_set(f)

    car = bpy.data.objects['whole_car']
    # get 3d coordinates of cone
    location = car.location.copy()
    with open(car_path, 'a') as file:
        print(f'{round(location[0], 3)};{round(location[1], 3)};{round(location[2], 3)}', file=file)
```

### Get cone position from blenders

```python
import os
import bpy

file_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.dirname(file_path)
#path = os.path.split(os.getcwd())[0]

scene = bpy.context.scene

# needed to rescale 2d coordinates
# needed to rescale 2d coordinates
render = scene.render

cone_path = os.path.join(path, 'cone_position.p3d')

# erease content of .p2d file
open(cone_path, 'w').close()
coneCollection = bpy.data.collections['Cones']
for cone in coneCollection.objects:
    # get 3d coordinates of cone
    location = cone.location.copy()
    with open(cone_path, 'a') as file:
        print(f'{round(location[0], 3)};{round(location[1], 3)};{round(location[2], 3)}', file=file)
```
