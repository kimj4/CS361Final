import pickle
import hcf
import sys

def playPlayers(playersFile, playerIndex, goFirst, symmetry, hyper):
    GLOBAL_DEPTH = 1
    substrate = hcf.configureSubstrate
    with open(playersFile, 'r') as f:
        listOfPlayers = pickle.load(f)
    print(goFirst)
    if goFirst:
        hcf.play("Human", listOfPlayers[playerIndex], substrate, False, True, False, GLOBAL_DEPTH)
    else:
        hcf.play(listOfPlayers[playerIndex], "Human", substrate, False, True, False, GLOBAL_DEPTH)

def main():
    if (len(sys.argv) < 5):
        print("Arguments expected")
        print("path to file containing players")
        print("the index of player you want to play in the list of players")
        print("1 if you want to go first, 0 if player goes first")
        print("1 if player used symmetry, 0 else")
        print("1 if player is HyperNEAT, 0 else")
        return

    playersFile = sys.argv[1]
    playerIndex = int(sys.argv[2])
    goFirst = int(sys.argv[3])
    symmetry = int(sys.argv[4])
    hyper = int(sys.argv[4])

    playPlayers(playersFile, playerIndex, goFirst, symmetry, hyper)

main()
