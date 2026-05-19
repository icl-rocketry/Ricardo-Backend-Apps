import socketio
import json
import argparse
import magcalibration

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server", required=False, help='address of backend', type=str, default='localhost')
ap.add_argument("-p", "--port",   required=False, help='port of backend',    type=int, default=1337)
ap.add_argument("-f", "--filename", required=False, help='load mag data from CSV instead of live feed', type=str, default='')
args = vars(ap.parse_args())

if __name__ == '__main__':
    magcal = magcalibration.MagCalibration(args['server'], args['port'], args['filename'])

    if args['filename'] == '':
        sio = socketio.Client()
        sio.connect('http://' + args['server'] + ':' + str(args['port']), namespaces=['/telemetry'])

        @sio.on('magcal', namespace='/telemetry')
        def on_telemetry(data):
            telemetryJson = json.loads(data)
            try:
                telemetryFrame = telemetryJson["data"]
            except KeyError:
                telemetryFrame = telemetryJson
            magcal.updateData(telemetryFrame)

    magcal.run()
