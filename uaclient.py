#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import hashlib
import os
import time
import uaserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class Log:
    
    def __init__(self,fich_log):
    
        self.fich_log = fich_log

    def eventos(self, evento, ip, port, messag):
    #Eventos : escribe en el log
        log = open(self.fich_log, 'a')
        Time = time.time()
        fecha = '%Y-%m-%d %H:%M:%S'
        Time_user = time.strftime(fecha, time.gmtime(Time))
        if evento == 'Starting':
            lines = Time_user + ' Starting...'
        elif evento == 'Finishing':
            lines = Time_user + ' Finishing.'
        elif evento == 'Sent to':
            lines = Time_user + ' ' + evento + ':' + str(port) + ':' + str(messag)
        elif evento == 'Received from':
            lines = Time_user + ' ' + evento + ' ' + ip + ':' + str(port) + ':' + messag
        elif evento == 'Error':
            lines = Time_user + '' + evento + messag.decode('utf-8')
        else:
            lines = "Error: algo raro pasa aqui " + evento + " " + ip + " " + port + " " + str(messag)
        log.write(lines+ '\r\n')    
        log.close()


if __name__ == "__main__":
    # Argumentos que introduce el cliente.
    try:
        Config = sys.argv[1]
        METODO = sys.argv[2].upper()
        if METODO == 'REGISTER':
            Option = int(sys.argv[3])
        elif METODO == 'INVITE' or 'BYE':
            Option = str(sys.argv[3])
            if '@' not in Option:
                print('Usage: python uaclient.py config method option')
                raise SystemExit
        if len(sys.argv) != 4:
            print('Usage: python uaclient.py config method option')
            raise SystemExit
    except IndexError:
        print('Usage: python uaclient.py config method option')
        raise SystemExit
    except ValueError:
        print('Usage: python uaclient.py config method option')
        raise SystemExit

    parser = make_parser()
    xml_hand = uaserver.XMLHandler()
    parser.setContentHandler(xml_hand)
    try:
        parser.parse(open(Config))
    except IOError:
        sys.exit('Usage: python uaclient.py config method option')

    #Datos para conectar con el proxy y servidor
    for dicc in xml_hand.lista:
         if dicc['name'] == 'account':
             username = dicc['username']
             passwd = dicc['passwd']
         elif dicc['name'] == 'uaserver':
             ip_server = dicc['ip']
             port_server = dicc['puerto']
         elif dicc['name'] == 'rtpaudio':
             port_rtp = int(dicc['puerto'])
         elif dicc['name'] == 'regproxy':
             ip_px = dicc['ip']
             port_px = int(dicc['puerto'])
         elif dicc['name'] == 'log':
             log_path = dicc['path']
         elif dicc['name'] == 'audio':
             audio_path = dicc['path']
    print(ip_px)
    print(port_px)
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto del proxi
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((ip_px, port_px))

    #Creamos log
    fich_log = Log(log_path)
    #Formamos peticiones
    if METODO == 'REGISTER':
         request = METODO + ' sip:' + username + ':' + str(port_server) + ' SIP/2.0\r\n'
         cabecera = 'Expires: ' + str(Option) + '\r\n\r\n'
         request_t = request + cabecera
 
    elif METODO == 'INVITE':
         request = METODO + ' sip:' + Option + ' SIP/2.0\r\n'
         cabecera = 'Content-Type: application/sdp\r\n\r\n'
        #Estructura SDP
         sdp = 'v=0\r\n' + 'o=' + username + ' ' + ip_server + '\r\n' \
             + 's=MiSesion\r\n' + 't=0\r\n' + 'm=audio ' + str(port_rtp)\
             + ' RTP'
         request_t = request + cabecera + sdp
    elif METODO == 'BYE':
         request_t = METODO + ' sip:' + Option + ' SIP/2.0\r\n\r\n'
    #Enviamos petición
    my_socket.send(bytes(request_t,'utf-8'))
    fich_log.eventos('Sent to',ip_px, str(port_px), request_t)
    try:
        #Vemos lo que recibimos
        data = my_socket.recv(1024)
        print('Recibido -- ', data.decode('utf-8'))
        fich_log.eventos('Received from', ip_px, port_px, data.decode('utf-8'))
        Data = data.split()
        print(METODO)
        if METODO == 'REGISTER':
            Authorization = Data[2].decode('utf-8')
            if Authorization == 'Unauthorized':
                pas = Data[5].decode('utf-8')
                nonce = pas.split('=')[1]
                print('--------' + nonce)
                request = METODO + ' sip:' + username + ':' + str(port_server) + ' SIP/2.0\r\n'
                cabecera = 'Expires: ' + str(Option) + '\r\n'
                m = hashlib.md5()
                #---------------------REVISAR SI NONCE ESTA EN BYTES------------------
                m.update(bytes(passwd + nonce, 'utf-8'))
                response = m.hexdigest()
                Authorization = 'Authorization: response=' + response
                request_t = request + cabecera + Authorization
                my_socket.send(bytes(request_t,'utf-8'))
                fich_log.eventos('Sent to', ip_px, port_px, request_t)
                dato = my_socket.recv(1024)
                print(dato.decode('utf-8'))


        elif METODO == 'INVITE':
            Trying = Data[1].decode('utf-8')
            print('******INVITE*****')
            print(Data)
            if Trying == '100':
                Ring = Data[4].decode('utf-8')
                Ok = Data[7].decode('utf-8')
                if Ring == '180' and Ok == '200':
                #------------REVISAR SDP----------------------------
                    fich_log.eventos('Received from', ip_px, port_px, Trying)
                    fich_log.eventos('Received from', ip_px, port_px, Ring)
                    fich_log.eventos('Received from', ip_px, port_px, Ok)
                    request = 'ACK sip:' + Option + ' SIP/2.0'
                    print("Enviando: " + request)
                    my_socket.send(bytes(request,'utf-8'))
                    fich_log.eventos('Sent to', ip_px, port_px, request) 
                    Ip_serv = Data[13].decode('utf-8')
                    print(Ip_serv)
                    port = Data[17].decode('utf-8')
                    print(port)
                    aEjecutar = './mp32rtp -i ' + Ip_serv + ' -p ' + port
                    aEjecutar += '<' + audio_path
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                    fich_log.eventos('Sent to', Ip_serv, port, 'audio')
            elif Trying == '404':
                print(Data)
                fich_log.eventos('Received from', ip_px, port_px, data.decode('utf-8'))
       
        else:
            print(data)
        # Cerramos todo
        my_socket.close()
        print("Fin.")
    except socket.error:
        sys.exit('Error: No server listening at port ' + str(port_server))

#Error en el proxy del uaclient line referenced before..

