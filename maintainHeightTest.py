"""
Attempts to fly the drone at a constant height, even if the drone flies over a higher surface. The challenge is to override the flow deck, 
which uses a camera at the bottom of the drone to detect the distance between the drone and the object below it, and then tries to
maintain the same distance between the two at all times. The goal is to make the drone not move up or down if the ground moves up or down.
"""
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

from cflib.positioning.motion_commander import _SetPointThread

URI = "radio://0/80/2M/E7E7E7E7A1"

DEFAULT_HEIGHT = 0.5

is_deck_attached = False
def param_deck_flow(name, val):
    global is_deck_attached
    if val:
        is_deck_attached = True
        print("deck attached")
    else:
        print("deck not attached")

def run_sequence(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        #spt = _SetPointThread(scf, 0.1)
        time.sleep(5)
        # for i in range(10):
        #     time.sleep(1)
        #     print(spt.get_height())
        mc.down(0.2)
        mc.stop()

if __name__ == "__main__":
    cflib.crtp.init_drivers(enable_debug_driver=False)
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache")) as scf:
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2", cb=param_deck_flow)
        time.sleep(2)
        if is_deck_attached:
            run_sequence(scf)
            