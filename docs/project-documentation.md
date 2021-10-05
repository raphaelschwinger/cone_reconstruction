# Masterproject Deep Learning und Autonomous Racing

Race car tracking

Sommersemester 2021

Rakibuzzaman Mahmud
Raphael Schwinger


## Project Overview



- The master project "Ground Truth Generation"  is a part of the "Rosyard" project. 

- The SLAM algorithm will use the results of the master project to optimize the car by getting an accurate ground truth of the track and the car's position during a test race.

- This task of ground truth generation for the SLAM algorithm is divided into two subtasks. First, a ground truth of the race track has to be generated.  Second, the position of the car has to be recorded during a race. 


- A race track of Rosyard usually roughly covers 50 x 150 meters and is marked by two rows of cones placed parallel to each other. The cones are placed at intervals of 5 meters lengthwise to the direction of travel, the width of the track is about 3 meters, and a cone has a height of 32 cm. 

- In order to define the ground truth of the race track, it is therefore sufficient to determine the positions of these cones. We will use  3D scene reconstruction using images/videos of the race track. 



## Introduction

TODO:
- [ ] introduce Raceyard project
- [ ] introduce problem, why does car needs to be tracked
- [ ] discussion on what methods could be used
- [ ] what did the premilary group

## Reconstruction of the racetrack

TODO:
- [ ] Structure from motion
- [ ] Blender, why?
- [ ] transforming output to "real world" with affine transformation

## Tracking the racecar

TODO:
- [ ] Picture information from blender
- [ ] Tracking with openCV :

    - Comparison of different Object detection algorithm from openCV and how we choose CSRT algorithm as the best one.
- [ ] exact tracking? #25
- [ ] results #26

## Miscs


* [ ] Dev Container: Our implementation depends on various software packages in different versions, that's why we worke on a Docker dev container. Descirption of how we used dev container to manage our virtualbox.

* [ ] Pypangolin version error fix description


## README

TODO:
* [ ] how to run

