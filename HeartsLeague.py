#!/usr/bin/env python3


# IMPORTS


from importlib import import_module
import random
import pandas as pd
import math


# CONSTANTS


# column names for output DFs
TRICK_COLUMNS = ["Season", "Game", "Round", "Trick", "P1 Card", "P2 Card", "P3 Card", "P4 Card", "Lead", "Winner"]
ROUND_COLUMNS = ["Season", "Game", "Round", "P1 Score", "P2 Score", "P3 Score", "P4 Score", "Queen"]
GAME_COLUMNS = ["Season", "Game", "P1", "P2", "P3", "P4", "P1 Score", "P2 Score", "P3 Score", "P4 Score", "P1 Hearts",
                "P2 Hearts", "P3 Hearts", "P4 Hearts", "P1 Queens", "P2 Queens", "P3 Queens", "P4 Queens", "P1 Tricks",
                "P2 Tricks", "P3 Tricks", "P4 Tricks"]
STANDINGS_COLUMNS = ["Season", "Game", "Name", "Author", "Games Played", "#1", "#2", "#3", "#4", "Points",
                     "Rounds Played", "Tricks Won", "Hearts", "Queens"]

# useful subgroups of column names
SCORE_SUB = ["P1 Score", "P2 Score", "P3 Score", "P4 Score"]
TRICK_SUB = ["P1 Tricks", "P2 Tricks", "P3 Tricks", "P4 Tricks"]
CARD_SUB = ["P1 Card", "P2 Card", "P3 Card", "P4 Card"]

# filepaths
BOT_PATH = "Rosters/Main.csv"
SCHEDULE_PATH = "Schedules/Main.csv"
TRICK_PATH = "Outputs/TrickHistory.csv"
ROUND_PATH = "Outputs/RoundHistory.csv"
GAME_PATH = "Outputs/GameHistory.csv"
STANDINGS_PATH = "Outputs/Standings.csv"

# season name
SEASON = "Test Season"


# FUNCTIONS


# gets the sluff of the bot with the given name and the current game state
def getBotSluff(botName, gameState):
    globals()[botName] = import_module("Bots." + botName)
    move = globals()[botName].getSluff(gameState)
    return move


# gets the play of the bot with the given name and the current game state
def getBotPlay(botName, gameState):
    globals()[botName] = import_module("Bots." + botName)
    move = globals()[botName].getPlay(gameState)
    return move


# just tells everything else what to do
def runLeague():
    botList = pd.read_csv(BOT_PATH)
    schedule = pd.read_csv(SCHEDULE_PATH, header=None).values.tolist()
    league = League(SEASON, botList, schedule)
    league.playGames()
    league.writeToCsv(TRICK_PATH, ROUND_PATH, GAME_PATH, STANDINGS_PATH)


# CLASSES


