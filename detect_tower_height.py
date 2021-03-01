import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils.multiranger import Multiranger

#URI = 'radio://0/80/2M/E7E7E7E7A1'
URI = 'radio://0/80/250K/FEED10700B'
DEFAULT_HEIGHT = 0.3

is_deck_attached = False

def is_close(range):
    MIN_DISTANCE = 0.3  # m

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE

def param_deck_flow(name, value):
    global is_deck_attached
    print(value)
    if value:
        is_deck_attached = True
        print('Deck is attached!')
    else:
        is_deck_attached = False
        print('Deck is NOT attached!')

def run(scf):
    with PositionHlCommander(scf, default_height=DEFAULT_HEIGHT, default_velocity=1) as pc:
        # with Multiranger(scf) as multiranger:
        #     time.sleep(2)
        #     pc.set_default_velocity(0.1)
        #     x = 0
        #     y = 0
        #     z = DEFAULT_HEIGHT

        #     while is_close(multiranger.front) == False:
        #         x += 0.1
        #         pc.go_to(x, y, z)
        #     time.sleep(2)
        #     while is_close(multiranger.front) == True:
        #         z += 0.1
        #         pc.go_to(x, y, z)
        #     time.sleep(3)
        #     pc.go_to(0, 0, 0.2)
        #     time.sleep(1)
        pc.set_default_velocity(0.1)
        pc.go_to(0, 0.1, 0.3)
        time.sleep(1)

        

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        #check that flow deck is fully attached
        scf.cf.param.add_update_callback(group="deck", name="bcFlow2",
                                cb=param_deck_flow)
        time.sleep(2)
        if is_deck_attached:
            run(scf)
            # with Multiranger(scf) as multiranger:
            #     while True:
            #         print(f"left: {multiranger.left}, right: {multiranger.right}, front: {multiranger.front}, back: {multiranger.back}")
            #         time.sleep(1)
        else:
            print("deck not attached")
