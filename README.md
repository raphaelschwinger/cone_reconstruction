# Cone reconstruction

Heavily based on https://github.com/geohot/twitchslam


## Dev container setup

Open Folder inside [Dev Container](https://code.visualstudio.com/docs/remote/create-dev-container)
Access GUI at http://localhost:8080/vnc.html

## Blender

We use [Blender](https://www.blender.org/) to generate test images for reconstruction.
For this task Blender can be scripted with the help of python. Scripts are bundled inside the `.blender` file and can be executed from within the "Scripting" tab.

To start blender with the current directory set use the [script](https://stackoverflow.com/questions/9859404/opening-blender-a-program-from-a-specific-filepath-relative-paths-unix-execu/9940691#9940691) `openBlender` inside the cone-track folder.

