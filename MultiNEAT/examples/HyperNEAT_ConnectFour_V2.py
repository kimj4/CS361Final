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
import pickle
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
params.PopulationSize = 10

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


genome = NEAT.Genome(0, 7 * 6 * 2, 0, 1, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)


pop1 = NEAT.Population(genome, params, True, 1.0, 2345987) # the 0 is the RNG seed
pop2 = NEAT.Population(genome, params, True, 1.0, 9827348) # the 0 is the RNG seed


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
        while (True):
            if curPlayer == 1:
                makeMove(1, player1Net, game)
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
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
                makeMove(1, player1Net, game)
            elif curPlayer == 2:
                makeMove(2, player2Net, game)
            outcome = game.evaluate()
            curPlayer = (curPlayer % 2) + 1
            if outcome != 0:
                winner = outcome
                break
        if winner == 1:
            p1SecondWins += 1
        if winner == 3:
            p1SecondTies += 1
    return p1FirstWins + p1SecondWins + 0.5 * (p1FirstTies + p1SecondTies)

def evaluateAgainstRandom(genome, repeats):
    ''' Utility function to allow matches against multiple RNG opponents
    '''
    fitness = 0;
    for i in range(repeats):
        if (playAgainstRandom(genome, 1) == 2):
            fitness += 1
        if (playAgainstRandom(genome, 2) == 2):
            fitness += 1
    return fitness



def makeMove(player, playerNet, game):
    ''' Analyzes the game tree to a certain depth, feeds those trees as input to
    the NN, and makes the move depending on what it thought each outcome was
    worth.
    '''
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

    curPlayer = 1
    for game in range(2):
        game = Game()
        while (True):
            if (curPlayer == 1):
                makeMove(1, player1Net, game)
            elif (curPlayer == 2):
                makeMove(2, player2Net, game)
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

    return [p1Wins, p2Wins, ties]




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

    while (True):
        if (curPlayer == 1):
            game.makeMove(curPlayer, rnd.randint(0, 6))
        elif (curPlayer == 2):
            makeMove(curPlayer, computerNet, game)
        outcome = game.evaluate()
        if outcome != 0:
            winner = outcome
            break
        curPlayer = curPlayer % 2 + 1
    return winner

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
    f = open('genomes.txt', 'w')

    # HOF is a list of genomes
    HOF = []
    print("1")
    for generation in range(100):
        start = time.time()
        for genome in NEAT.GetGenomeList(pop1):
            print("2")
            fitness = evaluateAgainstRandom(genome, 10) + evaluateCoevolution(genome, pop1)
            print("3")

            numEliteWins = 0
            for elite in HOF:
                print("4")
                numEliteWins += matchNNs(genome, elite)[0]
                print("5")

            # punish individuals for beating less than half of the HOF elites
            if (len(HOF) > 0): # just to avoid divide-by-zero errors
                if ((numEliteWins / 2.0) / len(HOF) < 0.5):
                    fitness /= 2.0
                genome.SetFitness(fitness)

        if findBestIndividual(pop1) not in HOF:
            print("6")
            HOF.append(findBestIndividual(pop1))
            print("7")
        else:
            print("an individual was already in HOF")

        if len(HOF) > 10:
            pickle.dump(elite, f)
            HOF.pop(0)

        pop1.Epoch()
        end = time.time()
        print(end - start)
        if (generation % 10 == 0):
            playAgainstHuman(findBestIndividual(pop1), rnd.randint(1, 2))

# randEvolve()
# coevolve()
# randAndCoevolve()
def main():

    randAndCoevolveHOF()

main()
