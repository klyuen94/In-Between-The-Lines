import MalmoPython
import json
import logging
import os
import random
import sys
import time


class QAgent:
    def __init__(self, epsilon=0.1, alpha=0.1, gamma=1.0):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.loops = 0
        self.actions = ['moveeast 1', None, 'movewest 1']
        self.q_table = {}

    def clean_obs(self, observations):
        grid = observations.get(u'floorAll', 0)
        if type(grid) == int:
            print 'Grid Error'
            return 0
        if u'LineOfSight' not in observations.keys():  # south
            far = u'air'
        else:
            far = observations[u'LineOfSight'][u'type']
        return (grid[8],grid[5], grid[7], far, grid[3], grid[6]) #south east, east, south, far south, west, southwest

    def update_state(self, agent_host):
        world_state = agent_host.peekWorldState()
        while world_state.is_mission_running and all(e.text=='{}' for e in world_state.observations):
            world_state = agent_host.peekWorldState()
        world_state = agent_host.getWorldState()
        for err in world_state.errors:
            print err
        return world_state

    def act(self, world_state, agent_host, current_r):

        if not world_state.is_mission_running:
            return 0

        agent_host.sendCommand("movesouth 1")  # send forced movement command before making observation
        time.sleep(.1)  # this value varies based on computer, if 'didn't get observation!' message, increase it

        world_state = self.update_state(agent_host)
        if world_state.number_of_observations_since_last_state > 0:  # If we get an observation, make the observation
            msg = world_state.observations[-1].text
            obs = json.loads(msg)
            current_state = self.clean_obs(obs)
        else:
            print "Didn't get observation!"
            return 0

        if not self.q_table.has_key(current_state):
            self.q_table[current_state] = ([0] * len(self.actions))

        # update q table if not first action
        if self.prev_state is not None and self.prev_action is not None:
            old_q = self.q_table[self.prev_state][self.prev_action]
            self.q_table[self.prev_state][self.prev_action] = old_q + self.alpha + (current_r + self.gamma * max(self.q_table[current_state]) - old_q)

        # select an action
        rnd = random.random()
        if rnd < self.epsilon:  # take random action
            print '\nRANDOM!'
            action = random.randint(0, len(self.actions) - 1)
        else: # take action with highest q value
            m = max(self.q_table[current_state])
            tiebreak = list()
            for i in range(0, len(self.actions)):
                if self.q_table[current_state][i] == m:
                    tiebreak.append(i)
            choose = random.randint(0, len(tiebreak)-1)
            action = tiebreak[choose]

        # what it's doing, what it sees, what the highest q is, what all the q's are
        #print "Doing: ", self.actions[action], " In State: ", current_state, " because: ", self.q_table[current_state][action], " With Q: ", self.q_table[current_state]
        #time.sleep(2)

        if self.actions[action] is not None and world_state.is_mission_running: # choosing to just move forward will be the None action
            agent_host.sendCommand(self.actions[action])
            time.sleep(.2)
        self.prev_state = current_state
        self.prev_action = action

        return current_r

    def run(self, agent_host):
        self.prev_state = None
        self.prev_action = None

        total_reward = 0
        current_r = 0
        self.loops = 1

        # wait for available observation
        world_state = self.update_state(agent_host)

        if not world_state.is_mission_running:
            return 0

        # take first action
        total_reward += self.act(world_state, agent_host, current_r)

        # main loop
        while world_state.is_mission_running:
            world_state = self.update_state(agent_host)
            current_r = sum(r.getValue() for r in world_state.rewards)
            total_reward += self.act(world_state, agent_host, current_r)
            self.loops += 1
        total_reward += current_r
        if self.prev_state is not None and self.prev_action is not None:
            old_q = self.q_table[self.prev_state][self.prev_action]
            self.q_table[self.prev_state][self.prev_action] = old_q + self.alpha * (current_r - old_q)

        return total_reward

def create_def_objs():  # Create default Malmo objects:
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
    level = 1
    if level == 0:
        count = 0
        for x in range(0, 5):
            for z in range(5, 198):
                if count % 17 == 0:
                    for y in range(44, 56):
                        mission.drawBlock(x, y, z, 'glowstone')
                count += 1

    elif level == 1:
        for x in range(0, 5):
            for z in range(5, 198):
                if random.random() < 0.05 :  # how often to spawn obstacles
                    for y in range(44, 56):
                        mission.drawBlock(x, y, z, 'glowstone')
    return mission


def start_mission(mission, agent_host, agent):
    max_retries = 3  # how many times it tries to start the mission
    num_levels = 1  # how many levels
    num_repeats = 200  # how many times it repeats each level
    for i in range(num_levels):
        mission = create_level(mission, num_levels, i)
        mission_record = MalmoPython.MissionRecordSpec()
        for repeat in range(num_repeats):
            print repeat + 1, " of ", num_repeats
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
            cumulative_reward = agent.run(agent_host)
            print "\nTraveled:", agent.loops
            #print "Did:", agent.actions[agent.prev_action], "In State:", agent.prev_state, "Because:", agent.q_table[agent.prev_state]
            print "Mission ended\n"
            time.sleep(2)

        print  'Cumulative Reward: ', cumulative_reward, "for level: ", i
    print "Done"

def create_agent():
    # epsilon = %chance to take random action, alpha = % of reward agent remembers, gamma = decay rate
    agent = QAgent(epsilon=0.03, alpha=0.1, gamma=0.9)
    return agent


if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    my_agent_host = create_def_objs()
    my_mission = create_mission()
    agent = create_agent()
    start_mission(my_mission, my_agent_host, agent)





