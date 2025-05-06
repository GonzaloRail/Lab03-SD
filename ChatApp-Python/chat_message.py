#!/usr/bin/env python3
# chat_message.py

import pickle

class ChatMessage:
    """
    Define los diferentes tipos de mensajes que se intercambiarán entre los clientes y el servidor.
    Para comunicación entre clientes y servidor en Python usaremos pickle para serializar los objetos.
    """
    
    # Tipos de mensajes que el cliente puede enviar
    # WHOISIN para recibir la lista de usuarios conectados
    # MESSAGE para un mensaje de texto ordinario
    # LOGOUT para desconectarse del servidor
    WHOISIN = 0
    MESSAGE = 1
    LOGOUT = 2
    
    def __init__(self, msg_type, message):
        """
        Constructor
        :param msg_type: Tipo de mensaje (WHOISIN, MESSAGE, LOGOUT)
        :param message: Contenido del mensaje
        """
        self.type = msg_type
        self.message = message
    
    def get_type(self):
        """Retorna el tipo de mensaje"""
        return self.type
    
    def get_message(self):
        """Retorna el contenido del mensaje"""
        return self.message