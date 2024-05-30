import socket
import threading
#functie pt mesajele de la server
def receive_messages(client_socket):
    while True:
        try:
            #asteapta msj de la server
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message) #le afiseaza
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 9999)
    client_socket.connect(server_address)

    # introducem numele clientului
    name = input("Enter your name: ")
    client_socket.send(name.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response == 'Name already taken. Connection refused.':
        print(response)
        client_socket.close()
        return

    print(response)

    # thread pentru a primi mesaje de la server
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # meniu principal
    while True:
        print("\nOptions:")
        print("1. List products in auction")
        print("2. Sell a product")
        print("3. Bid on a product")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            client_socket.send('LIST'.encode('utf-8'))
        elif choice == '2':
            product_name = input("Enter product name: ")
            min_price = input("Enter minimum price: ")
            client_socket.send(f"SELL {product_name} {min_price}".encode('utf-8'))
        elif choice == '3':
            product_name = input("Enter product name to bid on: ")
            bid_amount = input("Enter your bid amount: ")
            client_socket.send(f"BID {product_name} {bid_amount}".encode('utf-8'))
        elif choice == '4':
            print("Exiting...")
            client_socket.close()
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
