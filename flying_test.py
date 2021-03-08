#flies the drone in a circle

import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander

import math

URI = 'radio://0/80/2M/E7E7E7E7E7'
#URI = 'radio://0/80/250K/FEED10700B'
DEFAULT_HEIGHT = 0.5

is_deck_attached = False

logging.basicConfig(level=logging.ERROR)

def param_deck_flow(name, value):
    global is_deck_attached
    print(value)
    if value:
        is_deck_attached = True
        print('Deck is attached!')
    else:
        is_deck_attached = False
        print('Deck is NOT attached!')

def take_off_simple(scf):
    with PositionHlCommander(scf, default_height=DEFAULT_HEIGHT, default_velocity=1) as pc:
        radius = 0.5
        pc.set_default_velocity(0.25)
        time.sleep(5)
        for i in range(36):
            radians = i * 10 * (3.14159 / 180)
            x = radius * math.cos(radians)
            y = radius * math.sin(radians)
            pc.go_to(x, y)
            time.sleep(0.025)
        pc.go_to(0, 0, 0.2)
        time.sleep(2)
        pc.go_to(0, 0, 1)
        time.sleep(5)
        pc.go_to(0, 0, 0.3)
        time.sleep(2)
        

if __name__ == '__main__':

    cflib.crtp.init_drivers(enable_debug_driver=False)
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        #check that flow deck is fully attached
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2",
                                cb=param_deck_flow)
        time.sleep(2)
        if is_deck_attached:
            take_off_simple(scf)
            print("attached")
        else:
            print("deck not attached")

