import MalmoPython
import json
import logging
import os
import random
import sys
import time
import sched, time


class TabQAgent:
    """Tabular Q-learning agent for discrete state/action spaces."""

    def __init__(self, actions=[], epsilon=0, alpha=0.1, gamma=1.0, debug=False, canvas=None, root=None):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.training = True

        self.actions = actions
        self.q_table = {}
        self.canvas = canvas
        self.root = root

        self.rep = 0

    def clean_obs(self, observations):
        grid = observations.get(u'floorAll', 0)


        if u'LineOfSight' not in observations.keys():  # south
            south = u'air'
        else:
            south = observations[u'LineOfSight'][u'type']


        print (grid[5], south , grid[3])
        return (grid[8], grid[5], south , grid[3], grid[6]) #southeast east west southwest


    def act(self, world_state, agent_host, current_r):
        """take 1 action in response to the current world state"""

        if world_state.number_of_observations_since_last_state > 0:

            obs_text = world_state.observations[-1].text
            obs = json.loads(obs_text)  # most recent observation

            current_s = self.clean_obs(obs)

            if not self.q_table.has_key(current_s):
                self.q_table[current_s] = ([0] * len(self.actions))

            # update Q values
            if self.training and self.prev_s is not None and self.prev_a is not None:
                old_q = self.q_table[self.prev_s][self.prev_a]
                self.q_table[self.prev_s][self.prev_a] = old_q + self.alpha * (current_r + self.gamma * max(self.q_table[current_s]) - old_q)

            print self.q_table[current_s]
            # select the next action
            rnd = random.random()
            if rnd < self.epsilon:
                a = random.randint(0, len(self.actions) - 1)
            else:
                m = max(self.q_table[current_s])

                l = list()
                for x in range(0, len(self.actions)):
                    if self.q_table[current_s][x] == m:
                        l.append(x)
                y = random.randint(0, len(l) - 1)
                a = l[y]


            # send the selected action
            if self.actions[a] != None:
                agent_host.sendCommand(self.actions[a])
            print self.actions[a]
            self.prev_s = current_s
            self.prev_a = a
        return current_r

    def run(self, world_state, agent_host):
        time.sleep(0.5)
        total_reward = 0
        current_r = 0
        tol = 0.01

        self.prev_s = None
        self.prev_a = None
        world_state = agent_host.peekWorldState()
        s = sched.scheduler(time.time, time.sleep)
        total_reward += self.act(world_state, agent_host, current_r)

        while world_state.is_mission_running:

            sys.stdout.write(".")
            move_agent_south(agent_host)

            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            current_r = sum(r.getValue() for r in world_state.rewards)
            for error in world_state.errors:
                print "Error:", error.text
            if world_state.number_of_observations_since_last_state > 0:
                if world_state.is_mission_running:
                    # act
                    total_reward += self.act(world_state, agent_host, current_r)

            #total reward
            total_reward += current_r

            #update q table
            if self.training and self.prev_s is not None and self.prev_a is not None:
                old_q = self.q_table[self.prev_s][self.prev_a]
                self.q_table[self.prev_s][self.prev_a] = old_q + self.alpha * (current_r - old_q)

        return total_reward

def create_def_objs(): # Create default Malmo objects:
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print 'ERROR:', e
        print agent_host.getUsage()
        exit(1)
    if agent_host.receivedArgument("help"):
        print agent_host.getUsage()
        exit(0)
    return agent_host

def create_mission():
    mission_file = './rayvision.xml'
    with open(mission_file, 'r') as f:
        mission_xml = f.read()
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        return my_mission

def create_level(mission, num_levels, level):
    print 'Level %d of %d' % (level + 1, num_levels)
    for x in range(0, 5):
        for z in range(5, 198):
            if random.random() < 0.05: #how often to spawn obstacles
                for y in range(44, 56):
                    mission.drawBlock(x, y, z, "glowstone")
    return mission

def move_agent_south(agent_host):
    agent_host.sendCommand("movesouth .5")


def start_mission(mission, agent_host):
    #list of actions the agent can go do
    actionSet = [ None, "movewest 1", "moveeast 1"]

    #creating an agent object
    agent = TabQAgent(
        actions=actionSet)

    max_retries = 3  # how many times it tries to start the mission
    num_levels = 2  # how many levels
    for i in range(num_levels):
        mission = create_level(mission, num_levels, i)
        mission_record = MalmoPython.MissionRecordSpec()
        num_repeats = 200
        cumulative_rewards = []
        for i in range(num_repeats):
            for retry in range(max_retries):
                try:
                    agent_host.startMission(mission, mission_record)
                    break
                except RuntimeError as e:
                    if retry == max_retries - 1:
                        print "Error starting mission:", e
                        exit(1)
                    else:
                        time.sleep(2)

            print "Waiting for the mission to start ",
            world_state = agent_host.getWorldState()
            while not world_state.has_mission_begun:
                sys.stdout.write(".")
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
                for error in world_state.errors:
                    print "Error:", error.text

            print "Mission running ",

            cumulative_reward = agent.run(world_state, agent_host)

            print "Mission ended"
            cumulative_rewards += [cumulative_reward]
            time.sleep(0.5)

    print "Done"

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    my_agent_host = create_def_objs()
    my_mission = create_mission()
    start_mission(my_mission, my_agent_host)





