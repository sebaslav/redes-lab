from turtle import Turtle, Screen, color
from time import *
from socket import *
from _thread import *
from threading import *
import sys
import keyboard
import re

def mostrar_tortugas_hilo():
    TURTLE_SIZE = 20  #tamaño del jugador
    WORLD_SIZE = 100  #cuadrado de 100 x 100
    angleMap = {'N':90,'E':0,'S':270,'W':180}  #Map para traducir direcciones en angulos de turtle
    colorList = ["red", 'blue', 'yellow', 'green', 'orange', 'black']
    screen = Screen()
    screen.setup(1000,1000)
    style = ('Arial',10,'italic')
    while True:
        screen.clear()
        with mutex_players:
            for p in players:
                pepe = Turtle(shape="turtle", visible=False)
                if p == my_name:
                    pepe.color (colorList[1])
                else:
                    pepe.color (colorList[0])
                pepe.speed(0)
                pepe.penup()
                pepeX = ((players[p]["x"]-50)/(WORLD_SIZE/2))*(screen.window_width()/2-TURTLE_SIZE/2)
                pepeY = ((players[p]["y"]-50)/(WORLD_SIZE/2))*(screen.window_height()/2-TURTLE_SIZE/2)
                pepe.goto(pepeX, pepeY)
                pepe.tiltangle(angleMap.get((players[p]["dir"])))
                pepe.showturtle()
                pepe.write(p,font=style,align='left')
        sleep(dt_show)

def update_player(lp):
    datos_player = lp.split()
    name = my_name
    if datos_player[0] != "PLAYER":
        name = datos_player[0]
    
    #actualiza los datos para el jugador "name"
    x = float(datos_player[1])
    y = float(datos_player[2])
    dir = datos_player[3]
    nuevos_datos = {"x": x, "y": y, "dir": dir}
    players[name] = nuevos_datos

def mundo_hilo(udp_mundo_socket):
    ultimo_timestamp = 0
    while True:
        mensaje_mundo = udp_mundo_socket.recvfrom(65535)[0].decode()

        #parsear y actualizar jugadores
        lineas_mensaje = mensaje_mundo.split("\n")
        timestamp = int(lineas_mensaje[0].split()[1])
        if timestamp < ultimo_timestamp:
            continue #se descarta el mensaje recibido por ser viejo
        lineas_player = lineas_mensaje[1:len(lineas_mensaje)-1]

        with mutex_players:
            if timestamp > ultimo_timestamp:
                players.clear() #borra datos viejos
                ultimo_timestamp = timestamp
            for lp in lineas_player:
                update_player(lp)



mutex_players = allocate_lock()
players = {}
dt_show = 0.1

serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
my_name = sys.argv[3]

if not re.search(r'^(\w)+$', my_name):
    print("El nombre debe ser alfanumerico")
    sys.exit()

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    #conectar al servidor
    clientSocket.connect((serverIP, serverPort))
except OSError:
    print("No se pudo conectar al servidor")
    clientSocket.close()
    sys.exit()

try:
    #mandar comando PLAYER
    mensaje = "PLAYER " + my_name + "\n"
    clientSocket.sendall(mensaje.encode())

    #recibir mensaje OK
    response = ""
    while not ("\n" in response):
        buff = clientSocket.recv(4096).decode()
        if len(buff) == 0: #servidor cerro su socket
            print("El servidor cerro la conexion")
            clientSocket.close()
            sys.exit()
        response += buff
    if response != "OK\n":
        print(response)
        clientSocket.close()
        sys.exit()

    #crear socket UDP
    clientIP = clientSocket.getsockname()[0]
    udp_mundo_socket = socket(AF_INET,SOCK_DGRAM)
    udp_mundo_socket.bind((clientIP, 0))
    udp_port = udp_mundo_socket.getsockname()[1]

    #mandar comando LISTEN
    mensaje = "LISTEN " + str(udp_port) + "\n"
    clientSocket.sendall(mensaje.encode())

    #recibir mensaje OK
    response = ""
    while not ("\n" in response):
        buff = clientSocket.recv(4096).decode()
        if len(buff) == 0: #servidor cerro su socket
            print("El servidor cerro la conexion")
            clientSocket.close()
            udp_mundo_socket.close()
            sys.exit()
        response += buff
    if response != "OK\n":
        print(response)
        clientSocket.close()
        udp_mundo_socket.close()
        sys.exit()
    

    Thread(target=mundo_hilo, args=(udp_mundo_socket,), daemon=True).start()
    Thread(target=mostrar_tortugas_hilo, daemon=True).start()

    #ingresar comandos GO
    direccion_actual = ""
    while True:
        key = keyboard.read_key()
        if key == direccion_actual:
            continue
        if key == 'w':
            direccion_actual = 'w'
            clientSocket.sendall("GO N\n".encode())
        elif key == "s":
            direccion_actual = "s"
            clientSocket.sendall("GO S\n".encode())
        elif key == "a":
            direccion_actual = "a"
            clientSocket.sendall("GO W\n".encode())
        elif key == "d":
            direccion_actual = "d"
            clientSocket.sendall("GO E\n".encode())
        elif key == "x":
            clientSocket.close()
            print("Gracias por jugar")
            sys.exit()
            
except OSError:
    clientSocket.close()
    print("Error en la conexion con el servidor")
    sys.exit()


