#!/usr/bin/env python3

#  ,---------,       ____  _ __
#  |  ,-^-,  |      / __ )(_) /_______________ _____  ___
#  | (  O  ) |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  | / ,--´  |    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#     +------`   /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Crazyflie control firmware
#
#  Copyright (C) 2020 Bitcraze AB
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, in version 3.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
#  Persist geometry and calibration data in the Crazyflie storage.
#
#  This script uploads geometry and calibration data to a crazyflie and
#  writes the data to persistant memory to make it available after
#  re-boot.
#
#  This script is a temporary solution until there is support
#  in the client.


import logging
import time

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import LighthouseBsCalibration
from cflib.crazyflie.mem import LighthouseBsGeometry
from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

uri = 'radio://0/30'


class WriteMem:
    def __init__(self, uri, geos, calibs):
        self.data_written = False
        self.result_received = False

        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            mems = scf.cf.mem.get_mems(MemoryElement.TYPE_LH)

            count = len(mems)
            if count != 1:
                raise Exception('Unexpected nr of memories found:', count)

            lh_mem = mems[0]

            for bs, geo in geos.items():
                self.data_written = False
                print('Write geoetry', bs, 'to RAM')
                lh_mem.write_geo_data(bs, geo, self._data_written, write_failed_cb=self._data_failed)

                while not self.data_written:
                    time.sleep(0.1)

            for bs, calib in calibs.items():
                self.data_written = False
                print('Write calibration', bs, 'to RAM')
                lh_mem.write_calib_data(bs, calib, self._data_written, write_failed_cb=self._data_failed)

                while not self.data_written:
                    time.sleep(0.1)

            print('Persist data')
            scf.cf.loc.receivedLocationPacket.add_callback(self._data_persisted)
            scf.cf.loc.send_lh_persist_data_packet(list(range(16)), list(range(16)))

            while not self.result_received:
                time.sleep(0.1)


    def _data_written(self, mem, addr):
        self.data_written = True

    def _data_failed(self, mem, addr):
        raise Exception('Write to RAM failed')

    def _data_persisted(self, data):
        if (data.data):
            print('Data persisted')
        else:
            raise Exception("Write to storage failed")

        self.result_received = True


geo0 = LighthouseBsGeometry()
geo0.origin = [-1.01977998,-0.19424433, 1.97086964]
geo0.rotation_matrix = [[ 0.66385385,-0.26347329, 0.6999142 ], [0.18206993,0.96466617,0.19044612], [-0.72536102, 0.00100494, 0.68836792], ]
geo0.valid = True

geo1 = LighthouseBsGeometry()
geo1.origin = [0, 0, 0]
geo1.rotation_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
geo1.valid = False

calib1 = LighthouseBsCalibration()
calib1.sweeps[0].tilt = -0.050709
calib1.sweeps[0].phase = 0.000000
calib1.sweeps[0].curve = 0.357357
calib1.sweeps[0].gibphase = 1.992199
calib1.sweeps[0].gibmag = -0.015771
calib1.sweeps[0].ogeephase = 2.078221
calib1.sweeps[0].ogeemag = 0.781026
calib1.sweeps[1].tilt = 0.049767
calib1.sweeps[1].phase = -0.006410
calib1.sweeps[1].curve = 0.369651
calib1.sweeps[1].gibphase = 2.684854
calib1.sweeps[1].gibmag = -0.012641
calib1.sweeps[1].ogeephase = 2.898701
calib1.sweeps[1].ogeemag = 0.641948
calib1.valid = True

calib2 = LighthouseBsCalibration()
calib2.sweeps[0].tilt = -0.052741
calib2.sweeps[0].phase = 0.000000
calib2.sweeps[0].curve = 0.131445
calib2.sweeps[0].gibphase = 2.541155
calib2.sweeps[0].gibmag = -0.005665
calib2.sweeps[0].ogeephase = 3.079340
calib2.sweeps[0].ogeemag = 0.144523
calib2.sweeps[1].tilt = 0.049684
calib2.sweeps[1].phase = -0.006519
calib2.sweeps[1].curve = 0.204206
calib2.sweeps[1].gibphase = 2.586327
calib2.sweeps[1].gibmag = -0.003412
calib2.sweeps[1].ogeephase = 0.736291
calib2.sweeps[1].ogeemag = -0.111319
calib2.valid = True

logging.basicConfig(level=logging.ERROR)
cflib.crtp.init_drivers(enable_debug_driver=False)

WriteMem(uri,
    {
        0: geo0,
        1: geo1,
    },
    {
        0: calib1,
        1: calib2,
    })
