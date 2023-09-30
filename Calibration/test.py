
SignMask24bit = 0b100000000000000000000000

data = 0x800000


if (data & SignMask24bit):
    dataInt = 1 + ~data

else:
    dataInt = data

print(dataInt)