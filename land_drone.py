#run this program if another program threw an exception and the drone is still flying

import cflib.crtp

from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

#uri = 'radio://0/80/2M'
uri = 'radio://0/80/250K/E7E7E7E7D4'

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        commander = cf.high_level_commander
        commander.stop()
        # pc = PositionHlCommander(cf, 0, 0, 0)
        # pc.land()