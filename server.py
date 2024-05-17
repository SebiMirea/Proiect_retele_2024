import socket
import random
import threading

secret_number = ""
clients = []
client_names = set()
dict = {}

def generate_number():
    while True:
        first_digit = str(random.randint(1, 9))
        rest_digits = ''.join(random.sample('0123456789', 3))
        if first_digit not in rest_digits:
            return first_digit + rest_digits

def check_guess(secret, guess):
    centered = 0
    non_centered = 0
    for i in range(4):
        if guess[i] == secret[i]:
            centered += 1
        elif guess[i] in secret:
            non_centered += 1
    return centered, non_centered

def notify_clients(winner, attempts):
    global clients
    message = f"\n{winner} a ghicit numarul din {attempts} incercari. Se genereaza un numar nou."
    for client_info in clients:
        client, name = client_info
        if name != winner:
            client.sendall(message.encode())

def handle_client(client_socket, client_address):
    global secret_number, clients, client_names
    name = client_socket.recv(1024).decode()
    
    if name in client_names:
        client_socket.sendall("Numele este deja folosit. Conectează-te cu alt nume.".encode())
        client_socket.close()
        return

    print('Conectat:', name)
    client_names.add(name)
    dict[name] = 0
    clients.append((client_socket, name))
    
    for client_info in clients:
        client, _ = client_info
        if client != client_socket:
            client.sendall(f"\n{name} s-a conectat.".encode())

    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        if data.isdigit():
            guess = data
            print(f"{name} a spus {guess}")
            dict[name] += 1
            centered, non_centered = check_guess(secret_number, guess)
            client_socket.sendall(f"{centered},{non_centered}".encode())
            if centered == 4:
                print(f"{name} a ghicit numarul.")
                notify_clients(name, dict[name])
                secret_number = generate_number()
                print("Noul numar secret generat:", secret_number)
                for i in dict:
                    dict[i] = 0
                for client_info in clients:
                    client, _ = client_info
                    client.sendall("\nNoul numar secret generat. Ghiceste-l!".encode())
        else:
            print(data)

    clients.remove((client_socket, name))
    client_names.remove(name)
    client_socket.close()

def main():
    global secret_number
    HOST = '127.0.0.1'
    PORT = 65432

    secret_number = generate_number()
    print("Numarul secret generat:", secret_number)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print("Serverul este pornit...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    main()
