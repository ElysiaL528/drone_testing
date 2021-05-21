#TODO:
#Step-by-step capability where we can input (via keyboard or controller) to run each step of the program
#Somehow remove the necessity of taking off to a default height, or take off to currentHeight + default height
#Landing correction (i.e. if you land a bit off from the target, take off and land again until within a certain margin of target)

import time

import pygame
import enum

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander

from collections import namedtuple

# URI to the Crazyflie to connect to
uri = 'radio://0/80/2M/E7E7E7E7E7'

#these values are set in position_callback, when the drone gets info from the base stations
xPos = 0
yPos = 0
zPos = 0

DEFAULT_HEIGHT = 0.5

is_deck_attached = False

found_location = False

#almost like a tuple in C#. The first parameter is the type it returns 
#(which is the same as the variable you're setting the namedtuple instance to),
# and the second parameter takes in the different variables
Point = namedtuple('Point', 'x y z') 

class ControllerButtons(enum.Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5

#list of Points for the drone to travel to
coordinates = [
    Point(0, 0, 0.4),
    Point(2, -1, 0.6),
    Point(-0.33, 1, 1),
    Point(-0.33, 1.53, 1),
    Point(-0.33, 1.53, 0.7)
]

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
        global xPos
        global yPos
        global zPos
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
    global xPos
    global yPos
    global zPos
    global found_location 
    xPos = data['kalman.stateX']
    yPos = data['kalman.stateY']
    zPos = data['kalman.stateZ']

    found_location = True

    print('pos: ({}, {}, {})'.format(xPos, yPos, zPos))

def set_position_callback(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

def vector_substract(v0, v1):
    return [v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]]


def vector_add(v0, v1):
    return [v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2]]

def run_sequence(scf):
    cf = scf.cf

    
    with PositionHlCommander(scf, default_height=DEFAULT_HEIGHT+zPos, default_velocity=1) as pc:
        #fly to random positions, waiting for console input between each movement
        button_pressed = -1
        for (x, y, z) in coordinates:
            pressed_button = False
            pc.go_to(x, y, z)
            print(f'x: {x}, y: {y}, z: {z}')
            while not pressed_button:
                for event in pygame.event.get(): # User did something.
                    button_pressed = event.dict.get("button")
                    if event.type == pygame.JOYBUTTONDOWN:
                        print("Joystick button pressed.")
                        pressed_button = True
            if button_pressed == ControllerButtons.LB.value: #the LB button cancels the rest of the flight & returns to origin
                pc.set_default_velocity(0.2)
                pc.go_to(0, 0, 0.2)
                break
            elif button_pressed == ControllerButtons.X.value:
                pc.set_default_velocity(0.1)

        time.sleep(1)
        
        #take off and land at same point
        # pc.go_to(0, 0, 0.4)
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
        # pc.go_to(0, 0, 0.4)
        # time.sleep(3)
        # pc.go_to(1, 0, 0.4)
        # time.sleep(3)
        # pc.go_to(1, -1, 0.4)
        # time.sleep(3)
        # pc.go_to(0, -1, 0.4)
        # time.sleep(3)
        # pc.go_to(0, 0, 0.4)
        # time.sleep(2)
        # pc.set_default_velocity(0.2)
        # pc.go_to(0, 0, 0.2)

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


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    pygame.init() #NEEDS to be declared to do anything with pygame

    #this NEEDS to be declared, even if you don't do anything with the variable, for pygame to detect the controller's events
    joystick = pygame.joystick.Joystick(0)
    
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        set_position_callback(scf)
        while not found_location:
            pass
        print(f'x: {xPos}')
        print(f'y: {yPos}')
        print(f'z: {zPos}')
        run_sequence(scf)

        
        

        # while True:
        #     pass