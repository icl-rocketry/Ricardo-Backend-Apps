#Sensor properties
mvperV = 2.0 #Output in mV at full scale range per input Volt (from datasheet)
FSR = 100 #Full scale range in kg
supplyV = 12

#ADC properties
adcMaxCounts = 2**23 - 1
adcMaxV = 1.2
adcGain = 1

m = adcMaxCounts * (mvperV * supplyV / (adcMaxV * 1/adcGain))/FSR

print("Gradient: " + str(m))