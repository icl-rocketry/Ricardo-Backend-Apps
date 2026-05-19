import requests
import numpy as np
from scipy import linalg
import threading
import csv
import os
# from . import magpackets
import magpackets
import socket

# from . import graphui
import graphui


class MagCalibration():
    def __init__(self,server,port,filename:str=''):
        self.networkEnabled = True

        self.hostname = socket.gethostname()
        self.clientid = self.hostname + ':MAGCALIBRATIONAPP'

        self.server = server
        self.port = port
        self.url = ''

        self.graphui = graphui.MagCalGraphsUI(on_send_calibration=self.on_send_calibration_clicked)
        
        #threading primitives are used here with the socketio background workers
        self.newData = threading.Event()
        self._lock = threading.Lock()

        self.stopData = False

        self.F = 1 #always calculate a unit transformation -> scale factor can be applied later 

        self.b = np.zeros([3,1])
        self.A_1 = np.eye(3)

        if self.server is None or self.port is None:
            self.networkEnabled = False
            
        else:
            self.url = 'http://' + server + ":" + str(port) + "/packet"
        
        self.magData = {"mx":[],
                        "my":[],
                        "mz":[]}
        self.filename:str = filename

        if self.filename != '':
            self.__load_data__()


    def updateData(self,telemetry):
        with self._lock:
            if not self.stopData:
                self.magData['mx'].append(telemetry["mx"])
                self.magData['my'].append(telemetry["my"])
                self.magData['mz'].append(telemetry["mz"])
                self.newData.set()
    
    def clearData(self):
        with self._lock:
            self.magData = {"mx":[],
                            "my":[],
                            "mz":[]}
            self.graphui.clearPlots()  
            self.newData.set()
    
    def calculate(self,verbose):
        magReadings = np.vstack([np.array(self.magData["mx"]),np.array(self.magData["my"]),np.array(self.magData["mz"])])
        num_rows, num_cols = magReadings.shape
        if num_rows != 3:
            print("Dimention Error")
            print(magReadings.shape)
            return

        if verbose: 
            print(magReadings)
            print(magReadings.shape)
        M, n, d = self.__ellipsoid_fit__(magReadings,verbose)

        M_1 = linalg.inv(M)
        self.b = -np.dot(M_1, n)
        self.A_1 = np.real(self.F / np.sqrt(np.dot(n.T, np.dot(M_1, n)) - d) *
                           linalg.sqrtm(M))

    def plotCalibration(self):
        magReadings = np.vstack([np.array(self.magData["mx"]),np.array(self.magData["my"]),np.array(self.magData["mz"])])
        correctedData = np.dot(self.A_1,(magReadings-self.b))
        correctedDataDict = {"mx":correctedData[0,:].tolist(),
                             "my":correctedData[1,:].tolist(),
                             "mz":correctedData[2,:].tolist()}
        self.graphui.plotCorrectedData(correctedDataDict)

    def send_calibration(self, destination=2, source=4):
        if not self.networkEnabled:
            print("No Server — cannot send calibration!")
            return
        magcalpacket = magpackets.MagCalCommand(command=61)
        magcalpacket.header.destination_service = 2
        magcalpacket.header.source = source
        magcalpacket.header.destination = destination
        magcalpacket.A11 = float(self.A_1[0,0])
        magcalpacket.A12 = float(self.A_1[0,1])
        magcalpacket.A13 = float(self.A_1[0,2])
        magcalpacket.A21 = float(self.A_1[1,0])
        magcalpacket.A22 = float(self.A_1[1,1])
        magcalpacket.A23 = float(self.A_1[1,2])
        magcalpacket.A31 = float(self.A_1[2,0])
        magcalpacket.A32 = float(self.A_1[2,1])
        magcalpacket.A33 = float(self.A_1[2,2])
        magcalpacket.b1 = float(np.real(self.b[0,0]))
        magcalpacket.b2 = float(np.real(self.b[1,0]))
        magcalpacket.b3 = float(np.real(self.b[2,0]))
        send_data = {"data": magcalpacket.serialize().hex(), "clientid": self.clientid}
        r = requests.post(self.url, json=send_data)
        if r.status_code != 200:
            print(f"Send Error: {r.status_code} {r.reason}")
        else:
            print("Calibration sent successfully.")

    def on_send_calibration_clicked(self):
        if len(self.magData['mx']) < 10:
            print(f"Not enough data ({len(self.magData['mx'])} points) — keep wiggling!")
            return
        self.stopData = True
        print(f"Calculating calibration from {len(self.magData['mx'])} points...")
        self.calculate(verbose=False)
        print(f"A_1:\n{self.A_1}\nb:\n{self.b}")
        self.plotCalibration()
        self.send_calibration()

    def run(self):
        while True:
            self.graphui.update()
            if self.newData.is_set():
                with self._lock:
                    # take a snapshot so the lock isn't held during rendering
                    magDataSnapshot = {
                        "mx": list(self.magData["mx"]),
                        "my": list(self.magData["my"]),
                        "mz": list(self.magData["mz"])
                    }
                self.graphui.updateMagField(magDataSnapshot)
                self.newData.clear()

    def __ellipsoid_fit__(self, s,verbose=False):

        # D (samples)
        D = np.array([s[0]**2., s[1]**2., s[2]**2.,
                      2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
                      2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

        # S, S_11, S_12, S_21, S_22 (eq. 11)
        S = np.dot(D, D.T)
        S_11 = S[:6,:6]
        S_12 = S[:6,6:]
        S_21 = S[6:,:6]
        S_22 = S[6:,6:]

        # C (Eq. 8, k=4)
        C = np.array([[-1,  1,  1,  0,  0,  0],
                      [ 1, -1,  1,  0,  0,  0],
                      [ 1,  1, -1,  0,  0,  0],
                      [ 0,  0,  0, -4,  0,  0],
                      [ 0,  0,  0,  0, -4,  0],
                      [ 0,  0,  0,  0,  0, -4]])

        # v_1 (eq. 15, solution)
        E = np.dot(linalg.inv(C),
                   S_11 - np.dot(S_12, np.dot(linalg.inv(S_22), S_21)))

        if verbose: print(E)

        E_w, E_v = np.linalg.eig(E)

        if verbose:
            print("Eigenvalues") 
            print(E_w)
            print("Eigenvectors")
            print(E_v)

        v_1 = E_v[:, np.argmax(E_w)]
        if v_1[0] < 0: v_1 = -v_1

        # v_2 (eq. 13, solution)
        v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

        # quadric-form parameters
        M = np.array([[v_1[0], v_1[3], v_1[4]],
                      [v_1[3], v_1[1], v_1[5]],
                      [v_1[4], v_1[5], v_1[2]]])
        n = np.array([[v_2[0]],
                      [v_2[1]],
                      [v_2[2]]])
        d = v_2[3]

        if verbose:
            print(M)
            print(n)
            print(d)
        return M, n, d

    def __load_data__(self):
        if not os.path.isfile(self.filename):
            print(str(self.filename) + " Not Found!")
            return
        if not self.filename.endswith(".csv"):
            print("Unrecognized File Type!")
            return
        with open(self.filename,newline='') as csvfile:
            reader = csv.reader(csvfile)
            numcols = len(list(reader)[0])
            if numcols != 3:
                print("Wrong number of Columns!")
                return

            csvfile.seek(0)

            for line in reader:
                self.magData['mx'].append(float(line[0]))
                self.magData['my'].append(float(line[1]))
                self.magData['mz'].append(float(line[2]))

            self.newData.set()

    def __save_data__(self,filename:str):
        if not filename.endswith(".csv"):
            filename += ".csv"
        with open(filename,'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(zip(*[self.magData[key] for key in ["mx","my","mz"]]))

    def __save_cal__(self,filename:str):
        if not filename.endswith(".txt"):
            filename += ".txt"
        with open(filename,'w') as file:
            file.write("MAGNETOMTER CALIBRATION\n")
            file.write("A_1:\n")
            for line in self.A_1:
                np.savetxt(file,line,fmt='%0.30f')
            file.write("\nb:\n")
            for line in self.b:
                np.savetxt(file,line,fmt='%0.30f')
            
        
   
