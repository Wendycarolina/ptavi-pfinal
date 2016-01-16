#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import socket
import sys
import os
import json
import time
import random
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import uaclient


class XMLHandlerP(ContentHandler):
    def __init__(self):
        self.etiqueta = ['server', 'database', 'log']
        self.atributo = {'server': ['name', 'ip', 'puerto'],
                         'database': ['path', 'passwdpath'],
                         'log': ['path']}
        self.lista = []

    def startElement(self, name, attrs):
        dicc = {}
        if name in self.etiqueta:
            dicc['etiqueta'] = name
            for i in self.atributo[name]:
                dicc[i] = attrs.get(i, "")
            self.lista.append(dicc)

    def get_tags(self):
        return self.lista


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc = {}

    def register2json(self):
        """
        Registra o da de baja aun usuario
        """
        fich = json.dumps(self.dicc)
        with open('registered.json', 'w') as fich:
            json.dump(self.dicc, fich, sort_keys=True, indent=4)

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        ip = self.client_address[0]
        port = str(self.client_address[1])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea = line.decode('utf-8')
            if linea != '':
                fich_log.eventos('Received from', ip, port, linea)
                print(linea)
                if linea.split()[0] == 'REGISTER':
                    print('**********REGISTER*********')
                    #Creo y guardo datos usuario
                    Cabecera = linea.split('\r\n')
                    if 'Authorization' not in Cabecera[2]:
                        nonce = random.getrandbits(1024)
                        Unauthorized = b'SIP/2.0 401 Unauthorized\r\n'
                        Unauthorized += b'WWW Authenticate: Digest nonce='
                        Unauthorized += bytes(str(nonce), 'utf-8')
                        Unauthorized += b'\r\n\r\n'
                        self.wfile.write(Unauthorized)
                        mensaje = Unauthorized.decode('utf-8')
                        fich_log.eventos('Sent to', ip, port, mensaje)
                    elif 'Authorization' in Cabecera[2]:
                        Usuario = Cabecera[0].split(':')[1]
                        Expires = float(Cabecera[1].split(':')[1])
                        Time = time.time()
                        Time_exp = Time + Expires
                        fecha = '%Y-%m-%d %H:%M:%S'
                        Time_user = time.strftime(fecha, time.gmtime(Time_exp))
                        port_a = Cabecera[0].split(':')[2]
                        port_s = port_a.split(' ')[0]
                        Datos_User = [ip, port_s, Time_user]
                        self.dicc[Usuario] = Datos_User
                        #Compruebo si el usuario se ha expiradoo se da de baja
                        if Expires == 0:
                            del self.dicc[Usuario]
                        for User in self.dicc:
                            Time = time.time()
                            if Time >= Time_exp:
                                if Usuario in self.dicc:
                                    del self.dicc[Usuario]
                        self.register2json()
                        Ok = b'SIP/2.0 200 OK\r\n\r\n'
                        self.wfile.write(Ok)
                        Ok = Ok.decode('utf-8')
                        fich_log.eventos('Sent to', ip, port, Ok)
                elif linea.split()[0] == 'INVITE':
                    print('**********INVITE*********')
                    #Obtenemos dirección y comprobamos si esta registrado
                    Address = linea.split()[1].split(':')[1]
                    Encontrado = False
                    for User in self.dicc.keys():
                        if Address == User:
                            Encontrado = True
                    print('Usuario encontrado: ' + str(Encontrado))
                    if Encontrado:
                        ip_r = self.dicc[Address][0]
                        port_r = int(self.dicc[Address][1])
                        #Conectamos con el receptor
                        Sock1 = socket.SOCK_DGRAM
                        Sock2 = socket.SO_REUSEADDR
                        my_socket = socket.socket(socket.AF_INET, Sock1)
                        my_socket.setsockopt(socket.SOL_SOCKET, Sock2, 1)
                        my_socket.connect((ip_r, port_r))
                        my_socket.send(bytes(linea, 'utf-8'))
                        fich_log.eventos('Sent to', ip_r, port_r, linea)
                        try:
                            data = my_socket.recv(1024)
                            d = data.decode('utf-8')
                            print('Recibido:\r\n', d)
                            fich_log.eventos('Received from', ip_r, port_r, d)
                        except socket.error:
                            Error = 'Error: No server listening at '
                            sys.exit(Error + ip_r + ' port ' + str(port_r))
                        self.wfile.write(data)
                        data = data.decode('utf-8')
                        print('Enviando mensaje recibido:\r\n' + data)
                        fich_log.eventos('Sent to', ip_r, port_r, data)
                    else:
                        request = b'SIP/2.0 404 User Not Found\r\n'
                        self.wfile.write(request)
                        request = request.decode('utf-8')
                        fich_log.eventos('Sent to', ip, port, request)
                elif linea.split()[0] == 'BYE' or linea.split()[0] == 'ACK':
                    Address = linea.split()[1].split(':')[1]
                    if linea.split()[0] == 'BYE':
                        print('Terminando llamada con: ' + Address)
                    Encontrado = False
                    for User in self.dicc.keys():
                        if Address == User:
                            Encontrado = True
                    if Encontrado:
                        ip_r = self.dicc[Address][0]
                        port_r = int(self.dicc[Address][1])
                        #Conectamos con el receptor
                        Sock1 = socket.SOCK_DGRAM
                        Sock2 = socket.SO_REUSEADDR
                        my_socket = socket.socket(socket.AF_INET, Sock1)
                        my_socket.setsockopt(socket.SOL_SOCKET, Sock2, 1)
                        my_socket.connect((ip_r, port_r))
                        my_socket.send(bytes(linea, 'utf-8'))
                        fich_log.eventos('Sent to', ip_r, port_r, linea)
                        data = my_socket.recv(1024)
                        print('Recibido:\r\n', data.decode('utf-8'))
                        dat = data.decode('utf-8')
                        fich_log.eventos('Received from', ip_r, port_r, dat)
                        self.wfile.write(data)
                        dat = data.decode('utf-8')
                        fich_log.eventos('Sent to', ip, port, dat)
                    else:
                        request = b'SIP/2.0 404 User Not Found\r\n'
                        self.wfile.write(request)
                        request = request.decode('utf-8')
                        fich_log.eventos('Sent to', ip, port, request)
                elif linea.split()[0] not in List:
                    request = b'SIP/2.0 405 Method Not Allowed'
                    self.wfile.write(request)
                    request = request.decode('utf-8')
                    fich_log.eventos('Sent to', ip, port, request)
                else:
                    request = b'SIP/2.0 400 Bad Request\r\n'
                    self.wfile.write(request)
                    request = request.decode('utf-8')
                    fich_log.eventos('Sent to', ip, port, request)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    #Argumentos proxy
    try:
        Config = sys.argv[1]
        List = ['REGISTER', 'INVITE', 'ACK', 'BYE']
        if len(sys.argv) != 2:
            print('Usage: python uaserver.py config')
            raise SystemExit
    except IndexError:
        sys.exit('Usage: python proxy_registrar.py config')

    parser = make_parser()
    xml_hand = XMLHandlerP()
    parser.setContentHandler(xml_hand)
    try:
        parser.parse(open(Config))
    except IOError:
        sys.exit('Usage: python uaclient.py config method option')
    #Datos
    for dicc in xml_hand.lista:
        if dicc['etiqueta'] == 'server':
            print("server")
            name = dicc['name']
            ip_px = dicc['ip']
            port_px = int(dicc['puerto'])
        elif dicc['etiqueta'] == 'database':
            user_path = dicc['path']
            passwd_path = dicc['passwdpath']
        elif dicc['etiqueta'] == 'log':
            log_path = dicc['path']
    serv = socketserver.UDPServer((ip_px, port_px), SIPRegisterHandler)
    fich_log = uaclient.Log(log_path)
    fich_log.eventos('Starting', '', '', '')
    MyServer = 'Server MiServidorBingBang listening at port '
    print(MyServer + str(port_px) + '...')
    serv.serve_forever()
