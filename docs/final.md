---
layout: default
title: Final Report
---

Project Summary: The project consists of a line runner implemented in the environment of minecraft. This means that there will be a straight line course that will be populated with obstacles that the agent has to navigate through skillfully. The agent will be required to completely avoid the obstacles or else the game will end. The method in which we are going about this is through visual learning. The training data will consist of snapshots of the world generated through an agent with complete course knowledge using a path finding algorithm while the target data will consist of the actions to be executed by this agent to avoid the obstacles. Through the use of a decision tree classifier, the agent will be able to consistently recognize the field with its respective obstacles by using edge detection to generalize obstacles. Additionally, levels of various difficulty will be generated as the agent completes the run, some of which will be randomly generated to the respective level of difficulty.

Below is an image of the three different levels we created in a birds eye view. The first level is where the glowstones are most populate but remain constant, the second is where the glowstones are less populated but more random, and the final level is where there is a full row of glowstones with only one opening (only one accurate move available) every 15 steps.
![levels](https://user-images.githubusercontent.com/27802382/27006751-6fd20e0a-4df1-11e7-819c-8b929e2ee7ad.png)
 
 
Approaches: On our project we created several agents in the process of developing our visual agent. The agents are as follows: random, Q-learning, A*, and finally our working visual agent. 
	
Random Agent: This agent is our baseline and simply works by choosing one of the 3 directions with a .33 random probability of choosing each move. Beyond that, it chooses not to run into the walls of the level that end the game, but will happily run into the normal obstacles. This is our worst agent and is only used to compare against the other agents that we implemented. It serves to prove that our other agents are acting intelligently rather than just being random behavior.  Pseudo code looks as follows: 
 
lr = random()
if lr >= .66666:
	agent_host.sendCommand(“moveast 1”)
elif lr >=.33333:
	agent_host.sendCommand(“movesouth 1”)
else:
	agent_host.sendCommand(“movewest 1”)
 
Q-learning: This is our first approach for the original visual learner. We wanted to combine the q-learning algorithm from homework 2 and use visual input rather than use the grid for observations. This meant that we wanted to be able to input an image to the agent and produce a prediction based on that input. Our q-learner however, does not do this but rather uses grid observations and ray observations to do the reinforcement learning. We used this as a placeholder until we figured out how to process the images in a way that were usable for the visual agent and as a means of comparing the visual agent to a basic learning algorithm. 
 
How it works: The q-table works by using a grid observation and a ray observation to gather data about the world it is in. From the grid, it gathers block information for the blocks located directly east, southeast, south, west, and southwest of the agent. The number of different blocks each direction can be is described in figure 1 below. The ray observation was also used to gather information and works by giving the agent information about the block that the crosshairs are pointing at. This means that it will give block information about blocks roughly 20 steps away. This information includes block type and distance from the agent. With all these observations the agent had 6,912 total states that it could be in. 
In our q-learning agent, we used a greedy policy to determine the actions of the agent. 
	The pseudo code for the policy is as follows: 
	
	rnd = random()
	if rnd < epsilon: 
		action = random(0, # of actions possible)
	else:
		m = max(q_table[current_state])
		tiebreak = []
		for i in range(0, # of actions)
			if q_table[current_state][i] == m:
				tiebreak.append(i)
		choose = random(0, # of item in tiebreak)
		action = tiebreak[choose]
 
	Figure 1: 
 
Block : 4 blocks possible
Block : 4 blocks possible 
Block : 4 blocks possible 
Block: 3 blocks possible
Ray observation : 3 blocks possible
Block: 3 blocks possible
 
 
 
 
 
 
 
 
 
 
 
 
 
 
A* Oracle: This agent works by first getting a grid for the entire level and then turns that grid into a two dimensional array which is used to find a path through the level using the A* algorithm using a heuristic that evaluates the number of neighbors each neighbor has. The pseudocode is as follows:
 
While not frontier.empty():
	Current = frontier.get()
	If agent is at end of level:
		Break
	For next in current.neighbors():
		If cost to next is less than current cost:
			Current cost = next cost
			Score = heuristic(next)
			If score != 0:
				frontier.put(next, score)
				path.add(next)
Return path
 
After this happens we’re left with all the possible solutions to the level and the score associated with each path. Another function chooses the best path and ensures that the agent is solving the level properly, and from there builds a list of the necessary actions. Finally, the agent follows the actions in the list and traverses the level while taking screenshots of what it’s doing for use with the visual agent. 
 
Visual Agent: The visual agent is the final agent that we implemented. We used all the knowledge we acquired through the development of the other agents to build this last one. It essentially only use images as input to train and make decisions. We moved away from the reinforcement learning approach and decided on using decision trees instead. We decided this based on the bad performance of the previously implemented q-learner and the fact that using images would mean having a massive amount of states thus making that approach very impractical. 
 
How it works: First, we used the oracle agent to run 50 times for every level we had. That meant that we had a total of 150 runs of which each consisted of 199 images and 199 decisions. This meant that we had 29,850 images to train from. The way we trained the agent was by creating a x_train and the a y_train to feed to the decision tree. However, the hardest part was determining how we would collect images from the malmo API. We did that by using the following code: 
 
frame	= world_state.video_frame[-1]
image	= Image.frombytes(‘RGB’, (frame.width, frame.height), str(frame.pixels))
 
Essentially that converted the byte array into a png file that we can use in the openCV library to do the edge detection. Also, that allows us to save it in  folder to use as a training data set in the learner. 
	
The way the x_train is structures is that each row is an image and each column is the features extracted from that image. We decided that we would extract features using the openCV canny edge detection library. This meant that each feature was essentially the pixel intensity above a certain threshold. So the number of features was the width*height of images. However, we realized that we needed to do some feature reduction. We did this by excluding the bottom and top ⅓’s of the images and excluding 1/6 of the image from the left and right. We made this decision because the majority of the interesting pixels were located right in front of the agent. 
 
We then trained the agent using a decision tree implementation from sklearn. We used the default settings since it proved to be very good at learning our data with those settings. 
Once trained, we used the predict function in the decision tree library in the act function in our learner to decide on an action. We collected this as our validation data. We will explain later the performance of each learner in the evaluation portion of the report. 
 
 
	
 
Evaluation: In order to evaluate the effectiveness of visual agents we’ve created three additional agents to compare it against. All of the agents will be compared by the number of actions they are able to take while the level is running which is also how far into the level they manage to get. The random agent serves as an absolute minimum as to what the visual agent should be able to do. If the visual agent is unable to traverse further than the random agent we will know something is wrong. The qlearning agent is representative of a basic learning algorithm; something that is much easier to implement than the visual learner. If the visual agent could not do better than this agent that would be disappointing, but a good lesson on working smarter rather than harder. Finally, the oracle agent is used to train the agent is is able to complete the level perfectly every time, so it’s less of a basis for comparison and more a training tool, but being able to match it would be incredible. 

Below are three graphs, one for each level of the game, that display the performance of each agent.  
![graphs](https://user-images.githubusercontent.com/27802382/27006750-6c516f82-4df1-11e7-928e-22c070ab6b98.png)
 
We’re very pleased with our final results and having no idea what they would be going in, it’s pretty surprising that it was able to do so well.  
