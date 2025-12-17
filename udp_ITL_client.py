from pylibrnp.defaultpackets import *
from pylibrnp.rnppacket import *
import socketio

import socket
import threading

#THIS SECTION HANDLES CONNECTION TO THE BACKEND SERVER
sio_backend: socketio.Client = socketio.Client(logger=False, engineio_logger=False)

@sio_backend.event()
def connect():
    print("I'm connected to the backend!")

@sio_backend.event()
def connect_error(data):
    print("Connection failed to backend")

@sio_backend.event()
def disconnect():
    print("Disconnected from backend")

@sio_backend.on('response', namespace='/packet') #type: ignore
def backend_response_handler(data):
    print("Response recieved from backend")
    print(data)
    try:
        packet = bytes.fromhex(data['data'])
        header = RnpHeader.from_bytes(packet)
        print(header)
    except:
        print("Failed to decode header")
    send_packet_to_simulator("Very sensative data")

@sio_backend.on('Error',namespace='/packet') #type: ignore
def backend_general_error_handler(data):
    print("An error occured relating to the general backend")
    print(data)


def simulator_response_loop(sock):
    while True:
        try:
            data = sock.recv(struct.calcsize(packet_from_sim_format))
            print("Recieved: ", data.decode('utf-8'))
            send_packet_to_board("IMPORTANT DATA")
        except Exception as e:
            print("Error in response loop:", e)
            break;

#THIS SECTION CONCERNS THE CONNECTION TO THE SIMULATOR
open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
packet_from_sim_format = "<HdQ3d3dd3d3dd8d8dd"
def send_packet_to_simulator(data):
    print("Sending data packet to simulator")
    format = "<HdQ32d"

    if(len(data)) == struct.calcsize(format):
        version_,dt_,frame_,actuators_ = struct.unpack(format,data)
        print("Version: ",version_, " dt:",dt_," frame:",frame_," actuators:", actuators_)
    #TODO ERROR HANDLING
    
    version = 0x0010
    dt = 0
    frame = 0
    actuators = ([0]*32)
    sending_data = struct.pack(format,version,dt,frame,*actuators)

    open_socket.send(sending_data)
    

def send_packet_to_board(data):

    format = packet_from_sim_format

    if len(data) == struct.calcsize(format):
        buff_ = bytes(struct.calcsize(format))
        vals = struct.unpack(format,buff_)
        version = vals[0]
        timestamp = vals[1]
        frame = vals[2]
        gyroscope = vals[3:6]
        accelerometer = vals[6:9]
        barometer = vals[9]
        gps_pos = vals[10:13]
        gps_vel = vals[13:16]
        gps_pdop = vals[16]
        pressures = vals[17:25]
        temperature = vals[25:33]
        battery = vals[34]

        print(version,timestamp,frame,gyroscope,accelerometer,barometer,gps_pos,gps_vel,gps_pdop,pressures,temperature,battery)
    
    #TODO() handle error cases
    print("Sending data packet to board___________________")
    packet:SimpleCommandPacket = SimpleCommandPacket(8, 0)
    packet.header.destination_service = 2
    packet.header.source_service = 1
    packet.header.source = 1
    packet.header.destination = 0
    packet.header.packet_type = 0
    serializedPacket:str = packet.serialize().hex()
    print("[DEBUG] emitting signal")
    sio_backend.emit('send_data',{'data':serializedPacket},namespace='/packet')



#If this function was ran directly
if __name__ == "__main__":

    backend_port = 1337
    backend_host = "localhost"
    backend_source_service = 1

    #connect to the Ricardo-Backend on port 1337 on localhost
    while True:
        try:
            sio_backend.connect('http://' + backend_host + ':' + str(backend_port) + '/',namespaces=['/','/telemetry','/packet'])
            break
        except socketio.exceptions.ConnectionError:  #type: ignore
            print('Server not found, attempting to reconnect!')
            sio_backend.sleep(1)
            # Try every second to connect to the Server

    print("Connected to backend")
    #We have successfully connected to the Ricardo-Backend

    #Connect to the simulator by sending an empty control frame 

    simulator_listening_port = 10550
    local_host = "127.0.0.1" #Loopback IP address

    udp_TIL_listening_port = 10551

    open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    open_socket.bind((local_host,udp_TIL_listening_port))
    open_socket.connect((local_host,simulator_listening_port))

    threading.Thread(target=simulator_response_loop,args=(open_socket,), daemon=False).start()

    
    print("Sending initial contact")
    open_socket.send(b"Connecting to simulator (pretend this is an empty frame")
                     
