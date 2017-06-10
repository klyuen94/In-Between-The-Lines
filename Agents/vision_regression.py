import MalmoPython
import json
import logging
import os
import random
import sys
import time
import train_classifier
from PIL import Image
import cv2
from sklearn.externals import joblib
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class VisualAgent:
    def __init__(self):
        self.prev = "movesouth 1"
        self.actions = ['moveeast 1', None, 'movewest 1']
        self.loops = 0

    def clear(self):
        self.loops = 0
        self.prev = "movesouth 1"

    def update_state(self, agent_host):
        world_state = agent_host.peekWorldState()
        while world_state.is_mission_running and all(e.text=='{}' for e in world_state.observations):
            world_state = agent_host.peekWorldState()
        world_state = agent_host.getWorldState()
        for err in world_state.errors:
            print err
        return world_state

    def act(self, world_state, agent_host,lr):
        if not world_state.is_mission_running:
            return 0

        world_state = self.update_state(agent_host)
        if world_state.is_mission_running and world_state.number_of_video_frames_since_last_state > 0:
            frame = world_state.video_frames[-1]
            image = Image.frombytes('RGB', (frame.width, frame.height), str(frame.pixels))
            image.save("save.png")
            img = cv2.imread("save.png")
            edges = cv2.Canny(img, 200, 300)
            edges = edges[80:160,72:360]
            move = lr.predict(edges.flatten())
            move = int(move[0])
            if move == 0:
                agent_host.sendCommand(self.prev)
                self.prev = self.actions[0]
                time.sleep(.1)
            elif move == 2:
                agent_host.sendCommand(self.prev)
                self.prev = self.actions[2]
                time.sleep(.1)

        if world_state.is_mission_running:
            agent_host.sendCommand(self.prev)
            self.prev = "movesouth 1"
            time.sleep(.1)

    def run(self, agent_host,learner):
        world_state = self.update_state(agent_host)
        if not world_state.is_mission_running:
            return 0
        # main loop
        while world_state.is_mission_running:
            world_state = self.update_state(agent_host)
            self.act(world_state,agent_host,learner)
            self.loops += 1

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
                if random.random() < 0.027 :  # how often to spawn obstacles
                    for y in range(44, 56):
                        mission.drawBlock(x, y, z, 'glowstone')

    elif level == 2:
        for z in range(5,195):
            if z % 15 == 0:
                rnd = random.randint(0,4)
                for x in range(0,5):
                    if x != rnd:
                        mission.drawCuboid(x, 44, z, x, 56, z, 'glowstone')

def start_mission(agent_host, agent, learner):
    max_retries = 3  # how many times it tries to start the mission
    num_levels = 10  # how many levels

    for i in range(num_levels):
        mission = create_mission()
        create_level(mission, num_levels, i)
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
        agent.run(agent_host, learner)
        print "Traveled:", agent.loops-1
        agent.clear()
        print "Mission ended\n"
        time.sleep(2)


    print "Done"

def create_agent():

    agent = VisualAgent()
    return agent


if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    my_agent_host = create_def_objs()
    agent = create_agent()
    choice = raw_input('input lr for saving a model and ld to load a model: ')
    if choice == "lr":
        learner = train_classifier.train_classifier()
        filename = 'finalized_model_10.sav'
        joblib.dump(learner, filename)
    elif choice == "ld":
        learner = joblib.load('finalized_model_10.sav')
    start_mission(my_agent_host, agent, learner)