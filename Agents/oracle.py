import MalmoPython
import json
import logging
import os
import random
import sys
import time
import Queue
import numpy as np

from PIL import Image
class OracleStarAgent:
    def __init__(self):
        self.loops = 0
        self.count = 0
        self.level = []
        self.actions = ['moveeast 1', None, 'movewest 1']
        self.route = []
        self.route_indexes = []


    def grid_to_level(self, grid):
        line = []
        for sq in range(len(grid)):
            if sq % 5 == 0 and sq != 0:
                self.level.append(line)
                line = []
                line.append(grid[sq])
            else:
                line.append(grid[sq])
        self.level.append(line)

    def update_state(self, agent_host):
        world_state = agent_host.peekWorldState()
        while world_state.is_mission_running and all(e.text=='{}' for e in world_state.observations):
            world_state = agent_host.peekWorldState()
        world_state = agent_host.getWorldState()
        for err in world_state.errors:
            print err
        return world_state

    def neighbors(self, coor):
        ret = []
        z = coor[0]
        x = coor[1]
        if z < 198:
            if self.level[z+1][x] == u'sandstone':
                ret.append((z+1,x))
            if x != 4 and self.level[z+1][x+1] == u'sandstone' and self.level[z][x+1] == u'sandstone':
                ret.append((z+1,x+1))
            if x != 0 and self.level[z+1][x-1] == u'sandstone' and self.level[z][x-1] == u'sandstone':
                ret.append((z+1,x-1))

        return ret

    def heuristic(self, coor, sum, d):
        sum +=  len(self.neighbors(coor))
        if d == 1:
            return sum
        for n in self.neighbors(coor):
            sum += self.heuristic(n, sum, d+1)
        return sum

    def find_path(self):
        print 'Finding Path...'
        ag_x = 2
        ag_z = 0
        came_from = {}
        cost_so_far = {}
        score_from = {}
        frontier = Queue.PriorityQueue()
        frontier.put((ag_z, ag_x))
        came_from[(ag_z, ag_x)] = None
        cost_so_far[(ag_z, ag_x)] = 0
        score_from[(ag_z, ag_x)] = None

        while not frontier.empty():
            current = frontier.get()
            if current == (0, 199) or current == (1, 199) or current == (2, 199) or current == (3, 199) or current == (4, 199):
                break

            for next in self.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    score = self.heuristic(next,0,0)
                    if score != 0:
                        frontier.put(next, score)
                        came_from[next] = current
                        score_from[next] = score

        return score_from, came_from

    def clean_path(self, path, came_from):
        current = (0,2)
        clean = []
        winner = ()
        for next in sorted(path.keys()):
            #print next, path[next]
            if next[0] == 0:
                clean.append(next)
                previous = next
                continue
            if previous[1] == next[1] or previous[1]+1 == next[1] or previous[1]-1 == next[1]:  # x in came_from[y] didn't work
                if current[0] != next[0]:
                    if winner:
                        clean.append(winner)
                        previous = winner
                    max = path[next]
                    winner = next
                else:
                    if path[next] > max:
                        max = path[next]
                        winner = next
                current = next
            else:
                if current[0] != next[0]:
                    if winner:
                        clean.append(winner)
                        previous = winner
                    if previous[1] == next[1] or previous[1] + 1 == next[1] or previous[1] - 1 == next[1]:
                        max = path[next]
                        winner = next
                    else:
                        max = -1
                        winner = ()
                current = next

        return clean

    def create_route(self, path, came_from):
        current = (0,2)
        path = self.clean_path(path, came_from)
        for next in path:
            if next[0] == 0:
                continue
            if next[1] == current[1]:
                self.route.append(self.actions[1])
                self.route_indexes.append(1)
            elif next[1] < current[1]:
                self.route.append(self.actions[2])
                self.route_indexes.append(2)
            else:
                self.route.append(self.actions[0])
                self.route_indexes.append(0)
            current = next
        for i in range(1,3):
            self.route.append(self.actions[1])
            self.route_indexes.append(1)

    def save_frame(self, agent_host, world_state, index):
        while world_state.number_of_video_frames_since_last_state < 1 and world_state.is_mission_running:
            world_state = agent_host.getWorldState()
        frame = world_state.video_frames[-1]
        filepath = "C:/Users/hrvega1510/Desktop/here/"
        image = Image.frombytes('RGB', (frame.width, frame.height), str(frame.pixels))
        image.save(filepath+str(index)+".png")


    def act(self, world_state, agent_host):
        for i in range(len(self.route)):  # main loop
            self.loops += 1
            world_state = self.update_state(agent_host)
            if not world_state.is_mission_running:
                return 0
            agent_host.sendCommand('movesouth 1')  # forced move
            time.sleep(.1)
            self.count = self.count + 1
            self.save_frame(agent_host, world_state, self.count)
            if self.route[i] is not None:

                agent_host.sendCommand(self.route[i])
                time.sleep(.1)





    def run(self, agent_host):
        world_state = self.update_state(agent_host)
        if world_state.number_of_observations_since_last_state > 0:  # If we get an observation, make the observation
            msg = world_state.observations[-1].text
            observations = json.loads(msg)
            grid = observations.get(u'levelAll', 0)
        else:
            print "Didn't get observation!"
            return 0

        self.grid_to_level(grid)
        path, came_from = self.find_path()
        self.create_route(path, came_from)

        self.act(world_state, agent_host)

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
    mission_file = './oracle.xml'
    with open(mission_file, 'r') as f:
        mission_xml = f.read()
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        return my_mission


def create_level(mission, num_levels, level):
    print 'Level %d of %d' % (level + 1, num_levels)
    level = 2
    if level == 0:
        for z in range(2,195):
            if z == 4:
                rnd = random.randint(0,4)
                for x in range(0,5):
                    if x != 0:
                        mission.drawCuboid(x, 44, z, x, 56, z, 'glowstone')

    elif level == 1:
        for x in range(0, 5):
            for z in range(5, 195):
                if random.random() < 0.05 :  # how often to spawn obstacles
                    for y in range(44, 56):
                        mission.drawBlock(x, y, z, 'glowstone')

    elif level == 2:
        for z in range(5,195):
            if z % 15 == 0:
                rnd = random.randint(0,4)
                for x in range(0,5):
                    if x != rnd:
                        mission.drawCuboid(x, 44, z, x, 56, z, 'glowstone')

    return mission


def start_mission(mission, agent_host, agent):
    max_retries = 3  # how many times it tries to start the mission
    num_levels = 1  # how many levels
    for i in range(num_levels):
        mission = create_level(mission, num_levels, i)
        mission_record = MalmoPython.MissionRecordSpec()
        for retry in range(max_retries):
            try:
                agent_host.startMission(mission, mission_record)
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print "Error starting mission:", e
                    exit(1)
                else:
                    time.sleep(1)

        print "Waiting for the mission to start ",
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            sys.stdout.write(".")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print "Error:", error.text

        print "Mission running\n",
        agent.run(agent_host)
        print "Traveled:", agent.loops
        print "Mission ended\n"
        time.sleep(1)

    print "Done"
    #returns the action list and the frames of video from each discrete time movement of the oracle agent 


def create_agent():
    agent = OracleStarAgent()
    return agent

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    my_agent_host = create_def_objs()
    my_mission = create_mission()
    agent = create_agent()
    start_mission(my_mission, my_agent_host, agent)

