# open blender on mac os x with the path set to the current working directory
# see https://stackoverflow.com/questions/9859404/opening-blender-a-program-from-a-specific-filepath-relative-paths-unix-execu/9940691#9940691
import os
import subprocess

blenderPath = "/Applications/Blender.app/Contents/MacOS/Blender"

# For ubuntu: location of where Blender is installed. run 'which blender' command to find out. 

# blenderPath = "/snap/bin/blender" 

blenderFile = "ownTrack.blend"

path1 = "./"

os.chdir(path1)

subprocess.check_call([blenderPath, blenderFile])
