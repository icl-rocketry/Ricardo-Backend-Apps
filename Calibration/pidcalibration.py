from pylibrnp.defaultpackets import *
from pylibrnp.rnppacket import *
from calibrationpackets import *
# import ..pylibrnp.defaultpackets
# import ..pylibrnp.rnppacket


import socketio
import argparse



sio = socketio.Client(logger=False, engineio_logger=False)


@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('response',namespace='/packet')
def on_response_handler(data):
    print(data)
    try:
        packet = bytes.fromhex(data['data'])
        header = RnpHeader.from_bytes(packet)
        print(header)
        if header.source_service == 2 and header.packet_type == 100:
            #we have a string message packet
            packet_body = packet[RnpHeader.size:]
            try:
                message = packet_body.decode('UTF-8')
            except:
                message = str(packet_body)
            print("Message: " + message)

    except:
        print("Failed to decode header")

@sio.on('Error',namespace='/packet')
def on_error_handler(data):
    print(data)




if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=False, help="backend host", type=str,default = "localhost")
    ap.add_argument("--port", required=False, help="backend port", type=int,default = 1337)
    args = vars(ap.parse_args())

    sio.connect('http://' + args["host"] + ':' + str(args['port']) + '/',namespaces=['/','/telemetry','/packet'])

    while True:
        source = input("source node : ")
        while not source:
            source = input("source node : ")
        destination = input("destination node : ")
        destination_service = input("destination service : ")
        k11 = input("k_11: ")
        k12 = input("k_12: ")
        k13 = input("k_13: ")
        k14 = input("k_14: ")
        k15 = input("k_15: ")
        k16 = input("k_16: ")
        cmd_packet = PIDCalibration(command = 5, k11 = float(k11), k12 = float(k12), k13 = float(k13), k14 = float(k14), k15 = float(k15), k16 = float(k16))
        cmd_packet.header.destination_service = int(destination_service)
        cmd_packet.header.source_service = 1
        cmd_packet.header.source = int(source)
        cmd_packet.header.destination = int(destination)
        cmd_packet.header.packet_type = 119
        serializedPacket:str = cmd_packet.serialize().hex()
        sio.emit('send_data',{'data':serializedPacket},namespace='/packet')
    
