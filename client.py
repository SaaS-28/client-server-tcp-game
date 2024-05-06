import socket, sys

# Function used for handle the connection with server
def server_connection():
    try:
        s = socket.socket() # Initialize the socket for sending and recieving data
        s.connect(('127.0.0.1', 20000)) # Connect to localhost
        print(f"Connesso al Server su 127.0.0.1:20000")
        lobby(s)
    except socket.error as errore:
        print(f"Qualcosa è andato storto, sto uscendo... \n{errore}")
        sys.exit()

# Function used to handle the lobby of the game. Command is used to pick up the input from the client while send is used to send the input to the server. recv instead is used to recive messages from the server
def lobby(s):
    message = str(s.recv(8192), "utf-8").strip() # Decodes received data in a Unicode string and removes any white spaces at the beginning and end of the string
    print(message)
    command = input("Inserisci la difficoltà: ")
    while command not in difficulties:
        command = input("Attenzione, inserisci una delle difficoltà tra quelle proposte: ")
    s.send(command.encode())
    command = input("Inserisci 'pronto' per iniziare per uscire: ")
    while command != "pronto":
        command = input("Attenzione: Inserisci 'pronto', non altro: ")
    s.send(command.encode())
    if command == "pronto":
        print("Hai messo pronto")
        message = str(s.recv(8192), "utf-8").strip()
        print(message)
        while message != "Tutti i client sono pronti!":
            message = str(s.recv(8192), "utf-8").strip()
            print(message)
            s.send(command.encode())
            break
        game(s)

# Function used to play the effective game
def game(s):
    try:
        while True:
            message = str(s.recv(8192), "utf-8").strip() # Decodes received data in a Unicode string and removes any white spaces at the beginning and end of the string
            print(message)

            if message.startswith("Complimenti!") or message.startswith("Hai esaurito i tentativi."):
                command = input("Se vuoi giocare ancora scrivi 'si' altrimenti scrivi 'no': ")
                s.send(command.encode())

                lobby(s) if command == "si" else disconnect_client(s)
            else:
                command = input("Inserisci una lettera: ")
                while command == "":
                    command = input("Attenzione, non hai inserito nulla, Inserisci una lettera: ")
                s.send(command.encode())

    except ConnectionResetError:
        print("Connessione chiusa dal server in modo imprevisto.")
        s.close()
    except ConnectionAbortedError:
        print("Connessione interrotta in modo imprevisto.")
        s.close()

# Function used to disconnect a client
def disconnect_client(s):
    print("Grazie per aver giocato!")
    s.close()
    sys.exit()

difficulties = ["extremly easy", "easy", "medium", 'hard']

if __name__ == '__main__':
    server_connection()