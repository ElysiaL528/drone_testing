#!/usr/bin/env python3
# Demo that makes one Crazyflie take off 30cm above the first controller found
# Using the controller trigger it is then possible to 'grab' the Crazyflie
# and to make it move.
import sys
import time

#import openvr

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander

# URI to the Crazyflie to connect to
#uri = 'radio://0/80/2M'
uri = 'radio://0/80/2M/E7E7E7E7E7'

DEFAULT_HEIGHT = 0.6

is_deck_attached = False

# print('Opening')
# vr = openvr.init(openvr.VRApplication_Other)
# print('Opened')

def param_deck_flow(name, value):
    global is_deck_attached
    print(value)
    if value:
        is_deck_attached = True
        print('Deck is attached!')
    else:
        is_deck_attached = False
        print('Deck is NOT attached!')

def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            # print("{} {} {}".
            #       format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)


def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']

    # x = data['lighthouse.x']
    # y = data['lighthouse.y']
    # z = data['lighthouse.z']

    print('pos: ({}, {}, {})'.format(x, y, z))


def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    # log_conf.add_variable('lighthouse.x', 'float')
    # log_conf.add_variable('lighthouse.y', 'float')
    # log_conf.add_variable('lighthouse.z', 'float')
    

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()


def vector_substract(v0, v1):
    return [v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]]


def vector_add(v0, v1):
    return [v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2]]


def run_sequence(scf):
    cf = scf.cf
    # commander = cf.high_level_commander

    with PositionHlCommander(scf, default_height=DEFAULT_HEIGHT, default_velocity=1) as pc:
        
        #take off and land at same point
        # pc.go_to(0, 0, 0.4)
        # time.sleep(3)
        # pc.set_default_velocity(0.2)
        # pc.go_to(0, 0, 0.2)

        #take off at tower, land at origin
        # pc.set_default_velocity(0.2)
        # pc.go_to(-0.32, 1.26, 0.6)
        # time.sleep(2)
        # pc.go_to(0, 0, 0.6)
        # time.sleep(2)
        # pc.go_to(0, 0, 0.2)

        #take off at origin, land on tower
        # pc.go_to(0, 0, 0.6)
        # pc.set_default_velocity(0.3)
        # pc.go_to(-0.32, 1.26, 0.6)
        # time.sleep(2)
        # pc.go_to(-0.32, 1.26, 0.35)
        
        #square fly (1 m each side)
        pc.go_to(0, 0, 0.4)
        time.sleep(3)
        pc.go_to(1, 0, 0.4)
        time.sleep(3)
        pc.go_to(1, -1, 0.4)
        time.sleep(3)
        pc.go_to(0, -1, 0.4)
        time.sleep(3)
        pc.go_to(0, 0, 0.4)
        time.sleep(2)
        pc.set_default_velocity(0.2)
        pc.go_to(0, 0, 0.2)

        #bigger square fly
        # pc.go_to(0, 0.5, 0.6)
        # time.sleep(3)
        # pc.go_to(2, 0.5, 0.6)
        # time.sleep(3)
        # pc.go_to(2, -1, 0.6)
        # time.sleep(3)
        # pc.go_to(0, -1, 0.6)
        # time.sleep(3)
        # pc.go_to(0, 0, 0.6)
        # time.sleep(2)
        # pc.set_default_velocity(0.2)
        # pc.go_to(0, 0, 0.2)

        # #take off at tower, go to origin
        # pc.go_to(-0.39, 1.47, 1)
        # time.sleep(2)
        # pc.go_to(0, 0, 1)
        # time.sleep(2)
        # pc.go_to(0, 0, 0.2)
        # time.sleep(2)

        #time.sleep(1)
        # pc.go_to(-0.57, 1.35, 0.9)
        # time.sleep(1)
        # pc.go_to(0, 1, 0.3)  
        # time.sleep(2)
        # pc.go_to(0, 0, 0.15)
        # time.sleep(1)

    # with PositionHlCommander(
    #             scf,
    #             x=
    #             default_velocity=0.3,
    #             default_height=0.3,
    #             controller=PositionHlCommander.CONTROLLER_PID) as pc:
    #     pc.go_to(0, 0, 0.3)
    #     time.sleep(2)
    #     pc.go_to(0, 1, 0.2)
    #commander.   

    #cf.commander.send_position_setpoint(0, 0, 0.4, 0)
    #time.sleep(5)
    #cf.commander.send_position_setpoint(-1, 0, 0.4, 0)
    # cf.commander.send_position_setpoint(0, 0, 0.2, 0)
    # time.sleep(5)
    #cf.commander.send_stop_setpoint()

    # cf.commander.send_setpoint(0, 0, 0, 0)
    # time.sleep(2)

    # cf.commander.send_position_setpoint(0, 0, 0.2, 0)
    # time.sleep(3)

    # cf.commander.send_position_setpoint(0, 0, 1, 0)
    # time.sleep(1)

    #print('Printing...')
    #start_position_printing(scf)
    # # Make sure that the last packet leaves before the link is closed
    # # since the message queue is not flushed before closing
    #time.sleep(100)


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2",
                                cb=param_deck_flow)
        time.sleep(2)
        if is_deck_attached:
            print("flow deck attached")
            reset_estimator(scf)
            start_position_printing(scf)
            run_sequence(scf)
            while True:
                pass
            
        else:
            print("Deck not attached")

#    openvr.shutdown()
