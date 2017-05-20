import MalmoPython
import json
import logging
import os
import random
import sys
import time
import timeit
import Tkinter as tk

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)


mission_file = './test.xml'
with open(mission_file, 'r') as f:
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)

my_mission_record = MalmoPython.MissionRecordSpec()

def lava_bridge():
    y = 45
    for a in range(4):
        z = random.randint(2,25 +25*i)
        for x in range(0,5):
            my_mission.drawBlock(x, y, z, "lava")
        x = random.randint(0, 5)
        my_mission.drawBlock(x, y, z, "sandstone")
def random_lava_spots(num):
    y = 46
    for a in range(10):
        z = random.randint(a*10,(a+1)*10)
        for x in (random.sample(range(0,5),num)):
            my_mission.drawBlock(x, y, z, "lava")

def level_one():
    y = 46
    for x in range(0,5):
        for z in range(2,100):
            my_mission.drawBlock(x, y, z, "snow_layer")
            #if z < 50:
                #if z%2 == 1:
                 #   my_mission.drawBlock(x, y, z, "red_flower")
                #else:
                 #   my_mission.drawBlock(x,y,z, "yellow_flower")

    #lava_bridge()
def level_two():
    y = 46
    for x in range(0,5):
        for z in range(2,100):
            my_mission.drawBlock(x, y, z, "sand")
def level_three():
    y = 46
    for x in range(0, 5):
        for z in range(2, 100):
            my_mission.drawBlock(x, y, z, "red_sandstone")


# Attempt to start a mission:
max_retries = 3 #how many times it tries to start the mission
num_repeats = 5 #how many "levels"
for i in range(num_repeats):

    print 'Starting Level %d of %d' % ( i+1, num_repeats )
    if i == 0:
        level_one()
        random_lava_spots(i)
    elif i ==1:
        level_two()
        random_lava_spots(i)
    elif i ==2:
        level_three()
        random_lava_spots(i-1)



    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print "Error starting mission:",e
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
            print "Error:",error.text

    print "Mission running ",
    start_time = time.clock()
    # Loop until mission ends:

    while world_state.is_mission_running:
        sys.stdout.write(".")
        agent_host.sendCommand("movesouth 1")
        time.sleep(0.1)

        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text  # Yes, so get the text
            observations = json.loads(msg)  # and parse the JSON
            grid = observations.get(u'floor3x3', 0)
            lr = random.random()
            if lr > .5:
                if grid[5] != u'nether_brick':
                    agent_host.sendCommand("moveeast 1")
            else:
                if grid[3] != u'nether_brick':
                    agent_host.sendCommand("movewest 1")
        else:
            print world_state.observations #help
        time.sleep(0.1)
    end_time = time.clock()
    run_time = end_time - start_time
    print run_time
    print "Mission ended"
    # Mission has ended.

    time.sleep(0.5)

print "Done"
