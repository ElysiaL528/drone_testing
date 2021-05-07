"""
Similar to the detect_tower_height test, except this implements the lighthouse coordinate system

Flies the drone straight toward the tower until the multiranger detects the tower within the given range. Then, the drone flies upward until
the drone no longer sees the tower, indicating it reached the top. The drone flies forward another 0.2 meters, and then lands.
"""

#TODO: Figure out how to set the initial (x,y,z) coordinate for the position commander so the first command goes to the right position
#       instead of using the starting point as (0,0) and fixing its position after the first go_to command
import sys
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.mem import Poly4D
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger
from cflib.positioning.position_hl_commander import PositionHlCommander

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/E7E7E7E7D4'
#uri = 'radio://0/80/250K/E7E7E7E7D4'

curr_x = 0
curr_y = 0
curr_z = 0

def is_close(range, minDistance):
    if range is None:
        return False
    else:
        return range < minDistance


def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']

    # x = data['lighthouse.x']
    # y = data['lighthouse.y']
    # z = data['lighthouse.z']

    curr_x = x
    curr_y = y
    curr_z = z

    print('pos: ({}, {}, {})'.format(x, y, z))


def start_position_printing(cf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    # log_conf.add_variable('lighthouse.x', 'float')
    # log_conf.add_variable('lighthouse.y', 'float')
    # log_conf.add_variable('lighthouse.z', 'float')
    

    cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_x_history = [1000] * 10
    var_y_history = [1000] * 10
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

            #if the position stabilizes so the incoming values for each axis don't vary by more than 0.001...
            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                start_position_printing(scf)
                break


def reset_estimator(cf):
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)


def activate_high_level_commander(cf):
    cf.param.set_value('commander.enHighLevel', '1')


def activate_mellinger_controller(cf):
    cf.param.set_value('stabilizer.controller', '2')


def run_sequence(cf):
    #global curr_x
    commander = cf.high_level_commander
    print("starting sequence")

    

    with Multiranger(scf) as multiranger:
        # while True:
        #     print(f"left: {multiranger.left}, right: {multiranger.right}, front: {multiranger.front}, back: {multiranger.back}")
        #     time.sleep(1)
        print("fly")
        pc = PositionHlCommander(cf, curr_x, curr_y, curr_z)
        pc.take_off(0.2)
        pc.go_to(0, 0, 0.2)
        time.sleep(3)
        #pc.go_to(0, 0, 0.2)
        

        
        # pc.go_to(-0.35, 0.5, 0.3)
        # time.sleep(3)
        # x = -0.35
        # y = 0.6
        # z = 0.3

        # dist = 0.3

        # while not is_close(multiranger.left, dist) and curr_y < 1.7:
        #     y += 0.01
        #     pc.go_to(x, y, z)
        #     print(f"left: {multiranger.left}")
        # print("reached tower")
        # time.sleep(5)
        # print(f"final left: {multiranger.left}")
        
        # while is_close(multiranger.left, dist):
        #     z += 0.01
        #     pc.go_to(x, y, z)
        #     print(f"x: {x}, y: {y}, z: {z}")
        # print("reached height")
        # time.sleep(3)
        # newY = y + 0.2
        # pc.go_to(x, newY, z)
        # time.sleep(1)
        # pc.land()

        #pc.go_to(x, y, 0.2)
        #time.sleep(1)
    #     time.sleep(1)
    #     pc.land()
    #     # while True:
        #     pos = pc.get_position()
        #     x = pos[0]
        #     y = pos[1]
        #     z = pos[2]
        #     print(f"x: {x}, y: {y}, z: {z}")
        #     time.sleep(1)
            #pc.go_to(0, 0, 0.3, )
        # commander.takeoff(0.3, 1.0)
        # # # #time.sleep(3.0)
        # # # #commander.go_to(0, 0, 0.3, 0, 5)
        # # # #time.sleep(5)
        # # motion_commander._is_flying = True
        # # motion_commander.start_back(0.1)
        # # while not is_close(multiranger.back, 0.3):
        # #     pass
        # # motion_commander.start_back(0)
        # # time.sleep(2)
    commander.stop()


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        activate_high_level_commander(cf)
        activate_mellinger_controller(cf)
        #duration = upload_trajectory(cf, trajectory_id, figure8)
        #print('The sequence is {:.1f} seconds long'.format(duration))
        reset_estimator(cf)
        run_sequence(cf)
        # while True:
        #     pass
        
