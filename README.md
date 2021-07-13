# Cone reconstruction

Heavily based on https://github.com/geohot/twitchslam


## Dev container setup

Open Folder inside [Dev Container](https://code.visualstudio.com/docs/remote/create-dev-container)
Access GUI at http://localhost:8080/vnc.html

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

# loop through cammera collection
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
