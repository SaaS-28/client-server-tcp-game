# Client-server-tcp-game
**TCP local client-server game** made with [**python**](https://www.python.org/). The game in question is **"The Hangman"** or better a **reworked version**.

## How it was done
To do this, **sockets** and **threads** were used so as to allow the **parallel execution** of the game and allow the operation of all the mechanics inserted.

One of these mechanics allows clients to **choose different difficulties**, in fact if the client chooses the same difficulty, the same word will be shown, otherwise different words will be shown.

So this is not a game where all the clients try to guess the word against the computer that generates it, but <u>everyone will have to guess his word</u>.

## How to play it
To play, just start the server and then the various clients. You will have to select the **game mode** (Extremly easy, Easy, Medium and Hard) and after that the word will be shown.

At this point it will be enough to guess the word trying to guess the individual letters.

## Future deployments
- *Graphics* to make the game more enjoyable.
- A *final ranking* based on whether you guessed the word or not and how long it took.

collaborators: [@M4rga](https://github.com/M4rga)