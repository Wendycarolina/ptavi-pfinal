#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import hashlib
import os

# Argumentos que introduce el cliente.
try:
    Config = sys.argv[1]
    METODO = sys.argv[2].upper()
    if METODO = 'REGISTER':
        Option = int(sys.argv[3])
    elif METODO = 'INVITE' or 'BYE':
        Option = str(sys.argv[3])
        if '@' not in Option:
            print('Usage: python uaclient.py config method option')
            raise SystemExit
    if len(sys.argv) != 3:
        print('Usage: python uaclient.py config method option')
        raise SystemExit
except IndexError:
    print 'Usage: python uaclient.py config method option'
    raise SystemExit
except ValueError:
    print 'Usage: python uaclient.py config method option'
    raise SystemExit

#------------------------------CAMBIAR--------------------
#Falta ip y puerto para conectar
# Contenido que vamos a enviar
LINE = METODO + ' sip:' + ADDRESS + ' SIP/2.0' + '\r\n'


# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP, PORT))

#-------------------------------------------------------
try:
    #Formamos peticiones
    if METODO = 'REGISTER':
         request = METODO + ' sip:' + username + ':' \
             + str(port_server) + ' SIP/2.0\r\n'
         cabecera = 'Expires: ' + Option + '\r\n\r\n'
         request_t = request + cabecera
 
    elif METODO == 'INVITE':
         request = METODO + ' sip:' + OPCION + ' SIP/2.0\r\n'
         cabecera = 'Content-Type: application/sdp\r\n\r\n'
    #Estructura SDP
         sdp = 'v=0\r\n' + 'o=' + username + ' ' + ip_server + '\r\n' \
             + 's=MiSesion\r\n' + 't=0\r\n' + 'm=audio ' + str(port_rtp) \
             + ' RTP'
         request_t = request + cabecera + sdp
 
    elif METODO == 'BYE':
         request_t = METODO + ' sip:' + Option + ' SIP/2.0\r\n\r\n'
    #Enviamos petición
    my_socket.send(request)
    #------------------Meter LOG-------------

try:
    #Vemos lo que recibimos
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))
    Data = data.split()
    Trying = Data[1].decode('utf-8')
    Ring = Data[4].decode('utf-8')
    Ok = Data[7].decode('utf-8')
    #Respuesta si recibe un Trying, Ring y OK
    if Trying == '100':
        if Ring == '180' and Ok == '200':
            request = 'ACK' + ' sip:' + ADDRESS + ' SIP/2.0'
            print("Enviando: " + request)
            my_socket.send(request)
    #---------------------Meter log------------
    #para autentificar
    elif Trying == '401':
        request = METODO + ' sip:' + username + ':' \
             + str(port_server) + ' SIP/2.0\r\n'
         cabecera = 'Expires: ' + Option + '\r\n'
         m = hashlib.md5()
         m.update(passwd + nonce)
         response = m.hexdigest()
         Authorization = 'Authorization:' + 'response=' + response
         request_t = request + cabecera + Authorization
         my_socket.send(request_t)



    # Cerramos todo
    my_socket.close()
    print("Fin.")
except socket.error:
    sys.exit('Error: No server listening at ' + SERVER + ' port ' + str(PORT))
