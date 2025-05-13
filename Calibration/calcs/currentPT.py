#Sensor params
PTmax = 100 #in bar
minI = 4e-3 #min sensr current
maxI = 20e-3 #max sensr current

#Board params
sensR = 49.9 #in ohms
ADCMaxV = 1.2
ADCMaxCounts = 2**23 - 1

minCounts = ADCMaxCounts * (minI * sensR)/ADCMaxV
maxCounts = ADCMaxCounts * (maxI * sensR)/ADCMaxV

m = (maxCounts - minCounts)/(PTmax)
zeroReading  = 1396573 #adc channel reading at ambient pressure with PT plugged in
c = zeroReading - 1.0135 * m #for absolute pressure instead of gauge

print(c)
print(m)