import socket
import threading
import time

def sending(conn, stop_event):
    name = input("Introdu numele tau: ")
    conn.sendall(name.encode())
    time.sleep(1)
    try:
        while not stop_event.is_set():
            guess = input("Introdu un numar de 4 cifre diferite: ")
            if stop_event.is_set():
                break
            if len(guess) != 4 or len(set(guess)) != 4:
                print("Numarul introdus trebuie sa aiba 4 cifre diferite.")
                continue
            conn.sendall(guess.encode())
            time.sleep(0.1) 
    except Exception as e:
        print("Error in send_data thread:", e)

def receiving(conn, stop_event):
    try:
        while True:
            response = conn.recv(1024).decode()
            if response == "Numele este deja folosit. Conectează-te cu alt nume.":
                print(response)
                stop_event.set() 
                conn.close()
                break
            if ',' not in response:
                print(response)
                continue
            centered, non_centered = response.split(',')
            print(f"\nNumar centrate: {centered}, Numar necentrate: {non_centered}")
            if int(centered) == 4:
                print("Felicitari! Ai ghicit numarul.")
                continue  
    except Exception as e:
        print("Error in receive_data thread:", e)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 65432)
    client_socket.connect(server_address)

    stop_event = threading.Event()  
    
    thread_send = threading.Thread(target=sending, args=(client_socket, stop_event))
    thread_recv = threading.Thread(target=receiving, args=(client_socket, stop_event))
    
    thread_recv.start()
    thread_send.start()
    
    thread_send.join()
    thread_recv.join()

if __name__ == "__main__":
    main()
