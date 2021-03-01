import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

uri1 = "radio://0/80/2M/E7E7E7E7E7"
uri2 = "radio://0/80/2M/E7E7E7E7A1"

DEFAULT_HEIGHT = 0.3

is_deck_attached = True

def param_deck_flow(name, val):
    global is_deck_attached
    if is_deck_attached:
        print(val)
        if val:
            is_deck_attached = True
            print ("Deck is attached")
        else:
            is_deck_attached = False
            print ("Deck not attached")



def run_sequence(scf1, scf2):
    with MotionCommander(scf1, default_height=DEFAULT_HEIGHT) as mc1:
        with MotionCommander(scf2, default_height=DEFAULT_HEIGHT) as mc2:
            mc1.up(0.3)
            mc2.up(0.3)
            time.sleep(1)
            mc1.down(0.2)
            mc2.down(0.2)
            mc1.stop()
            mc2.stop()

if __name__ == "__main__":
    cflib.crtp.init_drivers(enable_debug_driver=False)
    with SyncCrazyflie(uri1, cf=Crazyflie(rw_cache='./cache')) as scf1:
        with SyncCrazyflie(uri2, cf=Crazyflie(rw_cache='./cache')) as scf2:
            scf1.cf.param.add_update_callback(group="deck", name ="bcFlow2", cb=param_deck_flow)
            scf2.cf.param.add_update_callback(group="deck", name ="bcFlow2", cb=param_deck_flow)
            time.sleep(2)
            if is_deck_attached:
                run_sequence(scf1, scf2)
            