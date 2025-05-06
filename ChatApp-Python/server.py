#!/usr/bin/env python3
# server.py

import socket
import pickle
import threading
import sys
import time
from datetime import datetime
from chat_message import ChatMessage

class ClientThread(threading.Thread):
    """Un hilo para manejar cada cliente conectado"""
    
    def __init__(self, server, socket, unique_id):
        """
        Constructor para el hilo de cliente
        :param server: Referencia al servidor
        :param socket: Socket del cliente
        :param unique_id: ID único para este cliente
        """
        threading.Thread.__init__(self)
        self.server = server
        self.socket = socket
        self.id = unique_id
        self.username = ""
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Recibir el nombre de usuario del cliente
        try:
            data = socket.recv(4096)
            self.username = pickle.loads(data)
            self.server.broadcast(f"{server.notif}{self.username} se ha unido a la sala de chat.{server.notif}")
        except Exception as e:
            self.server.display(f"Error al crear streams de entrada/salida: {e}")
            return
    
    def get_username(self):
        """Retorna el nombre de usuario"""
        return self.username
    
    def set_username(self, username):
        """Establece el nombre de usuario"""
        self.username = username
    
    def run(self):
        """Bucle infinito para leer y reenviar mensajes"""
        # Bucle hasta LOGOUT
        keep_going = True
        while keep_going:
            # Leer un objeto del cliente
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                cm = pickle.loads(data)
                
                # Obtener el mensaje del objeto ChatMessage recibido
                message = cm.get_message()
                
                # Diferentes acciones basadas en el tipo de mensaje
                if cm.get_type() == ChatMessage.MESSAGE:
                    confirmation = self.server.broadcast(f"{self.username}: {message}", self)
                    if not confirmation:
                        msg = f"{self.server.notif}Lo siento. No existe dicho usuario.{self.server.notif}"
                        self.write_msg(msg)
                
                elif cm.get_type() == ChatMessage.LOGOUT:
                    self.server.display(f"{self.username} se desconectó con un mensaje LOGOUT.")
                    keep_going = False
                
                elif cm.get_type() == ChatMessage.WHOISIN:
                    self.write_msg(f"Lista de usuarios conectados a {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Enviar lista de clientes activos
                    for i, client in enumerate(self.server.clients):
                        self.write_msg(f"{i+1}) {client.username} desde {client.date}")
            
            except Exception as e:
                self.server.display(f"{self.username} Excepción leyendo streams: {e}")
                break
        
        # Si sale del bucle, entonces se desconecta y elimina de la lista de clientes
        self.server.remove(self.id)
        self.close()
    
    def close(self):
        """Cierra todo"""
        try:
            if self.socket:
                self.socket.close()
        except Exception as e:
            pass
    
    def write_msg(self, msg):
        """Escribe un mensaje al stream de salida del cliente"""
        # Si el cliente todavía está conectado, envía el mensaje
        try:
            self.socket.sendall(pickle.dumps(msg))
            return True
        except Exception as e:
            self.server.display(f"{self.server.notif}Error al enviar mensaje a {self.username}{self.server.notif}")
            self.server.display(str(e))
            return False

class Server:
    """El servidor que puede ejecutarse como una aplicación de consola"""
    
    # Un ID único para cada conexión
    unique_id = 0
    
    def __init__(self, port):
        """
        Constructor que recibe el puerto para escuchar conexiones
        :param port: Número de puerto
        """
        self.port = port
        self.clients = []  # Lista para mantener los hilos de clientes
        self.keep_going = False
        self.notif = " * "  # para notificaciones
    
    def start(self):
        """Inicia el servidor"""
        self.keep_going = True
        
        # Crear socket del servidor y esperar solicitudes de conexión
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('', self.port))
            server_socket.listen(10)
            
            # Bucle infinito para esperar conexiones (hasta que el servidor esté activo)
            while self.keep_going:
                self.display(f"Servidor esperando clientes en el puerto {self.port}.")
                
                # Acepta conexión si es solicitada por un cliente
                client_socket, client_address = server_socket.accept()
                
                # Rompe si el servidor se detuvo
                if not self.keep_going:
                    break
                
                # Si el cliente está conectado, crea su hilo
                Server.unique_id += 1
                t = ClientThread(self, client_socket, Server.unique_id)
                
                # Agrega este cliente al array
                self.clients.append(t)
                t.start()
            
            # Intenta detener el servidor
            try:
                server_socket.close()
                for client in self.clients:
                    client.close()
            except Exception as e:
                self.display(f"Excepción al cerrar el servidor y los clientes: {e}")
                
        except Exception as e:
            self.display(f"Excepción en nuevo ServerSocket: {e}")
    
    def stop(self):
        """Detiene el servidor"""
        self.keep_going = False
        try:
            # Conectamos brevemente al socket para desbloquear el accept()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', self.port))
            s.close()
        except Exception as e:
            pass
    
    def display(self, msg):
        """Muestra un evento en la consola"""
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"{time_str} {msg}")
    
    def broadcast(self, message, sender=None):
        """
        Envía un mensaje a todos los clientes
        :param message: mensaje a enviar
        :param sender: remitente del mensaje (None si es del servidor)
        :return: True si se envió correctamente
        """
        # Agregar marca de tiempo al mensaje
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Para verificar si el mensaje es privado, es decir, mensaje de cliente a cliente
        words = message.split(" ", 2)
        is_private = False
        
        if len(words) > 1 and words[1].startswith('@'):
            is_private = True
        
        # Si es un mensaje privado, envía el mensaje solo al nombre de usuario mencionado
        if is_private:
            to_check = words[1][1:]  # Quita el @ del principio
            
            if len(words) > 2:
                message = words[0] + " " + words[2]
            else:
                message = words[0]
                
            message_with_time = f"{time_str} {message}"
            found = False
            
            # Recorremos en orden inverso para encontrar el nombre de usuario mencionado
            for i in range(len(self.clients) - 1, -1, -1):
                client = self.clients[i]
                check = client.get_username()
                
                if check == to_check:
                    # Intenta escribir al cliente, si falla lo elimina de la lista
                    if not client.write_msg(message_with_time):
                        self.clients.pop(i)
                        self.display(f"Cliente desconectado {client.username} eliminado de la lista.")
                    
                    # Nombre de usuario encontrado y mensaje entregado
                    found = True
                    break
            
            # Usuario mencionado no encontrado, devuelve False
            if not found:
                return False
        
        # Si el mensaje es un mensaje de difusión
        else:
            message_with_time = f"{time_str} {message}"
            
            # Imprime el mensaje
            print(message_with_time)
            
            # Recorremos en orden inverso en caso de que tengamos que eliminar un cliente
            # porque se ha desconectado
            for i in range(len(self.clients) - 1, -1, -1):
                client = self.clients[i]
                
                # Intenta escribir al cliente, si falla lo elimina de la lista
                if not client.write_msg(message_with_time):
                    self.clients.pop(i)
                    self.display(f"Cliente desconectado {client.username} eliminado de la lista.")
        
        return True
    
    def remove(self, id):
        """
        Elimina un cliente si envió mensaje LOGOUT para salir
        :param id: ID del cliente a eliminar
        """
        disconnected_client = ""
        
        # Escanea la lista de arrays hasta encontrar el ID
        for i, client in enumerate(self.clients):
            # Si lo encuentra, lo elimina
            if client.id == id:
                disconnected_client = client.get_username()
                self.clients.pop(i)
                break
        
        self.broadcast(f"{self.notif}{disconnected_client} ha abandonado la sala de chat.{self.notif}")

def main():
    """Función principal para iniciar el servidor"""
    # Inicia el servidor en el puerto 1500 a menos que se especifique un número de puerto
    port_number = 1500
    
    # Procesar argumentos de línea de comandos
    if len(sys.argv) > 1:
        try:
            port_number = int(sys.argv[1])
        except ValueError:
            print("Número de puerto inválido.")
            print("Uso: > python server.py [puerto]")
            return
    
    # Crear un objeto de servidor e iniciarlo
    server = Server(port_number)
    server.start()

if __name__ == "__main__":
    main()