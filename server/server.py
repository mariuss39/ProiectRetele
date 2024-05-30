import socket
import threading
import time

clients = {} # dictionar pentru clientii conectati
products = {} # dictionar pentru produse
auction_duration = 60 # timpul pentru fiecare licitatie

# functia care trimite notificari fiecarui client
def notify_all_clients(message):
    for client in clients.values():
        client.send(message.encode('utf-8'))

# functia care se ocupa de comunicarea cu clientul
def handle_client(client_socket, client_address):
    try:
        name = client_socket.recv(1024).decode('utf-8') # primeste numele
        if name in clients:
            client_socket.send('Name already taken. Connection refused.'.encode('utf-8'))
            client_socket.close()
            return
        # il adauga in dictionar
        clients[name] = client_socket
        client_socket.send('Connected successfully.'.encode('utf-8'))
        print(f"{name} connected from {client_address}")
        
        while True:
            # primim requesturi de la clienti
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            # functia de list
            if request == 'LIST':
                response = "Products in auction:\n"
                for product, details in products.items():
                    response += f"{product} - Seller: {details['seller']}, Min Price: {details['min_price']}, Max Price: {details['max_price']}, Highest Bidder: {details['highest_bidder']}\n"
                client_socket.send(response.encode('utf-8'))
            # sell
            elif request.startswith('SELL'):
                parts = request.split()
                if len(parts) != 3:
                    client_socket.send('Invalid SELL command. Usage: SELL <product_name> <min_price>'.encode('utf-8'))
                    continue
                
                _, product_name, min_price = parts
                try:
                    min_price = float(min_price)
                except ValueError:
                    client_socket.send('Invalid price. Please enter a valid number.'.encode('utf-8'))
                    continue
                
                if product_name in products:
                    client_socket.send('Product name already exists.'.encode('utf-8'))
                else:
                    products[product_name] = {
                        'seller': name,
                        'min_price': min_price,
                        'max_price': min_price,
                        'highest_bidder': None,
                        'bidders': [],
                        'end_time': time.time() + auction_duration
                    }
                    # trimite notificarea ca s-a adaugat cu succes
                    notify_all_clients(f"New product added: {product_name} by {name} starting at {min_price}")
                    # facem si thead separat pentru timer
                    threading.Thread(target=auction_timer, args=(product_name,)).start()
                    client_socket.send('Product added successfully.'.encode('utf-8'))
            # functia pentru bid
            elif request.startswith('BID'):
                parts = request.split()
                if len(parts) != 3:
                    client_socket.send('Invalid BID command. Usage: BID <product_name> <bid_amount>'.encode('utf-8'))
                    continue
                
                _, product_name, bid_amount = parts
                try:
                    bid_amount = float(bid_amount)
                except ValueError:
                    client_socket.send('Invalid bid amount. Please enter a valid number.'.encode('utf-8'))
                    continue
                
                if product_name not in products:
                    client_socket.send('Product not found.'.encode('utf-8'))
                else:
                    product = products[product_name]
                    if time.time() > product['end_time']:
                        client_socket.send('Auction for this product has ended.'.encode('utf-8'))
                        continue
                    
                    if bid_amount <= product['max_price']:
                        client_socket.send('Bid amount must be higher than the current max price.'.encode('utf-8'))
                    else:
                        product['max_price'] = bid_amount
                        product['highest_bidder'] = name
                        if name not in product['bidders']:
                            product['bidders'].append(name)
                        
                    notify_all_clients(f"New bid on {product_name} by {name}: {bid_amount}")
            
            else:
                client_socket.send('Invalid command.'.encode('utf-8'))
    
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        if name in clients:
            del clients[name]
        client_socket.close()
        print(f"{name} disconnected.")

def auction_timer(product_name):
    time.sleep(auction_duration)
    product = products.pop(product_name, None)
    if product:
        notify_all_clients(f"Auction for {product_name} has ended. Final price: {product['max_price']}, Winner: {product['highest_bidder']}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print("Server started on port 9999.")
    
    try:
        while True:
            # accepta un nou client
            client_socket, client_address = server_socket.accept()
            # creeaza thread separat pentru client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
