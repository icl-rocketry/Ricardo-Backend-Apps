from pylibrnp.defaultpackets import *
from pylibrnp.rnppacket import *
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


def get_valid_input_uint8(prompt):
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= 255:
                return value
            else:
                print("Error: Please enter a number between 0 and 255.")
        except ValueError:
            print("Error: Invalid input. Please enter a number between 0 and 255.")

def get_valid_input_int32(prompt):
    while True:
        try:
            value = int(input(prompt))
            if -2**31-1 <= value <= 2**31 - 1:
                return value
            else:
                print("Error: Please enter a number between -2,147,483,647 and 2,147,483,647.")
        except ValueError:
            print("Error: Invalid input. Please enter a number between -2,147,483,647 and 2,147,483,647.")



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=False, help="backend host", type=str,default = "localhost")
    ap.add_argument("--port", required=False, help="backend port", type=int,default = 1337)
    ap.add_argument("--service", required=False, help="Source Service", type=int,default = 1)
    args = vars(ap.parse_args())

    while True:
        try:
            sio.connect('http://' + args["host"] + ':' + str(args['port']) + '/',namespaces=['/','/telemetry','/packet'])
            break
        except socketio.exceptions.ConnectionError:
            print('Server not found, attempting to reconnect!')
            sio.sleep(1)

    

    while True:
        source = get_valid_input_uint8("source node : ")
        while not source:
            source = get_valid_input_uint8("source node : ")
        destination = get_valid_input_uint8("destination node : ")
        destination_service = get_valid_input_uint8("destination service : ")
        command_num = get_valid_input_uint8("command id : ")
        arg = get_valid_input_int32("arg : ")
        cmd_packet :SimpleCommandPacket= SimpleCommandPacket(command = int(command_num), arg = int(arg))
        cmd_packet.header.destination_service = int(destination_service)
        cmd_packet.header.source_service = args['service']
        cmd_packet.header.source = int(source)
        cmd_packet.header.destination = int(destination)
        cmd_packet.header.packet_type = 0
        serializedPacket:str = cmd_packet.serialize().hex()
        sio.emit('send_data',{'data':serializedPacket},namespace='/packet')
    