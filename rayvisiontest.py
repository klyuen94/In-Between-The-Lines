import MalmoPython
import json
import logging
import os
import random
import sys
import time
import sched

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
        for z in range(2, 198):
            if random.random() < 0.005: #how often to spawn obstacles
                for y in range(46, 56):
                    mission.drawBlock(x, y, z, "glowstone")
    return mission


def run_agent(world_state, agent_host):
    turn_rate = -.0002

    obstacles = []
    while world_state.is_mission_running:

        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()

        for error in world_state.errors:
            print "Error:", error.text
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text  # Yes, so get the text
            observations = json.loads(msg)  # and parse the JSON

            grid = observations.get(u'floorAll', 0)
            obstacles.append(grid[-1]) # left
            obstacles.append(grid[-2]) #center
            obstacles.append(grid[-3]) #rigth
            print(obstacles)
            if obstacles[-2] == u'glowstone':
                agent_host.sendCommand("movewest 1")
            agent_host.sendCommand("movesouth 0.5")
        obstacles = []








def start_mission(mission, agent_host):
    max_retries = 3  # how many times it tries to start the mission
    num_levels = 2  # how many levels

    #for loop runs the number of missions
    for i in range(num_levels):
        mission = create_level(mission, num_levels, i)
        mission_record = MalmoPython.MissionRecordSpec()
        #tried to start the mission
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


        run_agent(world_state, agent_host)
        print "Mission ended"
        time.sleep(0.5)

    print "Done"

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
    my_agent_host = create_def_objs()
    my_mission = create_mission()
    start_mission(my_mission, my_agent_host)





