import socket, sys, threading, random, os

# Function used for running the server
def run_server(address, port):
    global connected_clients
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Initialize a socket object. AF_INET means that we are using IPv4 while SOCK_STREAM means that we are using TCP.
    s.bind((address, port)) # Connects the socket to a specified IP address and port
    s.listen() # Start the server in listening mode for incoming connections

    print(f"Server in ascolto su {address}:{port}")

    threads = []

    while True:
        conn, addr = s.accept() # Accept new incoming connection on socket s. Conns is the new socket that represents the accepted connection. It will be used to communicate with the client that established the connection. Addr is the IP address and port number of the client that established the connection 
        connected_clients.append(conn) # Appends all the clients connected in an array

        print(f"Connesso a {addr}")
        thread = threading.Thread(target=lobby, args=(conn, addr)) # Creates a new thread to manage the client connection. The thread target is the lobby function, which is responsible for managing communication with the client.
        thread.start() # Start the execution of the new thread just created
        threads.append(thread) # Adds the newly created thread to the threads list. This is done to keep track of all active threads.

# Function that loads the file based on the difficulty client chooses
def select_difficulty(difficulty):
    script_directory = os.path.dirname(__file__) # Used to locate the directory on wich the client runs the script

    # Looking for every possible choose
    match difficulty:
        case "extremly easy":
            words_file = load_words(os.path.join(script_directory, 'words/extremly_easy.txt'))
        case "easy":
            words_file = load_words(os.path.join(script_directory, 'words/easy.txt'))
        case "medium":
            words_file = load_words(os.path.join(script_directory, 'words/medium.txt'))
        case "hard":
            words_file = load_words(os.path.join(script_directory, 'words/hard.txt'))

    return words_file

# Function used for load all the words in the file
def load_words(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()] # Reads all the lines and return a list with all the words. It also eliminate spaces

# Functions used for modify the word to return to client
def edit_word(word):
    return word[0] + '_' * (len(word) - 2) + word[-1] # This returns the word with "_" except for the first and the last character

def lobby(conn, addr):
    global connected_clients, ready_clients, shared_word, client_difficulties, client_shared_words

    try:
        print(f"Dispositivi connessi: {len(connected_clients)}")
        conn.sendall("Benvenuto al gioco dell'Impiccato! | Seleziona la difficoltà: extremly easy / Easy / Medium / Hard".encode())
        response = conn.recv(1024).decode().strip().lower()

        client_difficulties[conn] = response  # Pick the difficulty chosen by the client

        # Checks if there are other clients with the same difficulty choosen. This uses dictionary, which is a data structure that maps keys to values
        same_difficulty_clients = [c for c in client_difficulties.keys() if client_difficulties[c] == response]
        
        # This is used to choose randomly a word to assign to the clients. If there are multiple clients that have chosen the same difficulty, it assing the same word for both. If not it assign a word only to the client. If the client wants to play again it choose a random word again
        if len(same_difficulty_clients) > 1 and response not in client_shared_words.values():
            shared_word = random.choice(select_difficulty(response))
            for client in same_difficulty_clients:
                client_shared_words[client] = shared_word
        else:
            shared_word = random.choice(select_difficulty(response))
            client_shared_words[conn] = shared_word
        
        while True:
            response = conn.recv(1024).decode().strip().lower()

            # Looks for response and handles the 'pronto' (which means ready) statement
            if response == "pronto":
                ready_clients += 1
                print(f"Dispositivi pronti: {ready_clients}")
                if ready_clients == len(connected_clients) and len(connected_clients) > 0:
                    for c in connected_clients:
                        c.sendall("Tutti i client sono pronti!".encode())
                    ready_clients = 0
                    game(conn, addr)
                    break
                else:
                    conn.sendall("Aspetta che tutti i client siano pronti...".encode())
                    while True:
                        response = conn.recv(1024).decode().strip().lower()
                        if response == "pronto":
                            game(conn, addr)
                            break

        shared_word = None
        client_difficulties = {}
        client_shared_words = {}

    except Exception as e:
        print(f"errore: {e}")

