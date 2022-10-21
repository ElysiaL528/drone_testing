import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

from cflib.crazyflie.log import LogConfig #a representation of one log configuration that enables logging from the Crazyflie
from cflib.crazyflie.syncLogger import SyncLogger #The SyncLogger class provides synchronous access to log data from the Crazyflie.

uri = 'radio://0/80/2M/E7E7E7E7E7'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def simple_log(scf, logconf):
    with SyncLogger(scf, lg_stab) as logger:
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]
            print("timestamp: ", timestamp, "name: ", logconf_name, "data", data)
            time.sleep(1)

def simple_log_async(scf, logconf):
    cf = scf.cf
    cf.log.add_config(logconf)
    logconf.data_received_cb.add_callback(log_stab_callback)
    logconf.start()
    time.sleep(5)
    logconf.stop()

def param_stab_est_callback(name, value):
    print("parameter: ", name, " value: ", value)

def simple_param_async(scf, groupstr, namestr):
    cf = scf.cf
    full_name = groupstr + "." + namestr
    cf.param.set_value(full_name, 1)
    cf.param.add_update_callback(group=groupstr, name=namestr, cb=param_stab_est_callback)
    cf.param.set_value(full_name,2)
    time.sleep(1)

def log_stab_callback(timestamp, data, logconf):
    print(timestamp, " ", logconf.name, " ", data)

def simple_connect():
    print("connected :)")

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    #add logging configuration
    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    group = "stabilizer"
    name = "estimator"

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        simple_param_async(scf, group, name)
    