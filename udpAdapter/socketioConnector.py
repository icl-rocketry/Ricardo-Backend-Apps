import socketio
import redis
import json
import multiprocessing
import queue

verbose = False
sendQueue = None
receiveQueue = None

sio = socketio.Client(logger=False, engineio_logger=False)

@sio.event
def connect():
    print("Socketio Connected")

@sio.event
def connect_error(data):
    print("Socketio Connection Failed!")

@sio.event
def disconnect():
    print("Socketio Disconnected!")

@sio.on('response',namespace='/packet')
def on_response_handler(data):
    packet = bytes.fromhex(data['data'])
    if verbose:
        print(packet.hex())
    
    receiveQueue.put({"data":packet})
    

@sio.on('Error',namespace='/packet')
def on_error_handler(data):
    print(data)




def SocketioConnector(host,port,sendQ,receiveQ,_verbose):
    global verbose,sendQueue,receiveQueue
    verbose = _verbose
    sendQueue = sendQ
    receiveQueue = receiveQ
    
    sio.connect('http://' + str(host) + ":" +str(port),namespaces=['/','/packet'])

    while True:
        try:
            packet = sendQueue.get_nowait()
            sio.emit('send_data',{'data':str(bytes(packet['data']).hex())},namespace='/packet')
        except queue.Empty:
            pass


