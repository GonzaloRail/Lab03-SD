import java.io.*;
import java.net.*;
import java.util.concurrent.*;

public class LoadTestClient {
    public static void main(String[] args) {
        int messagesPerClient = 10; // Número de mensajes por cliente
        int delayBetweenMessages = 100; // Milisegundos entre mensajes

        for (int numClients = 100; numClients <= 1000; numClients += 100) {
            System.out.println("Probando con " + numClients + " clientes...");
            ExecutorService executor = Executors.newFixedThreadPool(numClients);

            for (int i = 0; i < numClients; i++) {
                int clientId = i;
                executor.execute(() -> {
                    Socket socket = null;
                    ObjectOutputStream sOutput = null;
                    ObjectInputStream sInput = null;
                    try {
                        socket = new Socket("localhost", 1500);
                        sOutput = new ObjectOutputStream(socket.getOutputStream());
                        sInput = new ObjectInputStream(socket.getInputStream());

                        // Enviar nombre de usuario
                        String username = "User" + clientId;
                        sOutput.writeObject(username);

                        // Enviar mensajes
                        for (int j = 0; j < messagesPerClient; j++) {
                            String message = "Message " + j + " from " + username;
                            long startTime = System.currentTimeMillis(); // Tiempo antes de enviar el mensaje
                            sOutput.writeObject(new ChatMessage(ChatMessage.MESSAGE, message));
                            long endTime = System.currentTimeMillis(); // Tiempo después de enviar el mensaje
                            try (PrintWriter writer = new PrintWriter(new FileWriter("resultados_java.txt", true))) {
                                writer.println(endTime - startTime);
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                            Thread.sleep(delayBetweenMessages);
                        }

                        // Desconectar
                        sOutput.writeObject(new ChatMessage(ChatMessage.LOGOUT, ""));
                    } catch (Exception e) {
                        System.out.println("Error en cliente " + clientId + ": " + e.getMessage());
                    } finally {
                        try {
                            if (sOutput != null) sOutput.close();
                            if (sInput != null) sInput.close();
                            if (socket != null) socket.close();
                        } catch (IOException e) {
                            System.out.println("Error cerrando recursos para cliente " + clientId + ": " + e.getMessage());
                        }
                    }
                });
            }

            executor.shutdown();
            try {
                executor.awaitTermination(1, TimeUnit.MINUTES);
            } catch (InterruptedException e) {
                System.out.println("Error esperando la finalización de los clientes.");
            }
        }
    }
}