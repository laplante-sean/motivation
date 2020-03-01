'''
Used to track power
'''
import threading


class PowerTracker:
    '''
    Base class for tracking power output
    '''

    _instance = None

    def __init__(self, req_power):
        self.lock = threading.Lock()
        self.power = 0
        self.req_power = req_power
        self._instance = self

    @classmethod
    def get(cls):
        '''
        If the instance isn't set yet, it'll just return None
        '''
        return cls._instance

    def set_power(self, power):
        '''
        Value directly from device
        '''
        with self.lock:
            self.power = power

    def get_effective_power(self):
        '''
        Must be implemented by base class. Get's the effective power value for
        whatever version of this class is implemented.
        '''
        raise NotImplementedError

    def pass_fail(self):
        '''
        Are we doing well enough?
        '''
        eff_power = self.get_effective_power()
        return eff_power >= self.req_power


class AveragePowerTracker(PowerTracker):
    '''
    Track average power output
    '''

    def __init__(self):
        self.running_sum = 0
        self.count = 0
        super().__init__()

    def set_power(self, power):
        with self.lock():
            self.running_sum += power
            self.count += 1
        super().set_power(power)

    def get_effective_power(self):
        '''
        For average power we have to calculate a running average
        '''
        with self.lock:
            if not self.count:
                return 0
            return self.running_sum / self.count



class RawPowerTracker(PowerTracker):
    '''
    Track raw power output
    '''

    def get_effective_power(self):
        '''
        For raw power it's just the difference b/w current power and start power
        '''
        with self.lock:
            return self.power
