---
marp: true
---

<!-- backgroundColor: skyblue -->

# Master's Project: Deep Learning und Autonomous Racing

<!-- TODO: add names and lars and claudius names as tutors maybe? -->

---

<!-- paginate: true -->

# Project Overview:

<!-- TODO:
         * add a picture of the racetrack / racecar
         * Why SLAM here?
          -->

- About "Rosyard" project.

- The SLAM algorithm

- Race-track discription

---

# Introduction:

- This task of ground truth generation is divided into two subtasks.

  - A ground truth of the race track has to be generated.
  - The position of the car has to be recorded during a race.

- Possible methods
  <!-- TODO: I would suggest to mention Image based triangulation last and name it "Image based Triangulation" -->
  - **Image based Triangulation** : Taking the position of the cones and using 3D scene reconstruction using images/videos of the race-track.
  - UWB based Triangulation
  - LiDAR
  - Ultrasonic sensors
  - IMUs

---

<!-- ---TODO: we can probably leave that out -->

- **Environment Setup**
  - Dev Container:
  - Pypangolin version error fix description

---

# Reconstruction of the race-track using Blender :

<!-- TODO: we could demo our blender file here
            * add why we used blender-->

- **Blender**
  - Scene construcution
  - Getting cone position point using script
  <!-- TODO: I would mention the affine transformation after the reconstruction -->
- **Affine transformation**

---

# Tracking the racecar :

- **Tracking with openCV** :

  - Comparison of different Object detection algorithm from openCV and how we choose CSRT algorithm as the best one.
  <!-- TODO: add code, show tracker, maybe we can add a screencapture for this -->

  - Color Tracking
  <!-- TODO: we should demo the tracking -->

<!-- TODO:  * add slides to explain the 3d reconstuction: SLAM
            * mention and explain all imputs: 2D positions, calibration matrix, camera images
            * show code of important SLAM parts -->

---

<!-- TODO:  * make this an extra slide
            * explain transformation and show code and examples
            * and add the plots showing the after transformation -->

- **Results**

---

<!--TODO: add plot after normalization  -->

# Evaluation :

- Mean squard error

- MSE for "normalized" points

- Optimization error and plotted Graph

---

<!-- TODO:  * need to capture the whole scene at ones
            * highly sensitive to tracking errors
            * motion blur -> need fast shutter speed -->

# Project Limiations:

- Using only Blender generated scene.
- Accuracy and noise of the real world

---

<!-- TODO: * theoretial good enough (error in centimeter region) -->

# Conclusion :

- Future prospetcs
- Implementing the pipeline with the real-word images/video
