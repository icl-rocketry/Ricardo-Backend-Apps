from pylibrnp.defaultpackets import *
from pylibrnp.rnppacket import *
from hitlpackets import * 

import socketio
import socket
import threading

#THIS SECTION HANDLES CONNECTION TO THE BACKEND SERVER
sio_backend: socketio.Client = socketio.Client(logger=False, engineio_logger=False)

@sio_backend.event()
def connect():
    print("I'm connected to the backend!")

@sio_backend.event()
def connect_error(_):
    print("Connection failed to backend")

@sio_backend.event()
def disconnect():
    print("Disconnected from backend")

@sio_backend.on('response', namespace='/packet') #type: ignore
def backend_response_handler(data):
    print("Response recieved from backend")
    packet = bytes.fromhex(data['data'])
    process_and_send_to_simulator(packet)


@sio_backend.on('Error',namespace='/packet') #type: ignore
def backend_general_error_handler(data):
    print("An error occured relating to the general backend")
    print(data)


#__________________________________________________________________________________
#THIS SECTION CONCERNS THE CONNECTION TO THE SIMULATOR
open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#These need to be set manually if the format of the simulator structures are changed!

#Ran by a thread dedicated to waiting for simulator actions and sending the data to the backend
def simulator_response_loop(sock):
    while True:
            data = sock.recv(simInPacket.size)
            process_and_send_sensor_data(data)

#These should be maintained within this adaptor program
'''SETUP - This is maintained thread safe such that multiple inbound packets can be processed concurrently'''
setuplock = threading.Lock() # basic lock to protect date (if performance becomes a greater concern then an alternative data type should be used for stored_actuators
toSimPacket:simInPacket = simInPacket()
toSimPacket.version = 0x0010
toSimPacket.actuators = [0.0 for _ in range(32)]
toSimPacket.dt = 0
toSimPacket.frame = 0


#Recieves actuator data from the board and processes appropriately
def process_and_send_to_simulator(packet):
    print("Sending data packet to simulator")

    header = RnpHeader.from_bytes(packet)

#Handle recieved packet according to the packet origin board
    match header.packet_type:
        case 1:
            print("packet recived from pickle rick board")
            #FILL ANY DATA RECIEVED HERE
            setuplock.acquire()
            actuators = [0.0 for _ in range(32)]
            setuplock.release()

            #Stand in for updating the stored actuators
            toSimPacket.actuators = actuators

        case _:
            print("Unknown packet recieved by the adaptor from hardware")
            return
    
    setuplock.acquire()
    sending_data = struct.pack(simInPacket.struct_str,toSimPacket.version,toSimPacket.dt,toSimPacket.frame,*actuators)
    setuplock.release()
    open_socket.send(sending_data)

#Accepts vals which is of the form of the unpacked C++ struct
def send_packet_to_pickle_rick(packet:simOutPacket):
    pickleRickSensorsPacket:PickleRickSensorsPacket = PickleRickSensorsPacket()
    pickleRickSensorsPacket.accelgyro_gyro = packet.gyroscope 
    pickleRickSensorsPacket.accelerometer = packet.accelerometer
    pickleRickSensorsPacket.barometer = [packet.barometer]*3
    pickleRickSensorsPacket.gps_pos = packet.gps_pos[0:2]
    pickleRickSensorsPacket.gps_vel = [int(x) for x in packet.gps_vel]
    pickleRickSensorsPacket.gps_pdop = int(packet.gps_pdop)

    ''' Other Pieces of data 0 by default at this point in time '''
 
    #Direct packet to the PickleRickBoard
    pickleRickSensorsPacket.header.destination_service = 3
    pickleRickSensorsPacket.header.source_service = 0
    pickleRickSensorsPacket.header.source = 1
    pickleRickSensorsPacket.header.destination = 0
    pickleRickSensorsPacket.header.packet_type = 1

    #Serialize and send the packet over the socketio connection to the backend
    serializedPacket:str = pickleRickSensorsPacket.serialize().hex()
    sio_backend.emit('send_data',{'data':serializedPacket}, namespace='/packet')

    
#Accepts data of the form of the c++ structure used by the simulator program
def process_and_send_sensor_data(data):
    vals = struct.unpack(simOutPacket.struct_str,data)
    packet:simOutPacket = simOutPacket(vals)
    if(vals[0] != toSimPacket.version): return #Ensure that the version of the packets being sent and recieved with the simulator are correct to ensure that they are operating on the same version

#Send data to all relevent boards
    send_packet_to_pickle_rick(packet)

    #INSERT OTHER BOARDS DATA HERE



if __name__ == "__main__":

    backend_port = 1337
    backend_host = "localhost"
    backend_source_service = 1

#Connect to the Ricardo-Backend on port 1337 on localhost
    sio_backend.connect('http://' + backend_host + ':' + str(backend_port) + '/',namespaces=['/','/telemetry','/packet'])
    print("Connected to backend")

#Enable HITL
    cmd_packet :SimpleCommandPacket= SimpleCommandPacket(command = 0, arg = 0)
    cmd_packet.header.destination_service = 3
    cmd_packet.header.source_service = 0
    cmd_packet.header.source = 1
    cmd_packet.header.destination = 0
    cmd_packet.header.packet_type = 0
    serializedPacket:str = cmd_packet.serialize().hex()
    sio_backend.emit('send_data',{'data':serializedPacket},namespace='/packet')



#Connect to the simulator
    simulator_listening_port = 10550
    udp_ITL_listening_port = 10551
    local_host = "127.0.0.1" #Loopback IP address

    open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    open_socket.bind((local_host,udp_ITL_listening_port))
    open_socket.connect((local_host,simulator_listening_port))
    threading.Thread(target=simulator_response_loop,args=(open_socket,), daemon=False).start()

#DEBUG
    print("Sending contact to the simulator")
    open_socket.send(b"Debug message from udp_ITL_client")
                     
