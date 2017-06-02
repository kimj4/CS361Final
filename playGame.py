import pickle
import hcf
import sys

def playPlayers(playersFile, playerIndex, goFirst, symmetry, hyper):
    substrate = hcf.configureSubstrate
    with open('playersFile', 'r') as f:
        listOfPlayers = pickle.load(f)
    if goFirst:
        play(listOfPlayers[playerIndex], "Human", substrate, False, True, False, GLOBAL_DEPTH)
    else:
        play(listOfPlayers[playerIndex], "Human", substrate, False, True, False, GLOBAL_DEPTH)

def main():
    if (len(sys.argv) < 3):
        print("Arguments expected")
        print("path to file containing players")
        print("the index of player you want to play in the list of players")
        print("1 if you want to go first, 0 if player goes first")
        print("1 if player used symmetry, 0 else")
        print("1 if player is HyperNEAT, 0 else")

    playersFile = sys.argv[1]
    playerIndex = sys.argv[2]
    goFirst = sys.argv[3]
    symmetry = sys.argv[4]
    hyper = sys.argv[4]

    playPlayers(playersFile, playerIndex, goFirst, symmetry, hyper)
