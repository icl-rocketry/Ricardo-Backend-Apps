from pylibrnp.defaultpackets import *
from pylibrnp.rnppacket import *
# import ..pylibrnp.defaultpackets
# import ..pylibrnp.rnppacket


import socketio
import argparse
import time
import pandas as pd


sio = socketio.Client(logger=False, engineio_logger=False)
df = pd.DataFrame

def importcurve():
    df = pd.read_csv("reflowcurve.csv", delimiter= ',')
    return df.to_numpy()

def findTemp(time, timebelow, timeabove, tempbelow, tempabove):
    dt = (time - timebelow) / (timeabove - timebelow)
    
    newtemp = dt * (tempabove - tempbelow) + tempbelow

    return newtemp;



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
    data = importcurve()
    prevTime = time.time()
    startTime = time.time()
    rows, cols = data.shape

    for i in range(rows-2):
        while (time.time() - startTime < data[i,1]):
            if (time.time() - prevTime > 0.10):
                currtime = time.time() - startTime

                source = 1
                destination = 0
                destination_service = 2
                command_num = 69
                arg = (273.15+findTemp(currtime,data[i,1],data[i+1,1],data[i,0],data[i+1,0])) * 10000
                #print(arg)
                cmd_packet :SimpleCommandPacket= SimpleCommandPacket(command = int(command_num), arg = int(arg))
                cmd_packet.header.destination_service = int(destination_service)
                cmd_packet.header.source_service = 1
                cmd_packet.header.source = int(source)
                cmd_packet.header.destination = int(destination)
                cmd_packet.header.packet_type = 0
                serializedPacket:str = cmd_packet.serialize().hex()
                sio.emit('send_data',{'data':serializedPacket},namespace='/packet')
                prevTime = time.time()
                
    
    source = 1
    destination = 0
    destination_service = 2
    command_num = 69
    arg = 0
    cmd_packet :SimpleCommandPacket= SimpleCommandPacket(command = int(command_num), arg = int(arg))
    cmd_packet.header.destination_service = int(destination_service)
    cmd_packet.header.source_service = 1
    cmd_packet.header.source = int(source)
    cmd_packet.header.destination = int(destination)
    cmd_packet.header.packet_type = 0
    serializedPacket:str = cmd_packet.serialize().hex()
    sio.emit('send_data',{'data':serializedPacket},namespace='/packet')
    