---
layout: default
title: 	Proposal
---

**Summary:**
The project will consist of a line runner implemented in minecraft. This means that there will be a course that will be populated with obstacles that the agent has to navigate through. The way we are going to do this by using visual computing. We will train a learner to recognize obstacles using a neural network for classification. The training data will consist of snapshots of the world generated through the malmo API and the target data will consist of actions to be executed by the agent to avoid the obstacles. 

**AI/ML Algorithms:** 
	We will be using a neural network to do object recognition in minecraft. We chose this approach because traditional object recognition methods would have a difficult time in a world populated solely by squares. For example, using a HOG to create a template would be troublesome since many of the items in the world are squares. So there would be no way of distinguishing a cactus vs a block of wood. 

**Evaluation Plan:**
	We will have two metrics to score the agent: One would be the error rate of object recognition done by the neural network the other metric will be the distance that the agent traverses through the course. We will have a standard set of obstacles which the agent will have to recognize and associate with an action in order to traverse the course. This way we can evaluate the obstacle recognition before the agent actually runs the course and then get insight on how well the agent learned to associate an object with a certain action. If the agent makes it to the end of the course then we can determine if the agent has a low recognition error or hasn’t learned to properly use the right actions with the right obstacles. Since the moving forward will not be controlled by the agent, the baseline will not necessarily be zero, but whatever the score distance to the first obstacle is, most likely about 3 seconds. Ideally, the agent will be able to complete any combination of the standard obstacles, but since we be creating the course ourselves, we expect it to be able to complete whatever we create. 
	Qualitatively, we expect our agent to move efficiently and smoothly, it will be interesting to see if by training our agent to stay without the bounds of the course, it chooses to run in a straight line or if it constantly turns. We may have to create specific training courses for behavior such as a long straight line to teach it to stay within bounds. Our moonshot goal is to have a AI that can efficiently navigate any course we make for as long as we can make it. If we could train it to recognize obstacles in general using our standard set, it would be quite cool.
  	

**Meeting Time:**
03:45 pm - Tuesday, April 25, 2017
