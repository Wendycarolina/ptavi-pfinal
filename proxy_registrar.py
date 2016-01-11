#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
import random
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import uaclient


class XMLHandler(ContentHandler):
    def __init__(self):
        self.etiqueta = ['server', 'database', 'log']
        self.atributo = {'server': ['name', 'ip', 'puerto'],
                         'database': ['path', 'passwdpath'],
                         'log': ['path']}
        self.lista = []

    def startElement(self, name, attrs):
        dicc = {}
        if name in self.etiqueta:
            dicc['name'] = name
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

    def json2registered(self):
        """
        Comprueba si existe un archivo
        """
        if os.path.exists('registered.json'):
            self.dicc = json.loads(open('registered.json').read())
        else:
            self.dicc = {}

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        #self.json2registered()
        ip = self.client_address[0]
        port = str(self.client_address[1]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            fich_log.eventos('Receiving from', ip, port, line)
            linea = line.decode('utf-8')
            if linea.split()[0] == 'REGISTER':
                #Creo y guardo datos usuario
                Cabecera = linea.split('\r\n',:2)
                if 'Authorization' not in Cabecera:
                    nonce = random.getrandbits(1024)
                    Unauthorized = b'SIP/2.0 401 Unauthorized\r\n'
                    Unauthorized += b'WWW Authenticate: nonce=' + nonce
                    self.wfile.write(Unauthorized)
                elif 'Authorization' in Cabecera:
                    IP = self.client_address[0]
                    Expires = float(linea.split(':')[-1])
                    Time = time.time()
                    Time_exp = Time + Expires
                    fecha = '%Y-%m-%d %H:%M:%S'
                    Time_user = time.strftime(fecha, time.gmtime(Time_exp))
                    Datos_User = [IP, port, Time_user]
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
                    self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
            elif line.split()[0] == 'INVITE':
                #Obtenemos dirección y comprobamos si esta registrado
                Address = linea.split()[1].split(':')[1]
                Encontrado = False
                for User in dicc.keys():
                    if Address = User:
                        Encontrado = True
                if Encontrado = True:
                    ip_r = dicc[Address][0]
                    port_r = int(dicc[Address][1])
                    #Conectamos con el receptor
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip_r, port_r))
                    my_socket.send(bytes(linea,'utf-8'))
                    fich_log.eventos('Sent to',ip_r , port_r, linea)
                    try:
                        data = my_socket.recv(1024)
                        print('Recibido -- ', data.decode('utf-8'))
                        fich_log.eventos('Receiving from',ip_r , port_r, data)
                    except socket.error:
                        sys.exit('Error: No server listening at '+ ip_r + ' port ' + str(port_r))
                    self.wfile.write(data)
                    fich_log.eventos('Sent to',ip_r , port_r, data)
                else:
                    request = b'SIP/2.0 404 User Not Found\r\n'
                    self.wfile.write(request)
                    fich_log.eventos('Sent to',ip , port, request)
            elif line.split()[0] == 'BYE' or 'ACK':
                Address = linea.split()[1].split(':')[1]
                Encontrado = False
                for User in dicc.keys():
                    if Address = User:
                        Encontrado = True
                if Encontrado = True:
                    ip_r = dicc[Address][0]
                    port_r = int(dicc[Address][1])
                    #Conectamos con el receptor
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip_px, port_px))
                    my_socket.send(bytes(linea,'utf-8'))
                    fich_log.eventos('Sent to',ip_r , port_r, linea)
                else:
                    request = b'SIP/2.0 404 User Not Found\r\n'
                    self.wfile.write(request)
                    fich_log.eventos('Sent to',ip , port, request)
            elif line.split()[0] not in List:
                request = b'SIP/2.0 405 Method Not Allowed'
                self.wfile.write(request)
                fich_log.eventos('Sent to',ip , port, request)
            else:
                request = b'SIP/2.0 400 Bad Request\r\n'
                self.wfile.write(request)
                fich_log.eventos('Sent to',ip , port, request)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    #Argumentos proxy
    Config = sys.argv[1]
    List = ['REGISTER','INVITE', 'ACK', 'BYE']
        if len(sys.argv) != 1:
            print('Usage: python uaserver.py config')
            raise SystemExit
    except IndexError:
        sys.exit('Usage: python proxy_registrar.py config')

    parser = make_parser()
    xml_hand = XMLHandler()
    parser.setContentHandler(xml_hand)
    try:
        parser.parse(open(Config))
    except IOError:
        sys.exit('Usage: python uaclient.py config method option')
    #Datos
    for dicc in xml_hand.lista:
        if dicc['name'] == 'server':
            name = dicc['name']
            ip_px = dicc['ip']
            port_px = int(dicc['puerto'])
        elif dic['name'] == 'database':
            user_path = dicc['path']
            passwd_path = dicc['passwdpath']
        elif dicc['name'] == 'log':
            log_path = dicc['path']

    serv = socketserver.UDPServer((ip_px, port_px ), SIPRegisterHandler)
    fich_log = uaclient.Log(log_path)
    fich_log.eventos('Starting','', '', '')
    print('Server MiServidorBingBang listening at port ' + str(port_px) + '...')
    serv.serve_forever()





