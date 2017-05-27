import MalmoPython
import json
import logging
import os
import random
import sys
import time
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


mission_file = './random.xml'
with open(mission_file, 'r') as f:
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)

my_mission_record = MalmoPython.MissionRecordSpec()


# Attempt to start a mission:
max_retries = 3 #how many times it tries to start the mission
num_repeats = 2 #how many "levels"
for i in range(num_repeats):
    print 'Repeat %d of %d' % ( i+1, num_repeats )

    for x in range(0, 5):
        for z in range(2, 298):
            if random.random() < 0.03:
                for y in range(46,56):
                    my_mission.drawBlock(x, y, z, "glowstone")


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
            if lr >= .66666:
                if grid[5] != u'water':
                    agent_host.sendCommand("moveeast 1")
            elif lr >= .333333:
                continue
            else:
                if grid[3] != u'water':
                    agent_host.sendCommand("movewest 1")
        time.sleep(0.1)

    print "Mission ended"
    # Mission has ended.

    time.sleep(0.5)

print "Done"
