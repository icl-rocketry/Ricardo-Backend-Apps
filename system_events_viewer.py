
import socketio
import argparse
import json
import time

sio = socketio.Client(logger=False, engineio_logger=False)

@sio.on('new_event',namespace='/system_events')
def on_message_handler(data):
    # head = data["header"]
    # prefix:str = "[" + str(head["source"]) + ":" + str(head["source_service"]) + " -> " + str(head["destination"]) + ":" + str(head["destination_service"]) + " - " + str(time.time()) + " ] "
    # print(prefix + str(data["message"]))
    print(data)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=False, help="backend host", type=str,default = "localhost")
    ap.add_argument("--port", required=False, help="backend port", type=int,default = 1337)
    args = vars(ap.parse_args())
    
    while True:
        try:
            sio.connect('http://' + args["host"] + ':' + str(args['port']) + '/',namespaces=['/','/system_events'])
            sio.wait()
        except socketio.exceptions.ConnectionError as e:
            print('Server not found, attempting to reconnect!')
            sio.sleep(1)
        