def game(conn, addr):
    global client_shared_words, client_difficulties, ready_clients

    difficulty = client_difficulties[conn]  # Get the difficulty chosen by the client

    # if the client does not have a shared word yet, get words based on difficulty
    if conn not in client_shared_words:
        word_list = select_difficulty(difficulty)
        client_shared_words[conn] = random.choice(word_list)

    word = client_shared_words[conn]  # Get the effective word
    letters = [] # Used for save letters written by client
    print(word)

    hidden_word = list(edit_word(word))  # convert the word in a editable word
    attempts_left = 6

    conn.sendall(f"\nParola: {''.join(hidden_word)}  Tentativi rimasti: {attempts_left}\n".encode())

    while True:
        
        response = conn.recv(1024).decode().strip().lower()
        print(response)

        # This handles every possible input given by the client. Is the letter is correct, it return again the word with the letter guessed shown. If the clients misses, it return the same word but with attempts reduced by 1. If the client guesses the same letter, the same word appear with a warning. If the client tries to write multiple letters, the server return a warning
        if len(response) != 1 or not response.isalpha():
            conn.sendall(f"\nInserisci una sola lettera\nParola: {''.join(hidden_word)}  Tentativi rimasti: {attempts_left}\n".encode())
        else:
            if response in letters:
                conn.sendall(f"\nHai già usato questa lettera\nParola: {''.join(hidden_word)}  Tentativi rimasti: {attempts_left}\n".encode())
            else:
                if response in word:
                    for i in range(len(word)):
                        if word[i] == response:
                            hidden_word[i] = response
                else:
                    attempts_left -= 1

                letters.append(response)

                # If the client looses or win, it is given the possibility to play again
                if attempts_left == 0:
                    conn.sendall(f"\nHai esaurito i tentativi. Hai perso!\nLa parola era: {word}.".encode())
                    response = conn.recv(1024).decode().strip().lower()

                    lobby(conn, addr) if response == "si" else disconnect_client(conn, addr)
                    break
                elif ''.join(hidden_word) == word:
                    conn.sendall("\nComplimenti! Hai indovinato la parola!".encode())
                    response = conn.recv(1024).decode().strip().lower()
                    
                    lobby(conn, addr) if response == "si" else disconnect_client(conn, addr)
                    break
                else:
                    conn.sendall(f"\nParola: {''.join(hidden_word)}  Tentativi rimasti: {attempts_left}\n".encode())

# Function used to disconnect client correctly
def disconnect_client(conn, addr):
    global client_difficulties, client_shared_words, connected_clients, ready_clients, shared_word

    if conn in connected_clients:
        # Rimuovi il client dalle liste globali
        connected_clients.remove(conn)
        client_difficulties.pop(conn, None)
        client_shared_words.pop(conn, None)
        
        print(f"Disconnesso da {addr}")
        print(f"Dispositivi connessi: {len(connected_clients)}")

        # If there are some clients that wants to play the game again while one of the client disconnect, the other clients are allowed to play the game
        if len(connected_clients) > 0:
            if ready_clients == len(connected_clients):
                for c in connected_clients:
                    c.sendall("Uno o più client si sono disconnessi. Ora tutti i client sono pronti!".encode())
                ready_clients = 0
                game(conn, addr)

        else:
            close_server(conn)

# Fcuntion used to close the server
def close_server(conn):
    print("Chiusura del server in corso...")
    conn.close()
    sys.exit()
    
shared_word = None # Variable used to save the word to share with the clients that have choosen the same difficulty
ready_clients = 0 # Variable used to see all the clients that are ready
connected_clients = [] # Array used to save all connected clients
client_difficulties = {}
client_shared_words = {}

if __name__ == '__main__':
    run_server('0.0.0.0', 20000)
