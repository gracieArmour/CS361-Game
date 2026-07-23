# Stop and Smell the Roses (Microservices Edition)
A short adventure game made in Pico-8, with Python microservices, for CS361 Software Engineering I.

This project was made in collaboration with a team of group members, but the final result includes only 1 service not coded by myself. All code in `points_service.py` was written by a groupmate, Corinne, except for minor compatibility changes made for integration into this project. All other code is my own unless otherwise noted in code comments.

A version of this game with all microservice functionality re-implemented entirely in Pico-8 itself can now be found and played in-browser on [Itch](https://graciearmour.itch.io/stop-and-smell-the-irises), as well as in proper game cart form on the [Pico-8 BBS](https://www.lexaloffle.com/bbs/?tid=158252).

## Platform Notes
This game is designed for and runs only on the [Pico-8 Fantasy Console](https://www.lexaloffle.com/pico-8.php). Due to the nature of the microservice integrations, it could not be exported to a traditional binary format, and as such _requires_ an installed copy of Pico-8 in order to run.

In addition, as the microservices are coded in and run using Python, it also requires [Python 3](https://www.python.org/downloads/) to be installed.

The game has only been tested on Windows 10, but in theory it may run on any platform where both Python 3 and Pico-8 are supported.

## The Microservices
The main Pico-8 game is supported by 4 microservices: a Signs Services, a Death Message Service, a Points Service, and a High Score Service.

### [The Signs Service](https://github.com/CS-361-Coder-Club-Group/Signs-Microservice)
This service stores, formats, and serves the text of all signs in the game.

### [The Death Message Service](https://github.com/CS-361-Coder-Club-Group/Death-Message-Microservice)
This service stores, randomly selects, and serves messages for the "game over" screen from a pre-written list.

### [The Points Service](https://github.com/CS-361-Coder-Club-Group/Points-Microservice)
This service stores and manages running totals of points, identified by text-based IDs. It handles adding and subtracting points from existing totals, and telling the game how many points the player now has.

This service was almost entirely coded by one of my group members, Corinne Davila ([coridav](https://github.com/coridav)), and is provided here with permission.

### [The High Score Service](https://github.com/CS-361-Coder-Club-Group/High-Score-Microservice)
This service stores a persistent list of high scores, and handles checking new scores against the list to determine and inform the game if a new high score has been achieved.
