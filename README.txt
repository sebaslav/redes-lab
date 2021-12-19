Se describe la serie de pasos que debe seguir tanto un cliente como un servidor para hacer uso del juego.


--Servidor--

Para iniciar un servidor se debe ejecutar el comando:

python servidor.py <server_IP> <server_Port> <rango_visual> <max_jugadores> <max_largo_nombre>

<server_IP> es el nombre de host o la dirección IP donde el server acepta conexiones
<server_Port> es el número de puerto donde el servidor acepta conexiones
<rango_visual> es un número que representa el rango visual de cada jugador en el mapa (entre 0 y 150)
<max_jugadores> es el número máximo de jugadores que pueden estar conectados simultáneamente al servidor
<max_largo_nombre> es el número máximo de caracteres que puede tener el nombre de un jugador


--Cliente--

Por otro lado, para un cliente poder conectarse debe existir previamente un servidor levantado. Se ejecuta el siguiente comando:

python cliente.py <server_IP> <server_Port> <player_name>

<server_IP> es el nombre de host o la dirección IP del servidor
<server_Port> es el número de puerto donde el servidor acepta conexiones
<player_name> es el nombre del jugador el cual consiste solamente de caracteres alfanuméricos

El cliente abre una ventana donde se visualiza el mapa del juego y los jugadores dentro del rango visual.

El jugador puede controlar su avatar utilizando las flechas del teclado (teclas "up',"down","left" y "right"), desplazándose por el mapa. Cuando se desee, se puede salir de la partida apretando la tecla "q".

A efectos de facilitar el testeo de mas de un cliente en la misma máquina, se implementó una versión del cliente llamada clienteWASD.py, la cual solo se diferencia del primero en los inputs que recibe del teclado.
Para mover al jugador deben apretarse las teclas "w", "a", "s" y "d", y para finalizar el cliente se aprieta la tecla "x".


--Bots--

Se implementaron además 3 bots que actúan como clientes moviéndose de forma autónoma.
clienteBotCuadrado.py se mueve dibujando un cuadrado en pantalla.
clienteBotZigZag.py se mueve en zig zag con dirección general hacia la derecha.
clienteBotRandom.py se mueve de manera aleatoria en el mapa.

Los bots se ejecutan desde una terminal especificando los mismos parámetros que un cliente normal.