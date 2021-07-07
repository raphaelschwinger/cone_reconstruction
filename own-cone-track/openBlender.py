import os
import subprocess

blenderPath = "/Applications/Blender.app/Contents/MacOS/Blender"

path1 = "./"

os.chdir(path1)

subprocess.check_call([blenderPath, "ownTrack.blend"])
