import socket
import pickle
import threading
import time
from chat_message import ChatMessage

def simulate_client(client_id, messages_per_client, delay_between_messages):
    try:
        # Conectar al servidor
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", 1500))

        # Enviar nombre de usuario
        username = f"User{client_id}"
        client_socket.sendall(pickle.dumps(username))

        # Enviar mensajes
        for i in range(messages_per_client):
            message = f"Message {i} from {username}"
            start_time = time.time()  # Tiempo antes de enviar el mensaje
            client_socket.sendall(pickle.dumps(ChatMessage(ChatMessage.MESSAGE, message)))
            end_time = time.time()  # Tiempo después de enviar el mensaje
            with open("resultados_python.txt", "a") as file:
                file.write(f"{(end_time - start_time) * 1000:.2f}\n")
            time.sleep(delay_between_messages / 1000.0)

        # Desconectar
        client_socket.sendall(pickle.dumps(ChatMessage(ChatMessage.LOGOUT, "")))
        client_socket.close()
    except Exception as e:
        print(f"Error en cliente {client_id}: {e}")

    finally:
        if client_socket:
            client_socket.close()

def main():
    messages_per_client = 10  # Número de mensajes por cliente
    delay_between_messages = 100  # Milisegundos entre mensajes

    for num_clients in range(100, 1001, 100):
        print(f"Probando con {num_clients} clientes...")
        threads = []
        for i in range(num_clients):
            t = threading.Thread(target=simulate_client, args=(i, messages_per_client, delay_between_messages))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

if __name__ == "__main__":
    main()