import struct
from pylibrnp.rnppacket import RnpPacket


class ServoCalibration(RnpPacket):
    '''Servo calibration packet. Minimum and maximum angle define the servo allowed bounds, home angle defines the position the servo returns to by default (i.e. on power-up).'''
    struct_str = '<BHHH'
    size = struct.calcsize(struct_str)
    packet_type = 105

    def __init__(self, command: int = 5, angl_min: int = 0, angl_max: int = 180, home_angl: int = 0):

        self.command:int = command
        self.angl_min:int = angl_min
        self.angl_max:int = angl_max
        self.home_angl:int = home_angl

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
