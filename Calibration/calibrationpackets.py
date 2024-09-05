import struct
from pylibrnp.rnppacket import RnpPacket


class ServoCalibration(RnpPacket):
    '''Servo calibration packet. Minimum and maximum angle define the servo allowed bounds, home angle defines the position the servo returns to by default (i.e. on power-up).'''
    struct_str = '<BIIIIIII'
    size = struct.calcsize(struct_str)
    packet_type = 105

    def __init__(self, command: int = 5, defaultAngle: int = 0, minAngle: int = 0, maxAngle: int = 180, minWidth: int = 500, maxWidth: int = 2500, minAngleLimit: int = 0, maxAngleLimit: int = 0):

        self.command:int = command
        self.defaultAngle = defaultAngle
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.minWidth = minWidth
        self.maxWidth = maxWidth
        self.minAngleLimit = minAngleLimit
        self.maxAngleLimit = maxAngleLimit

        super().__init__(list(vars(self).keys()),
                         ServoCalibration.struct_str,
                         ServoCalibration.size,
                         ServoCalibration.packet_type)

    def __str__(self):
        header_str = self.header.__str__() + "\n"
        param_str = f'SERVO CALIBRATION PACKET BODY: \tcommand = {self.command}\n \t\t\tminimum angle = {self.angl_min} \n \t\t\tmaximum angle = {self.angl_max}\n \t\t\thome angle = {self.home_angl}\n'
        return header_str + param_str

class PTapCalibration(RnpPacket):
    '''Calibration packet for pressure transducers with a linear relationship between the pressure and reading.'''
	
    struct_str = '<Bff'
    size = struct.calcsize(struct_str)
    packet_type = 106

    def __init__(self, command: int = 5, const: float = 0, gradient: float = 0):

        self.command:int = command
        self.constant:float = const
        self.gradient:float = gradient

        super().__init__(list(vars(self).keys()),
                         PTapCalibration.struct_str,
                         PTapCalibration.size,
                         PTapCalibration.packet_type)

    def __str__(self):
        header_str = self.header.__str__() + "\n"
        param_str = f'PTAP CALIBRATION PACKET BODY: \tcommand = {self.command}\n \t\t\t constant = {self.constant} \n \t\t\tgradient = {self.gradient}\n'
        return header_str + param_str
    
class RedlineCalibration(RnpPacket):
    '''Calibration packet for redline monitor limits.'''
	
    struct_str = '<Bff'
    size = struct.calcsize(struct_str)
    packet_type = 109

    def __init__(self, command: int = 5, val_limit: float = 0, grad_limit: float = 0):

        self.command:int = command
        self.value_limit:float = val_limit
        self.gradient_limit:float = grad_limit

        super().__init__(list(vars(self).keys()),
                         RedlineCalibration.struct_str,
                         RedlineCalibration.size,
                         RedlineCalibration.packet_type)

    def __str__(self):
        header_str = self.header.__str__() + "\n"
        param_str = f'REDLINE PACKET BODY: \tcommand = {self.command}\n \t\t\t limit = {self.value_limit} \n \t\t\t grad_limit = {self.gradient_limit} \n'
        return header_str + param_str


class SolenoidCalibration(RnpPacket):
    '''Solenoid calibration packet.'''
    struct_str = '<BH'
    size = struct.calcsize(struct_str)
    packet_type = 115

    def __init__(self, command: int = 5, normal_state: int = 0):

        self.command:int = command
        self.normal_state:int = normal_state
        
        super().__init__(list(vars(self).keys()),
                         SolenoidCalibration.struct_str,
                         SolenoidCalibration.size,
                         SolenoidCalibration.packet_type)

    def __str__(self):
        header_str = self.header.__str__() + "\n"
        param_str = f'SOLENOID CALIBRATION PACKET BODY: \tcommand = {self.command}\n \t\t\normal state = {self.normal_state} \n'
        return header_str + param_str