PARA JAVA

Compilar los archivos Java

Abre una terminal en VS Code (Terminal > New Terminal)
Compila todos los archivos con el siguiente comando:
javac *.java


Iniciar el servidor

En la terminal, ejecuta el siguiente comando para iniciar el servidor:
java Server

Verás un mensaje indicando que el servidor está esperando conexiones en el puerto 1500

Iniciar uno o más clientes

Abre una nueva terminal en VS Code (puedes hacerlo con el botón + en el panel de terminal)
Ejecuta el comando:
java Client

Ingresa un nombre de usuario cuando se te solicite
Puedes abrir más terminales para conectar más clientes, cada uno con un nombre de usuario diferente

Paso 5: Utilizar el chat
Una vez que tengas el servidor y al menos un cliente ejecutándose:

Enviar mensaje a todos los usuarios:

Simplemente escribe el mensaje y presiona Enter


Enviar mensaje privado a un usuario específico:

Escribe @nombreusuario mensaje y presiona Enter


Ver quién está conectado:

Escribe WHOISIN y presiona Enter


Desconectarse del servidor:

Escribe LOGOUT y presiona Enter



Opcional: Ejecutar con parámetros
Puedes especificar parámetros al iniciar el cliente:

Para especificar un nombre de usuario:
java Client nombreusuario

Para especificar nombre de usuario y puerto:
java Client nombreusuario 1500

Para especificar nombre, puerto y dirección del servidor:
java Client nombreusuario 1500 localhost


De manera similar, puedes especificar un puerto diferente al iniciar el servidor:
java Server 1501
