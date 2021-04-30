'''
Examen Practico 2
Fernando López Ramírez - A07144620
Benjamín Gutiérrez Padilla - A01732079
Isser Kaleb Antonio Vasquez -A01732213
Alan Suárez Santamaría - A01328931
'''

import smbus
import time
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import busio
import adafruit_ssd1306

i2c = busio.I2C(SCL, SDA)
bus = smbus.SMBus(1)

# Crea la clase y define el ancho y alto de pantalla
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

#Definimos la direccion i2c de la memoria 24LC256
address = 0x50
#Definimos las variables utilizadas
#Matrices de comprobacion
data = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
dataPar = [2,4,6,8,10,12,14,16,18,20]
dataImpar = [1,3,5,7,9,11,13,15,17,19]
dataPrimo = [2,3,5,7,11,13,17,19]
dataMult3 = [3,6,9,12,15,18]
#Variables
totales = [0,0,1,0]
totalSuma = 0
totalResta = 0
totalMultPri = 1
totalMultTres = 0
#Matrices para imprimir en datos en el OLED
numPar = []
numImpar = []
numMultiPri = []
numMultTres = []

#Funcion para imprimir en la pantala OLED 
def showOLED(num, txt, x, y, t):
	disp.fill(0)
	disp.show()
	image = Image.new('1', (128, 64))
	draw = ImageDraw.Draw(image)

	font = ImageFont.load_default()

	#  Escribe 1 linea de texto
	draw.text((x, y),  txt + str(num),  font=font, fill=255)

	# Muestra Texto
	disp.image(image)
	disp.show()
	time.sleep(t)
	disp.fill(0)
	disp.show()

#Funcion que imprime las direcciones de memoria en consola y en el OLED
#Recibe el numero de localidades a imprimir
def printNums(a):
	for j in range (a):
		bus.write_i2c_block_data(address, 0x0000, [j])
		value = bus.read_byte(address)
		if j == 21 or j == 22 or j == 23 or j == 24:
			print("Recuperado de localidad-> " + str(j) + " direccion-> " + str(value))	
		else:
			print("Recuperado de localidad-> " + str(j) + " valor: " + str(value))		
		#showOLED(value)

#Funcion que lee los datos almacenados del 0->19
def readData():
	i = 1
	for j in range (20):
		bus.write_i2c_block_data(address, 0x0000, [i])
		value = bus.read_byte(address)
		'''if i == 21 or i == 22 or i == 23 or i == 24:
			print("Recuperado de localidad-> " + str(i) + " direccion-> " + str(value))	
		else:
			print("Recuperado de localidad-> " + str(i) + " valor: " + str(value))	'''
		if i in dataPar:
			numPar.append(value)
			totales[0] += value
		if i in dataImpar:
			numImpar.append(value)
			totales[1] -= value
		if i in dataPrimo:
			numMultiPri.append(value)
			totales[2] *=  value
		if i in dataMult3:
			numMultTres.append(value)
			totales[3] += (value*value)
		
		i += 1
	#print(totales)
	#Guardamos los datos
	saveData()

#Funcion que convierte un numero entero en 10 bytes
def int_to_byteArray(x):
	if x < 0:
		x = x * -1
	array = []
	while x > 255:
		a =  x % 256
		array.append(int(a))
		x = (x - a) / 256
		
	a = x % 256
	array.append(int(a))
	
	for i in range(10-len(array)):
		array.append(0)

	array.reverse()
	#print(array)
	return array
	
#Funcion que convierte n direcciones de memoria en un numero entero
def readTotales(addrs, n):
	totalRead = 0
	for j in range (n):
		bus.write_i2c_block_data(address, 0x0000, [addrs + j])
		value = bus.read_byte(address)
		totalRead += (value*256**(n-j-1))
		#Mostrar las lecturas
		#print("Leido en localidad: " + str(addrs+ j) + " con valor: " + str(value))
	return totalRead
	
#Funcion que Lee el elemento contendio en addrs
def readElement(addrs):
	bus.write_i2c_block_data(address, 0x0000, [addrs])
	return bus.read_byte(address)
		
#Funcion que Guarda los totales de las operaciones
def saveData ():
	##Guarda las direcciones en 21,22,23 y 24
	totalesAddress = [30,40,50,60]
	writeMemory(4,21,1,totalesAddress)
	#print("\nDATOS EN MEMORIA")
	#printNums(25)
	##Convierte los totales a arreglos de bytes
	bytesPar = int_to_byteArray(totales[0])
	bytesImpar = int_to_byteArray(totales[1])
	bytesPrimos = int_to_byteArray(totales[2])
	bytesMult3 = int_to_byteArray(totales[3])

	##Guarda los bytes en las direcciones
	writeMemory(10,30, 1, bytesPar)
	writeMemory(10,40, 1, bytesImpar)
	writeMemory(10,50, 1, bytesPrimos)
	writeMemory(10,60, 1, bytesMult3)

#Funcion que escribe en la memoria i datos o un dato especifico (modo)
def writeMemory(i, vIn, modo, array):
	#Write data
	for x in range (i):
		##Modo 0: pide los 20 primeros valores
		if modo == 0:
			arrayInput = int(input("dato " + str(x+1) + ": "))
			#arrayInput = data;
			L_Bye_Data = [vIn, arrayInput]
			bus.write_i2c_block_data(address, 0x0000, L_Bye_Data)
			#print("localidad ->  " + str(vIn) + " valor: " + str(arrayInput))
			vIn += 1
		##Modo 1: escribe los valores específicados en el array
		if modo == 1:
			L_Bye_Data = [vIn, array[x]]
			bus.write_i2c_block_data(address, 0x0000, L_Bye_Data)
			#print("localidad -> " + str(vIn) + " valor: " + str(array[x]))
			vIn += 1
		time.sleep(0.01)
	
#EJECUCION DE PROGRAMA
#Escribimos los 20 numeros a partir de la localidad 1
writeMemory(20,1,0,0)

#Leemos del 1->20 datos y realizamos las operaciones
readData()

#imprimir en el OLED
for i in numPar:
	showOLED(i, "numPar: ", 10, 20, 1)
showOLED(readTotales(readElement(21), 10), "T.Par= ", 10, 20, 3)	

for i in numImpar:
	showOLED(i, "numImpar: ", 10, 20, 1)
showOLED(readTotales(readElement(22), 10), "T.Impar= ", 10, 20, 3)

for i in numMultiPri:
	showOLED(i, "numPri: ", 10, 20, 1)
showOLED(readTotales(readElement(23), 10), "Prim= ", 10, 20, 3)	

for i in numMultTres:
	showOLED(i, "numMultiplo3: ", 10, 20, 1)
showOLED(readTotales(readElement(24), 10), "T.Mult3= ", 10, 20, 3)

#Guardamos la direccion que apunta a la suma de pares en la direccion 25
writeMemory(1, 25, 1, [readTotales( readElement(21), 10)])

#Modificas los 21,22,23,24
writeMemory(4,21,0,0)

#Imprimimos en el OLED el resultado
showOLED(readElement(25) + readElement(21) + readElement(22) + readElement(23) + readElement(24), "Total= ", 10, 20, 3)

bus.close()
