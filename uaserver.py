#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import uaclient


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
            #Datos para poder responder cliente o proxi
            ip_client = self.client_address[0]
            port_client = self.client_address[1]
            fich_log.eventos('Received from',ip_client , port_client, linea)
            if linea != '':
                Metodo = linea.split()[0]
                print(Metodo)
                #Mensajes que envío
                if Metodo == 'INVITE':
                    print('****************INVITE*******')
                    message = b'SIP/2.0 100 TRYING\r\n\r\n'
                    message +=b'SIP/2.0 180 RINGING\r\n\r\n'
                    message += b'SIP/2.0 200 OK\r\n'
                    cabecera = b'Content-Type: application/sdp\r\n\r\n'
                    #Estructura SDP
                    sdp = 'v=0\r\n' + 'o=' + username + ' ' + ip_client + '\r\n' \
                     + 's=MiSesion\r\n' + 't=0\r\n' + 'm=audio ' + str(port_rtp) + ' RTP'
                    message = message + cabecera + bytes(sdp, 'utf-8')
                    self.wfile.write(message)
                    print(message)
                    fich_log.eventos('Sent to',ip_client , port_client, message)
                elif Metodo == 'ACK':
                    #ip y puerto obtenidos mediante descripción de la sesion (SDP)
                    #REVISAR!!!!!!!!!!
                    aEjecutar = './mp32rtp -i ' + ip_client + ' -p ' + port_rtp
                    aEjecutar += '<' + audio_path
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                    fich_log.eventos('Sent to', ip_client, + port_rtp, 'audio')
                    
                elif Metodo == 'BYE':
                    print('***********BYE*********')
                    message = b'SIP/2.0 200 OK\r\n\r\n'
                    self.wfile.write(message)
                    fich_log.eventos('Sent to',ip_client , port_client, message)
                elif not Metodo in List:
                    message = b'SIP/2.0 405 Method Not Allowed'
                    self.wfile.write(message)
                    fich_log.eventos('Sent to',ip_client , port_client, message)
                else:
                    message = b'SIP/2.0 400 Bad Request\r\n'
                    self.wfile.write(message)
                    fich_log.eventos('Sent to',ip_client , port_client, message)
            else:
                break


if __name__ == "__main__":
    #Argumentos del servidor
    try:
        Config = sys.argv[1]
        List = ['INVITE', 'ACK', 'BYE']
        if len(sys.argv) != 2:
            print('Usage: python uaserver.py config')
            raise SystemExit
    except IndexError:
        sys.exit('Usage: python uaserver.py config')
    
    parser = make_parser()
    xml_hand = XMLHandler()
    parser.setContentHandler(xml_hand)
    try:
        parser.parse(open(Config))
    except IOError:
        sys.exit('Usage: python uaserver.py config')
    #Obtengo datos
    for dicc in xml_hand.lista:
         if dicc['name'] == 'account':
             username = dicc['username']
             passwd = dicc['passwd']
         elif dicc['name'] == 'uaserver':
             ip_server = dicc['ip']
             port_server = int(dicc['puerto'])
         elif dicc['name'] == 'rtpaudio':
             port_rtp = int(dicc['puerto'])
         elif dicc['name'] == 'regproxy':
             ip_px = dicc['ip']
             port_px = int(dicc['puerto'])
         elif dicc['name'] == 'log':
             log_path = dicc['path']
         elif dicc['name'] == 'audio':
             audio_path = dicc['path']

    serv = socketserver.UDPServer((ip_server, port_server), EchoHandler)
    fich_log = uaclient.Log(log_path)
    fich_log.eventos('Starting','', '', '')
    print("Listening...")
    serv.serve_forever()

#-------------------------DUDAS----------------------------


