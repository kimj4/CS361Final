#!/usr/bin/python3
'''
A different version of using Evolutionary NNs as to evolve a player to make a
move. This is a more naive approach where the NN is just given a board state as
input and it pops out 7 numbers each marking the 'goodness' of dropping a piece
in that column.
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


params = NEAT.Parameters()
params.PopulationSize = 20

params.DynamicCompatibility = True
params.CompatTreshold = 2.0
params.YoungAgeTreshold = 15
params.SpeciesMaxStagnation = 100
params.OldAgeTreshold = 35
params.MinSpecies = 1
params.MaxSpecies = 3
params.RouletteWheelSelection = False
params.EliteFraction = .1 # this variable may end up being important

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


genome = NEAT.Genome(0, 7 * 6 * 2, 0, 7, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)


pop1 = NEAT.Population(genome, params, True, 1.0, 2345987)
pop2 = NEAT.Population(genome, params, True, 1.0, 9827348)


def evaluateCoevolution(genome, population):
    ''' Evaluates an individual against the members of another population by
    matching them. Fitness is a function of wins and ties
    '''
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

        p1MoveIndexes = []
        p2MoveIndexes = []

        while (True):
            if curPlayer == 1:
                p1MoveIndexes.append(makeMove(1, player1Net, game))
            elif curPlayer == 2:
                p2MoveIndexes.append(makeMove(2, player2Net, game))
            outcome = game.evaluate()
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
                p1MoveIndexes.append(makeMove(1, player1Net, game))
            elif curPlayer == 2:
                p2MoveIndexes.append(makeMove(2, player2Net, game))
            outcome = game.evaluate()
            curPlayer = (curPlayer % 2) + 1
            if outcome != 0:
                winner = outcome
                break
        if winner == 1:
            p1SecondWins += 1
        if winner == 3:
            p1SecondTies += 1

    p1AvgMoveIdx = sum(p1MoveIndexes) / len(p1MoveIndexes)
    p2AvgMoveIdx = sum(p2MoveIndexes) / len(p2MoveIndexes)
    return [p1FirstWins + p1SecondWins + 0.5 * (p1FirstTies + p1SecondTies), p1AvgMoveIdx, p2AvgMoveIdx]

def evaluateAgainstRandom(genome, repeats):
    ''' Utility function to allow matches against multiple RNG opponents
    '''
    numWins = 0;
    for i in range(repeats):
        g1 = playAgainstRandom(genome, 1)
        if (g1[0] == 2):
            numWins += 1
        g2 = playAgainstRandom(genome, 2)
        if (g2[0] == 2):
            numWins += 1
    return [numWins, g1[1], g2[1]]



def makeMove(player, playerNet, game):
    ''' Analyzes the game tree to a certain depth, feeds those trees as input to
    the NN, and makes the move depending on what it thought each outcome was
    worth.
    '''
    gameTree = GameTree(0, game, player)
    outputList = []

    # print(gameTree.length())

    for i in range(gameTree.length()):
        iList = gameTree.getPMAt(i).getInputFormatVec(player)
        line = []
        for a in iList:
            line.append(a)

        playerNet.Flush()
        playerNet.Input(line)
        playerNet.Activate()
        # output list is size 1
        # for output in playerNet.Output():
        #     outputList.append(output)

        # The list contains the moves and how good the NN thinks they are
        for i in range(len(playerNet.Output())):
            outputList.append([i, playerNet.Output()[i]])

        # sorted in descending order
        sortedMoves = sorted(outputList, key=lambda x: x[1], reverse=True)



    # bestIndexSoFar = -1
    # bestValueSoFar = 20
    # for i in range(gameTree.length()):
    #     if outputList[i] < bestValueSoFar:
    #         bestValueSoFar = outputList[i]
    #         bestIndexSoFar = gameTree.getPMAt(i).moves[0]
    moved = False;
    curMove = 0;
    while (not moved):
        moved = game.makeMove(player, sortedMoves[curMove][0])
        curMove += 1
        if (curMove > 7):
            print("uh oh")
            break;
    return curMove - 1 # the index at which the move was made.

def matchNNs(genome1, genome2):
    ''' Play two NNs against each other. Two games are played where each NN goes
    first. Returns an array containing number of wins for each player and the
    number of ties.
    '''
    player1Net = NEAT.NeuralNetwork()
    player1Net.SetInputOutputDimentions(2, 1)
    genome1.BuildPhenotype(player1Net)

    player2Net = NEAT.NeuralNetwork()
    player2Net.SetInputOutputDimentions(2, 1)
    genome2.BuildPhenotype(player2Net)

    p1Wins = 0
    p2Wins = 0
    ties = 0

    p1MoveIndexes = []
    p2MoveIndexes = []

    curPlayer = 1
    for game in range(2):
        game = Game()
        while (True):
            if (curPlayer == 1):
                p1MoveIndexes.append(makeMove(1, player1Net, game))
            elif (curPlayer == 2):
                p2MoveIndexes.append(makeMove(2, player2Net, game))
            winner = game.evaluate()
            if (winner == 1):
                p1Wins += 1
                break;
            elif (winner == 2):
                p2Wins += 1
                break;
            else:
                ties += 1
                break;
            curPlayer = curPlayer % 2 + 1
        curPlayer = 2

    p1AvgMoveIdx = sum(p1MoveIndexes) / len(p1MoveIndexes)
    p2AvgMoveIdx = sum(p2MoveIndexes) / len(p2MoveIndexes)
    return [p1Wins, p2Wins, ties, p1AvgMoveIdx, p2AvgMoveIdx]




def playAgainstHuman(genome, firstPlayer):
    ''' Simulates a connect four game where one player is a NN and the other is
    a person. If firstPlayer = 1, the NN moves first. If firstPlayer = 2, the
    RNG moves first.
    '''
    game = Game()
    computerNet = NEAT.NeuralNetwork()
    computerNet.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(computerNet)
    printGame(game.gameGrid);
    curPlayer = firstPlayer
    while (True):
        if (curPlayer == 1):
            humanMove = input("your move [1, 7]")
            game.makeMove(1, humanMove - 1)
        elif (curPlayer == 2):
            makeMove(2, computerNet, game)
        outcome = game.evaluate()
        printGame(game.gameGrid);
        if outcome != 0:
            winner = outcome
            break
        curPlayer = curPlayer % 2 + 1
    if winner == 1:
        print("Computer still isn't very good")
    elif winner == 2:
        print("Wow, we evolved a pretty good player")
    else:
        print("Tied. Woah")


def playAgainstRandom(genome, firstPlayer):
    ''' Simulates a connect four game where one player is a NN and the other is
    an RNG. If firstPlayer = 1, the NN moves first. If firstPlayer = 2, the
    RNG moves first.
    '''
    game = Game()

    computerNet = NEAT.NeuralNetwork()
    computerNet.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(computerNet)
    curPlayer = firstPlayer

    movesIndexes = []

    while (True):
        if (curPlayer == 1):
            game.makeMove(curPlayer, rnd.randint(0, 6))
        elif (curPlayer == 2):
            movesIndexes.append(makeMove(curPlayer, computerNet, game))
        outcome = game.evaluate()
        if outcome != 0:
            winner = outcome
            break
        curPlayer = curPlayer % 2 + 1

    avgMoveIdx = sum(movesIndexes) / len(movesIndexes)
    return [winner, avgMoveIdx]

def findBestIndividual(pop):
    ''' Returns the genome of the individual with the highest fitness in the
    given population
    '''
    bestFitness = -1
    bestGenome = None
    for genome in NEAT.GetGenomeList(pop):
        if (genome.GetFitness() > bestFitness):
            bestFitness = genome.GetFitness()
            bestGenome = genome
    return genome


def coevolve():
    ''' Two populations evolve side by side. Each individual plays with a
    certain sample of the other population. For now, the sample is the whole
    population.
    '''
    for generation in range(100):
        # print("generation: " + str(generation))
        start = time.time()

        NNWins = 0
        for genome in NEAT.GetGenomeList(pop1):
            fitness = evaluate(genome, pop2)
            genome.SetFitness(fitness)
            if (playAgainstRandom(genome, 1) == 2):
                NNWins += 1
        # playAgainstHuman(findBestIndividual(pop1))


        for genome in NEAT.GetGenomeList(pop2):
            fitness = evaluate(genome, pop1)
            genome.SetFitness(fitness)
            if (playAgainstRandom(genome, 1) == 2):
                NNWins += 1
        # playAgainstHuman(findBestIndividual(pop2))

        print("Generation " + str(generation) + " win rate against random: " + str(NNWins/20.0) )
        pop1.Epoch()
        pop2.Epoch()

        end = time.time()
        print(end - start)

def randEvolve():
    ''' One population is evolved where the fitness is a function of the number
    of games that an individual wins against randomly-behaving players
    '''
    for generation in range(100):
        start = time.time()
        for genome in NEAT.GetGenomeList(pop1):
            fitness = evaluateAgainstRandom(genome, 10)
            genome.SetFitness(fitness)

        pop1.Epoch()
        end = time.time()
        print(end - start)

        if (generation % 10 == 0):
            playAgainstHuman(findBestIndividual(pop1))

def randAndCoevolve():
    ''' Uses one population to evaluated via playing a certain number of random
    opponents and themselves. More emphasis on the random players
    '''
    for generation in range(100):
        start = time.time()
        for genome in NEAT.GetGenomeList(pop1):
            fitness = 2 * evaluateAgainstRandom(genome, 10) + evaluateCoevolution(genome, pop1)
            genome.SetFitness(fitness)

        pop1.Epoch()
        end = time.time()
        print(end - start)
        if (generation % 10 == 0):
            playAgainstHuman(findBestIndividual(pop1), rnd.randint(1, 2))

def randAndCoevolveHOF():
    ''' Same as randAndCoevolve but uses a form of the hall-of-fame method.
    Store some number of elite individuals from each generation and use them
    in the evaluation of individuals in subsequent generations.
    '''
    # HOF is a list of genomes
    HOF = []
    for generation in range(1000):
        start = time.time()
        for genome in NEAT.GetGenomeList(pop1):
            r = evaluateAgainstRandom(genome, 10)
            # print("random wins ratio: " + str(randomWins / 20.0))
            a = evaluateCoevolution(genome, pop1)
            fitness = r[0] / (r[1] + 1)  + 2 * a[0] / (a[1] + 1)

        #     numEliteWins = 0
        #     for elite in HOF:
        #         numEliteWins += matchNNs(genome, elite)[0]
        #
        #     # punish individuals for beating less than half of the HOF elites
        #     if (len(HOF) > 0): # just to avoid divide-by-zero errors
        #         if ((numEliteWins / 2.0) / len(HOF) < 0.5):
        #             fitness /= 2.0
        #         genome.SetFitness(fitness)
        #
        # if findBestIndividual(pop1) not in HOF:
        #     HOF.append(findBestIndividual(pop1))

        pop1.Epoch()
        end = time.time()
        print(end - start)
        if (generation % 200 == 0):
            playAgainstHuman(findBestIndividual(pop1), rnd.randint(1, 2))
        if (generation % 999 == 0):
            playAgainstHuman(findBestIndividual(pop1), rnd.randint(1, 2))

# randEvolve()
# coevolve()
# randAndCoevolve()
randAndCoevolveHOF()
