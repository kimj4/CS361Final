#!/usr/bin/python3
'''
Evolving players for connect four using MultiNEAT.
The framework being used is HyperNEAT
The code below is just TestHyperNEAT_xor.py for now
'''

import os
import sys
sys.path.insert(0, '/home/peter/code/projects/MultiNEAT') # duh
import time
import random as rnd
import subprocess as comm
import pickle as pickle
import MultiNEAT as NEAT
from MultiNEAT import GetGenomeList, ZipFitness, EvaluateGenomeList_Serial, EvaluateGenomeList_Parallel

from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, '/home/juyun/CS361Final')
from ConnectFour import MyConnectFour
from ConnectFour import DoubleGrid


from datetime import datetime

####### added code

params = NEAT.Parameters()
params.PopulationSize = 10
# set properties here

#   params: (id,
#            number of inputs,
#            number of hidden (ignored for seed_type 0, specifies number of hidden nodes for seed_type 1)),
#            number of outputs
#            a_FS_NEAT,
#            output activation function type,
#            hidden activation function type,
#            seed type,
#            parameters object,
genome = NEAT.Genome(0, 7 * 6 * 2, 0, 7, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)
# two inputs per board position
# seven outputs that spits out the fitness of the move made at that column


#                    (genome, params, ramdomize weights, random range, rng seed)
pop1 = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed
pop2 = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed

'''
coevolution may be possible. in order to evaluate an individual.
To evaluate an individual, pass in the population that it will match against.
- Consider some kind of sampling
- Consider both cases: p1 goes first, p1 goes second
'''

def evaluate(genome, population):
    # build the NN for the individual that we are evaluating.
    player1Net = NEAT.NeuralNetwork()
    player1Net.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(player1Net)

    p1FirstWins = 0
    p1SecondWins = 0
    p1FirstTies = 0
    p1SecondTies = 0

    # For now, play two rounds with each of the individuals in the population
    popGenomeList = NEAT.GetGenomeList(population)
    for p2Genome in popGenomeList:
        # build opponent NN
        player2Net = NEAT.NeuralNetwork()
        player2Net.SetInputOutputDimentions(2, 1)
        p2Genome.BuildPhenotype(player2Net)

        # Game where p1 goes first
        curPlayer = 1
        winner = 0
        game = MyConnectFour(1)
        while (True):
            if curPlayer == 1:
                makeMove(1, player1Net, game)
                outcome = game.getGameOutcome(game.grid)
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
                outcome = game.getGameOutcome(game.grid)
            else:
                print("catastrophic failure")

            curPlayer = (curPlayer % 2) + 1
            if outcome != 0:
                winner = outcome
                break

        if winner == 1:
            p1FirstWins += 1
        if winner == 3:
            p1FirstTies += 1


        # Game where p2 goes first
        curPlayer = 2
        winner = 0
        game = MyConnectFour(1)
        while (True):
            if curPlayer == 1:
                makeMove(1, player1Net, game)
                outcome = game.getGameOutcome(game.grid)
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
                outcome = game.getGameOutcome(game.grid)
            else:
                print("catastrophic failure")

            curPlayer = (curPlayer % 2) + 1
            if outcome != 0:
                winner = outcome
                break

        if winner == 1:
            p1SecondWins += 1
        if winner == 3:
            p1SecondTies += 1

    print("one evaluatation complete")
    return p1FirstWins + p1SecondWins + 0.5 * (p1FirstTies + p1SecondTies)

def makeMove(player, playerNet, game):
    playerPotentials = game.getPotentialDoubleGridsFlat(player)
    outputList = []
    for i in range(len(playerPotentials)):
        listOfMinimums = []
        if (isinstance(playerPotentials[i], list)):
            for j in range(len(playerPotentials[i])):
                if playerPotentials[i][j] != None:
                    # print(playerPotentials[i][j])
                    # game.printGrid(playerPotentials[i][j].getDoubleGrid())
                    playerNet.Input(playerPotentials[i][j].makeIntoList())
                    playerNet.Activate()
                    # print("\n")
                    for output in playerNet.Output():
                        listOfMinimums.append(output)
                        # print(output)
                    # print("\n")

        elif game.isDoubleGrid(playerPotentials[i]):
            playerNet.Input(playerPotentials[i].makeIntoList())
            playerNet.Activate()
            # print("\n")
            for output in playerNet.Output():
                listOfMinimums.append(output)
                # print(output)
            # print("\n")
        outputList.append(listOfMinimums)

    bestIndexSoFar = -1
    bestMinSoFar = -10000
    for i in range(len(outputList)):
        # print(outputList[i])
        if outputList[i] != [] and outputList[i] != None:
            minimum = min(outputList[i])
            if minimum > bestMinSoFar:
                bestIndexSoFar = i
                bestMinSoFar = minimum

    game.actualMove(bestIndexSoFar, player)

def playAgainstHuman(genome):
    game = MyConnectFour(1)

    computerNet = NEAT.NeuralNetwork()
    computerNet.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(computerNet)

    game.printGrid(game.grid)
    while (True):
        humanMove = input("your move [1, 7]")
        game.actualMove(humanMove - 1, 1)
        outcome = game.getGameOutcome(game.grid)
        game.printGrid(game.grid)
        if outcome != 0:
            winner = outcome
            break

        makeMove(2, computerNet, game)
        outcome = game.getGameOutcome(game.grid)
        game.printGrid(game.grid)
        if outcome != 0:
            winner = outcome
            break

    if winner == 1:
        print("Computer still isn't very good")
    elif winner == 2:
        print("Wow, we evolved a pretty good player")
    else:
        print("????")




for generation in range(100):
    start = time.time()

    # playAgainstHuman(NEAT.GetGenomeList(pop1)[5])


    for genome in NEAT.GetGenomeList(pop1):
        fitness = evaluate(genome, pop2)
        genome.SetFitness(fitness)

    for genome in NEAT.GetGenomeList(pop2):
        fitness = evaluate(genome, pop1)
        genome.SetFitness(fitness)

    pop1.Epoch()
    pop2.Epoch()

    end = time.time()
    print(end - start)





####### end added code
