---
marp: true
---
<!-- backgroundColor: skyblue -->
# Master's Project: Deep Learning und Autonomous Racing


---
<!-- paginate: true -->

#  Project Overview:

- About  "Rosyard" project. 

- The SLAM algorithm

- Race-track discription

---

# Introduction:

- This task of ground truth generation is divided into two subtasks. 
  -  A ground truth of the race track has to be generated.  
  -  The position of the car has to be recorded during a race. 

- Taking the position of the cones and using 3D scene reconstruction using images/videos of the race-track. 

-  **Environment Setup**
     -  Dev Container:
     -  Pypangolin version error fix description

--- 
# Reconstruction of the race-track using Blender :

-  **Blender** 
   -  Scene construcution
   -  Getting cone position point using script
-  **Affine transformation**

---
# Tracking the racecar :

- **Tracking with openCV** :

    - Comparison of different Object detection algorithm from openCV and how we choose CSRT algorithm as the best one.
  
    - Color Tracking 

-  **Results**

---

# Evaluation :
-  Mean squard error

-  MSE for "normalized" points

-  Optimization error and plotted Graph 

---

# Project Limiations: 
   - Using only Blender generated scene.
   - Accuracy and noise of the real world 
---

# Conclusion :
   -  Future prospetcs 
   -  Implementing the pipeline with the real-word images/video