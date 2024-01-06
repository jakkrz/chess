# Chess

This project is a chess engine and client implemented in Python which uses sockets to connect to another player over a LAN. It includes over 2500 lines of code.

Originally, this project was made to be able to play with other people during computer lab classes and meant to be run in an intentionally constricted programming environment. However, this project taught me a lot about organization of projects and refactoring.

# Usage

Install the files and run
```
pip install -r requirements.txt
```
After that, you can run
```
python3 main.py
```
You will then be prompted whether to create or join a game. After that, if you choose to create a game in debug mode, you will be playing through two windows on the same device (used for testing). However, most users will want to use normal mode.

The other player must connect using the join option and enter the same IP and port that the game is being hosted on by the player using the create option. The rest is self-explanatory.
