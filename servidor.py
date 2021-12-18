from socket import *
from _thread import *
from threading import *
from time import *
from random import *
import sys
import math
import re

def simulacion_hilo():
    while True:
        with mutex_players:
            for p in players:
                if players[p]["dir"] == "N":
                    players[p]["y"] += v*dt_sim
                elif players[p]["dir"] == "S":
                    players[p]["y"] -= v*dt_sim
                elif players[p]["dir"] == "E":
                    players[p]["x"] += v*dt_sim
                elif players[p]["dir"] == "W":
                    players[p]["x"] -= v*dt_sim
                players[p]["x"] = players[p]["x"] % map_size
                players[p]["y"] = players[p]["y"] % map_size
        sleep(dt_sim)

def obtener_vecinos(player):
    vecinos = []
    for p in players:
        if player != p:
            dist = math.hypot(players[player]["x"] - players[p]["x"], players[player]["y"] - players[p]["y"])
            if dist < rango_visual:
                vecinos.append(p)
    return vecinos

def construir_mensajes(p, vecinos, timestamp):
    mensajes = []
    i = 0
    fin_de_vecinos = False
    while not fin_de_vecinos:
        mensaje = "WORLD " + timestamp + "\n"
        mensaje += "PLAYER " + str(players[p]["x"]) + " " + str(players[p]["y"]) + " " + players[p]["dir"] + "\n"
        while i < len(vecinos):
            nueva_linea = vecinos[i] + " " + str(players[vecinos[i]]["x"]) + " " + str(players[vecinos[i]]["y"]) + " " + players[vecinos[i]]["dir"] + "\n"
            if len(mensaje + nueva_linea) < max_udp_payload:
                mensaje += nueva_linea
                i += 1
            else:
                break
        mensajes.append(mensaje)
        if i == len(vecinos):
            fin_de_vecinos = True    
    return mensajes

def mundo_hilo():
    mundo_socket = socket(AF_INET, SOCK_DGRAM)
    while True:
        timestamp = str(int((time() - start_time)*1000))
        with mutex_players:
            for p in players:
                if "addr" in players[p]: #chequea que se haya recibido el comando LISTEN
                    vecinos = obtener_vecinos(p)
                    mensajes = construir_mensajes(p, vecinos, timestamp)
                    for m in mensajes:
                        mundo_socket.sendto(m.encode(), players[p]["addr"])
        sleep(dt_send)
    mundo_socket.close()

def atender_jugador_hilo(connectionSocket, addr):
    
    comandos = ""
    try:
        #recibir comando PLAYER
        while (not "\n" in comandos):
            buff = connectionSocket.recv(4096).decode()
            if len(buff) == 0: #cliente cerro su socket
                connectionSocket.close()
                return
            comandos += buff
        comando_player, comandos = comandos.split("\n", 1)

        if not re.search(r'^PLAYER (\w)+$', comando_player):
            error = "FAIL Comando no valido\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

        player_name = comando_player.split()[1]
        if len(player_name) > max_largo_nombre:
            error = "FAIL Nombre muy largo. El nombre debe tener hasta " + str(max_largo_nombre) + " caracteres\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

        player_repetido = False
        with mutex_players:
            if player_name in players:
                player_repetido = True
        if player_repetido:
            error = "FAIL Nombre de jugador repetido\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

        #crear jugador
        new_x = random()*map_size
        new_y = random()*map_size
        new_dir = "E" #por defecto arranca hacia la derecha
        new_player = {"x": new_x, "y": new_y, "dir": new_dir}
        max_jugadores_alcanzado = False
        with mutex_players:
            if len(players) < max_jugadores:
                players[player_name] = new_player #agrega jugador al mapa
            else:
                max_jugadores_alcanzado = True
        if max_jugadores_alcanzado:
            error = "FAIL No se admiten mas jugadores\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

    except OSError:
        connectionSocket.close()
        return

    try:
        #mandar OK
        connectionSocket.sendall("OK\n".encode())

        #recibir comando LISTEN
        while not ("\n" in comandos):
            buff = connectionSocket.recv(4096).decode()
            if len(buff) == 0: #cliente cerro su socket
                with mutex_players:
                    players.pop(player_name) #borra al jugador
                connectionSocket.close()
                return
            comandos += buff
        comando_listen, comandos = comandos.split("\n", 1)

        if not re.search(r'^LISTEN (\d)+$', comando_listen):
            with mutex_players:
                players.pop(player_name) #borra al jugador
            error = "FAIL Comando no valido\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

        clientUDPPort = int(comando_listen.split()[1])
        if clientUDPPort < 1 or clientUDPPort > 65535:
            with mutex_players:
                players.pop(player_name) #borra al jugador
            error = "FAIL Numero de puerto no valido\n"
            connectionSocket.sendall(error.encode())
            connectionSocket.close()
            return

        clientIP = addr[0]
        with mutex_players:
            players[player_name]["addr"] = (clientIP, clientUDPPort)
        
        #mandar OK
        connectionSocket.sendall("OK\n".encode())

        #recibir comandos GO
        while True:
            while not ("\n" in comandos):
                buff = connectionSocket.recv(4096).decode()
                if len(buff) == 0: #cliente cerro su socket
                    with mutex_players:
                        players.pop(player_name) #borra al jugador
                    connectionSocket.close()
                    return
                comandos += buff
            comando_go, comandos = comandos.split("\n", 1)
            with mutex_players:
                if comando_go == "GO N":
                    players[player_name]["dir"] = "N"
                elif comando_go == "GO S":
                    players[player_name]["dir"] = "S"
                elif comando_go == "GO E":
                    players[player_name]["dir"] = "E"
                elif comando_go == "GO W":
                    players[player_name]["dir"] = "W"
                else:
                    #comando GO invalido
                    players.pop(player_name) #borra al jugador
                    connectionSocket.close()
                    return

    except OSError:
        with mutex_players:
                players.pop(player_name) #borra al jugador
        connectionSocket.close()
        return


mutex_players = allocate_lock()
players = {}
max_udp_payload = 512
v = 1
dt_sim = 0.01
dt_send = 0.1
map_size = 100

serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
rango_visual = int(sys.argv[3])
max_jugadores = int(sys.argv[4])
max_largo_nombre = int(sys.argv[5])

start_time = time()
Thread(target=simulacion_hilo).start()
Thread(target=mundo_hilo).start()

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen()
while True:
    connectionSocket, addr = serverSocket.accept()
    Thread(target=atender_jugador_hilo, args=(connectionSocket, addr)).start()
serverSocket.close()