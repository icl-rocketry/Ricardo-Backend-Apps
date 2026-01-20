import struct
from pylibrnp.rnppacket import RnpPacket

class simInPacket():
    '''This is sent from the adaptor to the simulator'''
    struct_str = '<HdQ32d'
    size = struct.calcsize(struct_str)
    def __init__(self):
        self.version:int = 0x0010
        self.dt:float = 0.0
        self.frame:int = 0
        self.actuators:list[float] = ([0.0]*32)


class simOutPacket(RnpPacket):
    '''This packet is sent to the adaptor from the Simulator'''

    struct_str = '<HdQ3d3dd3d3dd8d8dd'

    size = struct.calcsize(struct_str)
    packet_type = 0

    #Slightly hacky but python does not allow for multiple constructors
    def __init__(self, vals:tuple = ()):
        if (vals == ()):
            self.version:int = 0x0010
            self.timestamp:float= 0.0
            self.frame:int = 0
            self.gyroscope:list[float] = [0.0]*3
            self.accelerometer:list[float]= [0.0]*3
            self.barometer:float = 0.0
            self.gps_pos:list[float] = [0.0]*3
            self.gps_vel:list[float] = [0.0]*3
            self.gps_pdop:float= 0.0
            self.pressures:list[float] = [0.0]*8
            self.temperature:list[float] = [0.0]*8
            self.battery:float = 0.0
        else:
            assert len(vals) == 34, f"expected 34 values, got {len(vals)}"

            self.version: int = vals[0]
            self.timestamp: float = vals[1]
            self.frame: int = vals[2]
            self.gyroscope: list[float] = list(vals[3:6])
            self.accelerometer: list[float] = list(vals[6:9])
            self.barometer: float = vals[9]
            self.gps_pos: list[float] = list(vals[10:13])
            self.gps_vel: list[float] = list(vals[13:16])
            self.gps_pdop: float = vals[16]
            self.pressures: list[float] = list(vals[17:25])
            self.temperature: list[float] = list(vals[25:33])
            self.battery: float = vals[33]
            
        super().__init__(list(vars(self).keys()),
                         simOutPacket.struct_str,
                         simOutPacket.size,
                         simOutPacket.packet_type)

        

class PickleRickSensorsPacket(RnpPacket):
    '''This packet is sent to the Pickle Rick Board to fake sensor data'''

    struct_str = "<17f4lBH8B"


    size = struct.calcsize(struct_str)
    packet_type = 1 #This identifies the packet as being for the pickle rick board
    
    def __init__(self):

        self.accelgyro_accel:list[float] = [0.0]*3
        self.accelgyro_gyro:list[float] = [0.0]*3
        self.accelerometer:list[float] = [0.0]*3
        self.magnometer:list[float] = [0.0]*3
        self.barometer:list[float] = [0.0]*3
        self.gps_pos:list[float] = [0.0]*2

        self.gps_alt:int = 0
        self.gps_vel:list[int] = [0]*3

        self.gps_sat:int = 0
        self.gps_pdop:int = 0
        self.gps_fix:int = 0
        self.gps_updated:int = 0
        self.gps_valid:int = 0 
        self.imu_error:int = 0
        self.haccel_error:int = 0
        self.mag_error:int = 0
        self.baro_error:int = 0
        self.gps_error:int = 0

        super().__init__(list(vars(self).keys()),
                         PickleRickSensorsPacket.struct_str,
                         PickleRickSensorsPacket.size,
                         PickleRickSensorsPacket.packet_type)
