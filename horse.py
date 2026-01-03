"""
Covering Of Trojan Horse
"""

import random


def game():

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