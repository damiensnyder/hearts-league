# Hearts League
If you're here, hopefully it's because you want to create a bot for [Hearts League](https://hearts.damiensnyder.com/). Here's how to do that.

## How Hearts works
[Here](http://mark.random-article.com/hearts/intro.html) is a guide on how to play Hearts. (The only difference is that the "holding hand" is skipped here.)

## How the league works
See the [about tab](https://hearts.damiensnyder.com/) for an explanation of the league rules.

## Bot format
A bot must be a Python file with two functions: `getPlay(gameState)` and `getSlough(gameState)`. The `gameState` parameter receives a `GameState` class with the following fields:

`hand` - A Python list of the cards currently in your hand. Cards are represented by a number from 0 to 51. The clubs are 0-12 (with the 2 being 0 and the ace being 12), diamonds are 13-25, spades are 26-38, and hearts are 39-51. An example hand would be `[25, 14, 6, 19]`, containing the ace of diamonds, 3 of diamonds, 8 of clubs, and 8 of diamonds.

`legalMoves` - The cards in your hand that you can legally play at that point. (Same format.)

`lead` - An integer representing the player who led or leads this trick. Player 1 is 0, Player 2 is 1, and so on.

`playHistory` - The cards that have been played (not including sloughed cards) so far this game. This is formatted as a list of lists of cards. Player 1 is the first sublist, Player 2 the second, and so on. Each sublist is only as long as the number of cards that player has played. An example list would be:

```
[[10],
 [12, 14],
 [ 0, 17],
 [ 6]]
```

`roundPoints` - A Python list containing the number of points each player has taken so far this round. For example, if Player 2 has taken 5 points and everyone else has taken no points, it would be `[0, 5, 0, 0]`.

`gamePoints` - The number of points each player has taken so far this game. (Same format.) This list is not updated until the end of each round.

`whichPlayer` - Your place in the turn order. (Same format as `lead`.)

`sloughDirection` - An integer representing which direction cards are passed this round. 1 is to the player immediately after you in the order, 2 is to the player across from you, and 3 is to the player immediately before you.

`sloughedByYou` - A list containing the cards you have sloughed so far this game.

`sloughedToYou` - A list containing the cards that were sloughed to you so far this game. This list is not updated until after all cards have been sloughed.

Both functions must return the index of the card in `legalMoves` that you intend to play. If `legalMoves` is `[5, 4, 11]` and you wish to play the 6 of clubs, you would return 1. If an index not in `legalMoves` is returned, a random legal move will be selected instead.

## Other rules

You may not import any modules other than numpy, pandas, math, and random. A season has hundreds of thousands of moves, so each move should take no longer than about 20 milliseconds to allow for quick simulation.

## Testing

The Hearts League simulation code is provided, along with an example roster, schedule, and bot. Run HeartsLeague.py with your bot in the Bots folder and its name in the roster, and view the tables in the Outputs to see the results.

## Submission

Email the Python file to me at damiensnyder@damiensnyder.com, and if it meets the requirements I will add it to the next applicable event.

## License

Do not redistribute any of my code or its outputs without my written permission.
