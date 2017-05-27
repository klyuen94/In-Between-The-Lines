import MalmoPython
import json
import logging
import os
import random
import sys
import time
import sched

current_yaw_delta_from_depth = 0

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
    mission_file = './videoproducer.xml'
    with open(mission_file, 'r') as f:
        mission_xml = f.read()
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        return my_mission

def create_level(mission, num_levels, level):
    print 'Level %d of %d' % (level + 1, num_levels)
    for x in range(0, 5):
        for z in range(5, 198):
            if random.random() < 0.01: #how often to spawn obstacles
                for y in range(46, 56):
                    mission.drawBlock(x, y, z, "glowstone")
    return mission

def process_frame(frame):
    global current_yaw_delta_from_depth
    video_height = 1920
    video_width = 1080

    y = int(video_height / 2)
    rowstart = y * video_width

    v = 0
    v_max = 0
    v_max_pos = 0
    v_min = 0
    v_min_pos = 0

    dv = 0
    dv_max = 0
    dv_max_pos = 0
    dv_max_sign = 0

    d2v = 0
    d2v_max = 0
    d2v_max_pos = 0
    d2v_max_sign = 0

    for x in range(0, video_width):
        nv = frame[(rowstart + x) * 4 + 3]
        ndv = nv - v
        nd2v = ndv - dv

        if nv > v_max or x == 0:
            v_max = nv
            v_max_pos = x

        if nv < v_min or x == 0:
            v_min = nv
            v_min_pos = x

        if abs(ndv) > dv_max or x == 1:
            dv_max = abs(ndv)
            dv_max_pos = x
            dv_max_sign = ndv > 0

        if abs(nd2v) > d2v_max or x == 2:
            d2v_max = abs(nd2v)
            d2v_max_pos = x
            d2v_max_sign = nd2v > 0

        d2v = nd2v
        dv = ndv
        v = nv

    print "d2v, dv, v: " + str(d2v) + ", " + str(dv) + ", " + str(v)

    # We want to steer towards the greatest d2v (ie the biggest discontinuity in the gradient of the depth map).
    # If it's a positive value, then it represents a rapid change from close to far - eg the left-hand edge of a gap.
    # Aiming to put this point in the leftmost quarter of the screen will cause us to aim for the gap.
    # If it's a negative value, it represents a rapid change from far to close - eg the right-hand edge of a gap.
    # Aiming to put this point in the rightmost quarter of the screen will cause us to aim for the gap.
    if dv_max_sign:
        edge = video_width / 4
    else:
        edge = 3 * video_width / 4

    # Now, if there is something noteworthy in d2v, steer according to the above comment:
    if d2v_max > 8:
        current_yaw_delta_from_depth = (float(d2v_max_pos - edge) / video_width)
    else:
        # Nothing obvious to aim for, so aim for the farthest point:
        if v_max < 300:
            current_yaw_delta_from_depth = (float(v_max_pos) / video_width) - 0.5
        else:
            # No real data to be had in d2v or v, so just go by the direction we were already travelling in:
            if current_yaw_delta_from_depth < 0:
                current_yaw_delta_from_depth = -1
            else:
                current_yaw_delta_from_depth = 1

def run_agent(world_state, agent_host):
    global current_yaw_delta_from_depth
    agent_host.sendCommand("move 2")

    while world_state.is_mission_running:
        sys.stdout.write(".")
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:", error.text

        while world_state.number_of_video_frames_since_last_state < 1 and world_state.is_mission_running:
            world_state = agent_host.getWorldState()

        print "Got Frame"

        if world_state.is_mission_running:
            process_frame(world_state.video_frames[0].pixels)
            agent_host.sendCommand("turn " + str(current_yaw_delta_from_depth))

def start_mission(mission, agent_host):
    max_retries = 3  # how many times it tries to start the mission
    num_levels = 2  # how many levels
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