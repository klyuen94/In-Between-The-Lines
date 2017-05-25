---
layout: default
title: Status
---
**Project Summary: **
The project consists of a line runner implemented in the environment of minecraft. This means that there will be a straight line course that will be populated with obstacles that the agent has to navigate through skillfully. The agent will be required to completely avoid the obstacles or else it will die and the game will end. The method in which we are going about this is through visual computing. A learner will be trained to recognize obstacles using linear regression for classification. The training data will consist of snapshots of the world generated through the malmo API while the target data will consist of actions to be executed by the agent to avoid the obstacles. Through the use of a linear regression classifer, the agent will be able to consistently recognize the field with its respective obstacles. Additionally, levels of various difficulty will be generated as the agent completes the run. The obstacles will be randomly generated to the respective level of difficulty. 

**Approach: **
We will be conducting visual computation through a linear regression classifier to implement object recognition in our agent. This was the approach of our choice because traditional object recognition methods would have a difficult time in a world populated solely by squares. We will be implementing computer vision to allow the agent to see the incoming obstacles and compute the appropriate actions (moving left, right, or continue forward). In order to achieve this, we will be training our learner by sending it a data set of images and calculating the necessary features using opencv.
As of right now, we are using a q table to have the agent learn which moves are best to take based on the observation of the incoming obstacles through the grid. The agent learns to make the appropriate move by having a highly negative reward for running into an obstacle. In order to ensure that the agent is running properly, it will be tested against the oracle.
As for the linear regression model we plan to use, we have not yet completed the implementation, but the equation would have a structure similar to this:
Y = B0 + B1*x
Once the data set is generated, we will update this equation with the appropriate values used for the coefficients of B0 and B1. When the coefficient becomes zero, the influence of the input variable will be effectively removed. 

**Evaluation: **
We will have two metrics to score the agent: the error rate of object recognition done by the computer vision through a linear regression classifier and the ability of the agent to succeed by finishing the course in optimal time. 
We will have a standard set of obstacles generated randomly throughout the course, with the more intricate and tough combinations based on the level of difficulty. By having the same sets of obstacles generated at different spots of the map, we can evaluate the obstacle recognition of the agent before it runs the course and determine how well the agent was able to associate a certain action given the obstacles it encounters. In order to do so, we trained a data set by generating continuous screenshots of the map as the agent the agent runs. Below are screenshots of what the agent sees and what we will be using to generate data. 
[[https://github.com/klyuen94/In-Between-The-Lines/blob/master/docs/B%26W_shot.png|alt=octocat]]
[[https://github.com/klyuen94/In-Between-The-Lines/blob/master/docs/normalshot.png|alt=octocat]]

With this learner, the agent is able to recognize all the different states of obstacles it encounters. Thus, we are able to evaluate the learner qualitatively by its ability to run smoothly without directly coming contact with the obstacle. 
The second metric we use to evaluate the agent is its ability to complete the course in optimal time. Despite the agent being able to recognize the different states it encounters and complete the course, it does not necessarily result in the optimal path. In order to verify the agent is taking the best possible path, the levels will be timed. If the agent takes unnecessary steps to the left or right, it will be noted in the resulting time. 

**Remaining Goals and Challenges: **
When we first began this project, we planned on implementing computer vision into the agent to visually recognize the map. However, we were unsure of where to begin due to lack of complete understanding of computer vision. Thus, we began by creating the course by scratch and adding obstacles/lava to increase the difficulty level. We then decided to implement a q table as a foundation for the agent to arbitrarily learn on something. We chose to use an oracle to have something to test the agent against. It turns out that the q table is not part of our final plans, and we will be moving forward with computer vision along with the oracle we have created. Our goal for when the final report is due is to fully develop the computer vision and train our agent through linear regression. Given that we initially chose to start with the q table, we were unable to implement the computer vision and linear regression classifier by the first progress report. However, we are now in the process of developing the computer vision aspect of our project, which is the main focus for the coming weeks. Specifically, we will be gathering data from screenshots, which will be taken continuously throughout the countless different practice runs. This is to ensure there is a competent enough data set for us to train the learner on. 
Moving forward, we anticipate facing a few challenges in the development of computer vision. Specifically, we are still in the process of taking screenshots of the environment while the agent is running continuously, in addition to accurately training the data to provide an accurate learner for the agent. In order to solve this problem, we plan to thoroughly explore open cv, external libraries, and other possible applications of taking screenshots in the code, all while testing our agent against our oracle.





