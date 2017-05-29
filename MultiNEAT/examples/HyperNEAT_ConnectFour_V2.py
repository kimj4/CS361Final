#!/usr/bin/python3
'''
Evolving players for connect four using MultiNEAT.
The framework being used is HyperNEAT
The code below is just TestHyperNEAT_xor.py for now
'''

import os
import sys
import time
import random as rnd
import subprocess as comm
# import Random
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, '/home/juyun/CS361Final')
# sys.path.insert(0, '/home/ubuntu/CS361Final')
import MultiNEAT as NEAT
from MultiNEAT import GetGenomeList, ZipFitness, EvaluateGenomeList_Serial, EvaluateGenomeList_Parallel

import ConnectFour2
from ConnectFour2 import Game, GameTree, PossibleMove, printGame

####### added code

params = NEAT.Parameters()
params.PopulationSize = 10

params.DynamicCompatibility = True
params.CompatTreshold = 2.0
params.YoungAgeTreshold = 15
params.SpeciesMaxStagnation = 100
params.OldAgeTreshold = 35
params.MinSpecies = 1
params.MaxSpecies = 3
params.RouletteWheelSelection = False
params.EliteFraction = .1

params.MutateRemLinkProb = 0.02
params.RecurrentProb = 0
params.OverallMutationRate = 0.15
params.MutateAddLinkProb = 0.08
params.MutateAddNeuronProb = 0.01
params.MutateWeightsProb = 0.90
params.MaxWeight = 8.0
params.WeightMutationMaxPower = 0.2
params.WeightReplacementMaxPower = 1.0

params.MutateActivationAProb = 0.0
params.ActivationAMutationMaxPower = 0.5
params.MinActivationA = 0.05
params.MaxActivationA = 6.0

params.MutateNeuronActivationTypeProb = 0.03

params.ActivationFunction_SignedSigmoid_Prob = 0.0
params.ActivationFunction_UnsignedSigmoid_Prob = 0.0
params.ActivationFunction_Tanh_Prob = 1.0
params.ActivationFunction_TanhCubic_Prob = 0.0
params.ActivationFunction_SignedStep_Prob = 1.0
params.ActivationFunction_UnsignedStep_Prob = 0.0
params.ActivationFunction_SignedGauss_Prob = 1.0
params.ActivationFunction_UnsignedGauss_Prob = 0.0
params.ActivationFunction_Abs_Prob = 0.0
params.ActivationFunction_SignedSine_Prob = 1.0
params.ActivationFunction_UnsignedSine_Prob = 0.0
params.ActivationFunction_Linear_Prob = 1.0

params.AllowLoops = False




# params.TournamentSize = 2
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
genome = NEAT.Genome(0, 7 * 6 * 2, 0, 1, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)


#                    (genome, params, ramdomize weights, random range, rng seed)
pop1 = NEAT.Population(genome, params, True, 1.0, 2345987) # the 0 is the RNG seed
pop2 = NEAT.Population(genome, params, True, 1.0, 9827348) # the 0 is the RNG seed

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
        game = Game()
        while (True):
            if curPlayer == 1:
                makeMove(1, player1Net, game)
                outcome = game.evaluate()
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
                outcome = game.evaluate()
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
        game = Game()
        while (True):
            if curPlayer == 1:
                makeMove(1, player1Net, game)
                outcome = game.evaluate()
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
                outcome = game.evaluate()
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

    return p1FirstWins + p1SecondWins + 0.5 * (p1FirstTies + p1SecondTies)

def makeMove(player, playerNet, game):
    gameTree = GameTree(1, game, player)
    outputList = []

    for i in range(gameTree.length()):
        iList = gameTree.getPMAt(i).getInputFormatVec(player)
        line = []
        for a in iList:
            line.append(a)

        playerNet.Flush()
        playerNet.Input(line)
        playerNet.Activate()
        # output list is size 1
        for output in playerNet.Output():
            outputList.append(output)

    bestIndexSoFar = -1
    bestValueSoFar = 20
    for i in range(gameTree.length()):
        if outputList[i] < bestValueSoFar:
            bestValueSoFar = outputList[i]
            bestIndexSoFar = gameTree.getPMAt(i).moves[0]

    game.makeMove(player, bestIndexSoFar)

def playAgainstHuman(genome):
    game = Game()

    computerNet = NEAT.NeuralNetwork()
    # computerNet.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(computerNet)

    printGame(game.gameGrid);
    while (True):
        humanMove = input("your move [1, 7]")
        game.makeMove(1, humanMove - 1)
        outcome = game.evaluate()
        printGame(game.gameGrid);
        if outcome != 0:
            winner = outcome
            break

        makeMove(2, computerNet, game)
        outcome = game.evaluate()
        # printGame(game.gameGrid);
        if outcome != 0:
            winner = outcome
            break

    if winner == 1:
        print("Computer still isn't very good")
    elif winner == 2:
        print("Wow, we evolved a pretty good player")
    else:
        print("Tied. Woah")


def playAgainstRandom(genome) :
    game = Game()

    computerNet = NEAT.NeuralNetwork()
    computerNet.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(computerNet)

    while (True):
        game.makeMove(1, rnd.randint(0, 6))
        outcome = game.evaluate()
        if outcome != 0:
            winner = outcome
            break

        makeMove(2, computerNet, game)
        outcome = game.evaluate()
        if outcome != 0:
            winner = outcome
            break

    return winner

def findBestIndividual(p):
    bestF = -1
    bestG = None
    for g in NEAT.GetGenomeList(p):
        if (g.GetFitness() > bestF):
            bestF = g.GetFitness()
            bestG = g
    return g


for generation in range(100):
    # print("generation: " + str(generation))
    start = time.time()

    NNWins = 0
    for genome in NEAT.GetGenomeList(pop1):
        fitness = evaluate(genome, pop2)
        genome.SetFitness(fitness)
        if (playAgainstRandom(genome) == 2):
            NNWins += 1
    # playAgainstHuman(findBestIndividual(pop1))


    for genome in NEAT.GetGenomeList(pop2):
        fitness = evaluate(genome, pop1)
        genome.SetFitness(fitness)
        if (playAgainstRandom(genome) == 2):
            NNWins += 1
    # playAgainstHuman(findBestIndividual(pop2))

    print("Generation " + str(generation) + " win rate against random: " + str(NNWins/20.0) )


    pop1.Epoch()
    pop2.Epoch()

    end = time.time()
    print(end - start)