class League:
    def __init__(self, season, botList, schedule):
        self.season = season
        self.pathList = botList["Filepath"].values.tolist()
        self.nameList = botList["Name"].values.tolist()
        self.authorList = botList["Author"].values.tolist()
        self.schedule = schedule
        self.trickHistory = []
        self.roundHistory = []
        self.gameHistory = []
        self.standings = []
        self.gameNumber = 0

    # simulates all the games
    def playGames(self):

        # for each game in the schedule:
        for playerIndices in self.schedule:
            self.gameNumber += 1

            # get the names of the players in the game
            players = []
            playerNames = []
            for i in range(4):
                players.append(self.pathList[playerIndices[i]])
                playerNames.append(self.nameList[playerIndices[i]])

            # create and run the game
            game = Game(players, playerNames, self.season, self.gameNumber)
            game.simGame()

            # get the history and update the standings
            for eachTrick in game.trickHistory:
                self.trickHistory.append(eachTrick)
            for eachRound in game.roundHistory:
                self.roundHistory.append(eachRound)
            self.gameHistory.append(game.getGameHistory())
            self.updateStandings()

        self.gameNumber += 1
        self.updateStandings()

    # adds the standings after each game to the standings DF
    def updateStandings(self):

        # for each player:
        for playerIndex in range(len(self.pathList)):

            # make some counters
            author = self.authorList[playerIndex]
            name = self.nameList[playerIndex]
            gamesPlayed = 0
            num1 = 0
            num2 = 0
            num3 = 0
            num4 = 0
            points = 0
            roundsPlayed = 0
            tricksWon = 0
            hearts = 0
            queens = 0

            # for each game so far:
            for gameNumber in range(self.gameNumber - 1):
                gameRow = self.gameHistory[gameNumber]

                if playerIndex in self.schedule[gameNumber]:
                    score = 0

                    # if it is player 1:
                    if self.schedule[gameNumber][0] == playerIndex:

                        # get the easy stuff
                        score = gameRow["P1 Score"]
                        tricksWon += gameRow["P1 Tricks"]
                        hearts += gameRow["P1 Hearts"]
                        queens += gameRow["P1 Queens"]

                    # if it is player 1:
                    elif self.schedule[gameNumber][1] == playerIndex:

                        # get the easy stuff
                        score = gameRow["P2 Score"]
                        tricksWon += gameRow["P2 Tricks"]
                        hearts += gameRow["P2 Hearts"]
                        queens += gameRow["P2 Queens"]

                    # if it is player 3:
                    elif self.schedule[gameNumber][2] == playerIndex:

                        # get the easy stuff
                        score = gameRow["P3 Score"]
                        tricksWon += gameRow["P3 Tricks"]
                        hearts += gameRow["P3 Hearts"]
                        queens += gameRow["P3 Queens"]

                    # if it is player 4:
                    else:

                        # get the easy stuff
                        score = gameRow["P4 Score"]
                        tricksWon += gameRow["P4 Tricks"]
                        hearts += gameRow["P4 Hearts"]
                        queens += gameRow["P4 Queens"]

                    gamesPlayed += 1
                    points += score

                    # get the number of tricks played
                    for colName in TRICK_SUB:
                        roundsPlayed += gameRow[colName]

                    # get the number of times each placement was gotten
                    numBetter = 0
                    numWorse = 0

                    # count how many players performed better and worse
                    for colName in SCORE_SUB:
                        if gameRow[colName] < score:
                            numBetter += 1
                        elif gameRow[colName] > score:
                            numWorse += 1

                    # deals with ties in the placement
                    if (numBetter == 0) & (numWorse == 1):
                        num1 += 4
                        num2 += 4
                        num3 += 4
                    elif (numBetter == 0) & (numWorse == 2):
                        num1 += 6
                        num2 += 6
                    elif (numBetter == 0) & (numWorse == 3):
                        num1 += 12
                    elif (numBetter == 1) & (numWorse == 2):
                        num2 += 12
                    elif (numBetter == 2) & (numWorse == 1):
                        num3 += 12
                    elif (numBetter == 3) & (numWorse == 0):
                        num4 += 12
                    elif (numBetter == 1) & (numWorse == 1):
                        num2 += 6
                        num3 += 6
                    elif (numBetter == 1) & (numWorse == 0):
                        num2 += 4
                        num3 += 4
                        num4 += 4
                    elif (numBetter == 2) & (numWorse == 0):
                        num3 += 6
                        num4 += 6
                    else:
                        num1 += 3
                        num2 += 3
                        num3 += 3
                        num4 += 3

            # add the row to the standings
            row = dict(zip(STANDINGS_COLUMNS, [self.season, self.gameNumber - 1, name, author, gamesPlayed, num1 / 12,
                                               num2 / 12, num3 / 12, num4 / 12, points, roundsPlayed / 13, tricksWon,
                                               hearts, queens]))
            self.standings.append(row)

    # outputs everything to CSV
    def writeToCsv(self, trickPath, roundPath, gamePath, standingsPath):
        trickHistoryDF = pd.DataFrame.from_dict(self.trickHistory)
        roundHistoryDF = pd.DataFrame.from_dict(self.roundHistory)
        gameHistoryDF = pd.DataFrame.from_dict(self.gameHistory)
        standingsDF = pd.DataFrame.from_dict(self.standings)

        trickHistoryDF.to_csv(trickPath, index=False, header=False)
        roundHistoryDF.to_csv(roundPath, index=False, header=False)
        gameHistoryDF.to_csv(gamePath, index=False, header=False)
        standingsDF.to_csv(standingsPath, index=False, header=False)


