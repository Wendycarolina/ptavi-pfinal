#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XMLHandler(ContentHandler):
    def __init__(self):
        self.etiqueta = ['account', 'uaserver', 'rtpaudio', 'regproxy', 'log', 'audio']
        self.atributo = {'account': ['username', 'passwd'],
                         'uaserver': ['ip', 'puerto'],
                         'rtpaudio': ['puerto'],
                         'regproxy': ['ip', 'puerto'],
                         'log': ['path'],
                         'audio' : ['path']}
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

class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea = line.decode('utf-8')
            print("El cliente nos manda " + linea)
            if linea != '':
                Metodo = linea.split()[0]
                IP = self.client_address[0]
                print(Metodo)
                #Mensajes que envío
                if Metodo == 'INVITE':
                    message = b'SIP/2.0 ' + b'100 TRYING' + b'\r\n\r\n'
                    message += b'SIP/2.0 ' + b'180 RINGING' + b'\r\n\r\n'
                    message += b'SIP/2.0 ' + b'200 OK' + b'\r\n\r\n'
                    self.wfile.write(message)
                elif Metodo == 'ACK':
                    #ejecutar en la shell
                    aEjecutar = './mp32rtp -i ' + IP + ' -p 23032 < ' + AUDIO
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                elif Metodo == 'BYE':
                    message = b'SIP/2.0 ' + b'200 OK' + b'\r\n\r\n'
                    self.wfile.write(message)
                elif not Metodo in List:
                    message = b'SIP/2.0 ' + b'405 Method Not Allowed'
                    self.wfile.write(message)
                else:
                    message = b'SIP/2.0 ' + b'400 Bad Request' + b'\r\n'
                    self.wfile.write(message)
            else:
                break


if __name__ == "__main__":
    #Argumentos del servidor
    try:
        IP = sys.argv[1]
        PORT = int(sys.argv[2])
        AUDIO = sys.argv[3]
        List = ['INVITE', 'ACK', 'BYE']
        if len(sys.argv) != 4 or not os.path.exists(AUDIO):
            print('Usage: python server.py IP port audio_file')
            raise SystemExit
    except IndexError:
        sys.exit('Usage: python server.py IP port audio_file')

    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
