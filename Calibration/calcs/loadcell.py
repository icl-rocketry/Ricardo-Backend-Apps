#Sensor properties
mvperV = 2.0 #Output in mV at full scale range per input Volt (from datasheet)
FSR = 100 #Full scale range in kg
supplyV = 5

#ADC properties
adcMaxCounts = 2**23 - 1
adcMaxV = 1.2
adcGain = 1

g = 9.80655

m = adcMaxCounts * (mvperV * 1e-3 * supplyV / (adcMaxV * 1/adcGain))/ (FSR * g)

print("Gradient: " + str(m))