class Game:
    def __init__(self, players, playerNames, season, gameNumber):
        self.season = season
        self.players = players
        self.playerNames = playerNames
        self.gameNumber = gameNumber
        self.roundPoints = None
        self.gamePoints = [0] * 4
        self.sluffDirection = 1
        self.gameOver = False
        self.deck = None
        self.sluffQueue = None
        self.lead = None
        self.legalMoves = None
        self.playHistory = None
        self.lastQueen = None
        self.trickHistory = []
        self.roundHistory = []
        self.roundNumber = 1

    # gets the current game state from the perspective of a given player
    def getGameState(self, player, isSluff):
        hand = self.deck[player]
        sluffedByYou = self.sluffQueue[player]
        passedFrom = (player - self.sluffDirection) % 4
        sluffedToYou = None
        if not isSluff:
            sluffedToYou = self.sluffQueue[passedFrom]
        gameState = GameState(hand, self.legalMoves, self.lead, sluffedByYou, sluffedToYou, player, self.sluffDirection,
                              self.playHistory, self.roundPoints, self.gamePoints)
        return gameState

    # runs rounds until the game ends
    def simGame(self):
        while not self.gameOver:
            self.dealCards()
            self.simSluff()
            self.simPlay()
            self.endRound()

    # shuffles and deals the deck
    def dealCards(self):
        undealtDeck = list(range(0, 52))
        random.shuffle(undealtDeck)
        self.deck = []
        for player in range(4):
            self.deck.append(undealtDeck[player * 13:(player + 1) * 13])

    # sims the sluffing phase of the game
    def simSluff(self):

        # reset some stuff at the beginning of each round
        self.roundPoints = [0] * 4
        self.sluffQueue = [[] for _ in range(4)]

        # get and play the bots' moves
        for trick in range(3):
            for player in range(4):
                self.setLegalMoves(player, True)
                move = getBotSluff(self.players[player], self.getGameState(player, True))
                self.sluffCard(move, player)

            # update trickHistory
            row = dict(zip(TRICK_COLUMNS, [self.season, self.gameNumber, self.roundNumber, trick - 3,
                                           self.sluffQueue[0][trick], self.sluffQueue[1][trick],
                                           self.sluffQueue[2][trick],
                                           self.sluffQueue[3][trick], -1, -1]))
            self.trickHistory.append(row)

        # transfer cards to the correct players
        for player in range(4):
            sluffTo = (player + self.sluffDirection) % 4

            for i in range(3):
                self.deck[sluffTo].append(self.sluffQueue[player][i])

    # receives a player's move and updates the game state accordingly
    def sluffCard(self, move, player):
        numCards = len(self.legalMoves)

        # replace invalid move index with random move
        if not 0 <= move < numCards:
            move = random.randint(0, numCards - 1)

        card = self.legalMoves[move]
        handIndex = self.deck[player].index(card)

        self.sluffQueue[player].append(card)
        del self.deck[player][handIndex]

    # simulates the play section of the game
    def simPlay(self):
        # reset playHistory
        self.playHistory = [[] for _ in range(4)]

        # get the player with the 2 of clubs
        self.lead = [i for i in range(4) if 0 in self.deck[i]][0]

        # for each trick:
        for trick in range(13):
            for i in range(4):
                # get whose turn it is
                player = (self.lead + i) % 4
                self.setLegalMoves(player, False)
                move = getBotPlay(self.players[player], self.getGameState(player, False))
                self.playCard(move, player)

            oldLead = self.lead

            # set the new lead and assign points
            self.setNewLead()

            # update trickHistory
            row = dict(zip(TRICK_COLUMNS, [self.season, self.gameNumber, self.roundNumber, trick,
                                           self.playHistory[0][trick], self.playHistory[1][trick],
                                           self.playHistory[2][trick], self.playHistory[3][trick], oldLead, self.lead]))
            self.trickHistory.append(row)

    # receives a player's play and updates the game state accordingly
    def playCard(self, move, player):
        numCards = len(self.legalMoves)

        # replace invalid move index with random move
        if not 0 <= move < numCards:
            move = random.randint(0, numCards - 1)

        card = self.legalMoves[move]
        handIndex = self.deck[player].index(card)

        # move the card from the deck to playHistory
        self.playHistory[player].append(card)
        del self.deck[player][handIndex]

    # finds the legal moves for the given player and adds them to the game state
    def setLegalMoves(self, player, isSluff):
        hand = self.deck[player]
        legalMoves = []

        # for each card:
        for card in hand:

            # if it's a sluff
            if isSluff:
                legalMoves.append(card)

            # if it's the lead player
            elif player == self.lead:

                # if it's the first trick:
                if len(self.playHistory[self.lead]) == 0:

                    # if it's the 2 of spades:
                    if card == 0:
                        legalMoves.append(card)

                # if it's not the first trick:
                else:

                    # if it's a heart
                    if card >= 39:

                        # check whether a penalty card has been played yet
                        penaltyPlayed = False
                        for playerHistory in self.playHistory:
                            for playedCard in playerHistory:
                                if (playedCard == 36) | (playedCard >= 39):
                                    penaltyPlayed = True

                        # if a penalty has been played:
                        if penaltyPlayed:
                            legalMoves.append(card)

                        # if a penalty has not been played:
                        else:

                            # check if the hand is only penalties
                            onlyPenalties = True
                            for handCard in hand:
                                if (handCard != 36) & (handCard < 39):
                                    onlyPenalties = False

                            # if the hand is only penalties:
                            if onlyPenalties:
                                legalMoves.append(card)

                    # if it's not a heart:
                    else:
                        legalMoves.append(card)

            # if it's not the lead player
            else:

                # get the lead suit
                leadSuit = math.floor(self.playHistory[self.lead][-1] / 13)

                # if it's the same suit
                if math.floor(card / 13) == leadSuit:
                    legalMoves.append(card)

                # if it's not the same suit
                else:

                    # check if that suit is in the hand
                    suitPresent = False
                    for handCard in hand:
                        if math.floor(handCard / 13) == leadSuit:
                            suitPresent = True

                    # if that suit is not in the hand
                    if not suitPresent:
                        legalMoves.append(card)


        self.legalMoves = legalMoves

    # figure out who won the trick and make them lead the next one
    def setNewLead(self):
        trick = len(self.playHistory[0]) - 1
        winningCard = self.playHistory[self.lead][trick]

        # for each card played that round
        for player in range(4):
            playerCard = self.playHistory[player][trick]

            # if it is the same suit but greater:
            if (math.floor(playerCard / 13) == math.floor(winningCard / 13)) & (playerCard > winningCard):
                # set the new lead and winningCard
                self.lead = player
                winningCard = playerCard

        # assign points
        for i in range(4):
            if self.playHistory[i][trick] == 36:
                self.roundPoints[self.lead] += 13
                self.lastQueen = self.lead
            elif self.playHistory[i][trick] > 38:
                self.roundPoints[self.lead] += 1

    # do behavior that needs to happen at the end of each round
    def endRound(self):

        # check if anyone shot the moon and add the points everyone got to gamePoints
        if self.roundPoints[0] == 26:
            self.roundPoints = [0, 26, 26, 26]
        elif self.roundPoints[1] == 26:
            self.roundPoints = [26, 0, 26, 26]
        elif self.roundPoints[2] == 26:
            self.roundPoints = [26, 26, 0, 26]
        elif self.roundPoints[3] == 26:
            self.roundPoints = [26, 26, 26, 0]

        self.gamePoints[0] += self.roundPoints[0]
        self.gamePoints[1] += self.roundPoints[1]
        self.gamePoints[2] += self.roundPoints[2]
        self.gamePoints[3] += self.roundPoints[3]

        # add it to the round history
        roundRow = dict(zip(ROUND_COLUMNS, [self.season, self.gameNumber, self.roundNumber, self.roundPoints[0],
                                            self.roundPoints[1], self.roundPoints[2], self.roundPoints[3],
                                            self.lastQueen]))

        self.roundHistory.append(roundRow)

        # check if game over
        for player in range(4):
            if self.gamePoints[player] >= 100:
                self.gameOver = True

        self.roundNumber += 1
        self.sluffDirection = (self.sluffDirection + 1) % 3 + 1

    # gets thea row containing the basic info about the game
    def getGameHistory(self):

        # some counters
        hearts = [0] * 4
        queens = [0] * 4
        tricks = [0] * 4

        # for each trick
        for trick in self.trickHistory:
            winner = trick["Winner"]

            # if there was a winner:
            if winner >= 0:
                tricks[winner] += 1

                for card in CARD_SUB:
                    if trick[card] == 36:
                        queens[winner] += 1
                    elif trick[card] >= 39:
                        hearts[winner] += 1

        row = dict(zip(GAME_COLUMNS, [self.season, self.gameNumber, self.playerNames[0], self.playerNames[1],
                                      self.playerNames[2], self.playerNames[3], self.gamePoints[0], self.gamePoints[1],
                                      self.gamePoints[2], self.gamePoints[3], hearts[0], hearts[1], hearts[2],
                                      hearts[3], queens[0], queens[1], queens[2], queens[3], tricks[0], tricks[1],
                                      tricks[2], tricks[3]]))
        return row


class GameState:
    def __init__(self, hand, legalMoves, lead, sluffedByYou, sluffedToYou, whichPlayer, sluffDirection, playHistory,
                 roundPoints, gamePoints):
        self.hand = hand
        self.legalMoves = legalMoves
        self.lead = lead
        self.playHistory = playHistory
        self.roundPoints = roundPoints
        self.gamePoints = gamePoints
        self.whichPlayer = whichPlayer
        self.sluffDirection = sluffDirection
        self.sluffedByYou = sluffedByYou
        self.sluffedToYou = sluffedToYou


# ACTUAL STUFF


runLeague()
