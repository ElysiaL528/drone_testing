#very unfinished: need to finish takeoff function and write land function

#both functions differ from the ones in position_hl_commander because they take in start & end coordinates, 
#consquently allowing taking off or landing at a chosen height instead of assuming a height of 0 m

#or maybe I could just do a single ramp_go_to function that ramps its speed down as it nears its target
#and just have a takeoff function and land function that just call that ramp_go_to function
import time

class HigherPositionHLCommander:
    DEFAULT = None

    def __init__(self, position_commander):
        self._position_commander = position_commander

    def takeoff(self, curr_pos, target_pos, velocity):
        if self._is_flying:
            raise Exception('Already flying')

        if not self._cf.is_connected():
            raise Exception('Crazyflie is not connected')

        # Wait a bit to let the HL commander record the current position
        now = time.time()
        hold_back = self._init_time + 1.0 - now
        if (hold_back > 0.0):
            time.sleep(hold_back)

        self._position_commander._is_flying = True

        height = self._height(curr_pos.z)

        duration_s = height / self._velocity(velocity)
        self._hl_commander.takeoff(height, duration_s)
        time.sleep(duration_s)
        self._z = height

    def _velocity(self, velocity):
        if velocity is self.DEFAULT:
            return self._default_velocity
        return velocity

    def _height(self, height):
        if height is self.DEFAULT:
            return self._default_height
        return height