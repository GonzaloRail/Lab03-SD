#!/usr/bin/env python3
# client.py

import socket
import pickle
import threading
import sys
from chat_message import ChatMessage

class Client:
    """Cliente que se puede ejecutar como una aplicación de consola"""
    
    def __init__(self, server, port, username):
        """
        Constructor para configurar el cliente
        :param server: dirección del servidor
        :param port: número de puerto
        :param username: nombre de usuario
        """
        self.server = server
        self.port = port
        self.username = username
        self.socket = None
        self.notif = " * "  # para notificaciones
    
    def get_username(self):
        """Retorna el nombre de usuario"""
        return self.username
    
    def set_username(self, username):
        """Establece el nombre de usuario"""
        self.username = username
    
    def start(self):
        """Inicia la conexión con el servidor"""
        # Intenta conectarse al servidor
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server, self.port))
        except Exception as e:
            self.display(f"Error al conectarse al servidor: {e}")
            return False
        
        msg = f"Conexión aceptada {self.socket.getpeername()[0]}:{self.socket.getpeername()[1]}"
        self.display(msg)
        
        # Envía el nombre de usuario al servidor
        try:
            # Primero enviamos el username serializado como objeto
            self.socket.sendall(pickle.dumps(self.username))
        except Exception as e:
            self.display(f"Excepción durante el login: {e}")
            self.disconnect()
            return False
        
        # Crea un hilo para escuchar mensajes del servidor
        listen_thread = threading.Thread(target=self.listen_from_server)
        listen_thread.daemon = True
        listen_thread.start()
        
        return True
    
    def display(self, msg):
        """Muestra un mensaje en la consola"""
        print(msg)
    
    def send_message(self, msg):
        """Envía un mensaje al servidor"""
        try:
            self.socket.sendall(pickle.dumps(msg))
        except Exception as e:
            self.display(f"Excepción al escribir al servidor: {e}")
    
    def disconnect(self):
        """Cierra la conexión cuando algo sale mal"""
        try:
            if self.socket:
                self.socket.close()
        except Exception as e:
            pass  # Si hay error al cerrar no hacemos nada
    
    def listen_from_server(self):
        """Método que escucha mensajes del servidor"""
        while True:
            try:
                # Lee el mensaje del stream de entrada
                data = self.socket.recv(4096)
                if not data:
                    self.display(f"{self.notif}Servidor ha cerrado la conexión{self.notif}")
                    break
                
                msg = pickle.loads(data)
                print(msg)
                print("> ", end="", flush=True)  # Para mantener el prompt
            except EOFError:
                self.display(f"{self.notif}Servidor ha cerrado la conexión{self.notif}")
                break
            except Exception as e:
                self.display(f"{self.notif}Error: {e}{self.notif}")
                break

def main():
    """Función principal para iniciar el cliente"""
    # Valores por defecto
    port_number = 1500
    server_address = "localhost"
    username = "Anónimo"
    
    # Obtener nombre de usuario
    username = input("Ingresa tu nombre de usuario: ")
    
    # Procesar argumentos de línea de comandos si existen
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port_number = int(sys.argv[2])
        except ValueError:
            print("Número de puerto inválido.")
            print("Uso: > python client.py [usuario] [puerto] [direccionServidor]")
            return
    if len(sys.argv) > 3:
        server_address = sys.argv[3]
    
    # Crear el objeto Cliente
    client = Client(server_address, port_number, username)
    
    # Intentar conectarse al servidor
    if not client.start():
        return
    
    print("\n¡Hola! Bienvenido a la sala de chat.")
    print("Instrucciones:")
    print("1. Simplemente escribe el mensaje para enviarlo a todos los clientes activos")
    print("2. Escribe '@usuario mensaje' sin comillas para enviar un mensaje al cliente deseado")
    print("3. Escribe 'WHOISIN' sin comillas para ver la lista de clientes activos")
    print("4. Escribe 'LOGOUT' sin comillas para desconectarse del servidor")
    
    # Bucle infinito para obtener la entrada del usuario
    while True:
        print("> ", end="", flush=True)
        # Leer mensaje del usuario
        msg = input()
        
        # Logout si el mensaje es LOGOUT
        if msg.upper() == "LOGOUT":
            client.send_message(ChatMessage(ChatMessage.LOGOUT, ""))
            break
        # Mensaje para verificar quién está en la sala de chat
        elif msg.upper() == "WHOISIN":
            client.send_message(ChatMessage(ChatMessage.WHOISIN, ""))
        # Mensaje de texto regular
        else:
            client.send_message(ChatMessage(ChatMessage.MESSAGE, msg))
    
    # Cliente completó su trabajo. Desconectar cliente.
    client.disconnect()

if __name__ == "__main__":
    main()