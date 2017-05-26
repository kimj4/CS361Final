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
import cv2
import numpy as np
import pickle as pickle
import MultiNEAT as NEAT
from MultiNEAT import GetGenomeList, ZipFitness, EvaluateGenomeList_Serial, EvaluateGenomeList_Parallel

from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, '/Accounts/kimj4/CS361Final')
from ConnectFour import MyConnectFour
from ConnectFour import DoubleGrid


from datetime import datetime

####### added code

params = NEAT.Parameters()
params.PopulationSize = 20
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
genome = NEAT.Genome(0, 7 * 6 * 2 + 1, 0, 1, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)
# two inputs per board position
# one output for the potential board


#                    (genome, params, ramdomize weights, random range, rng seed)
pop1 = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed
pop2 = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed

'''
coevolution may be possible. in order to evaluate an individual.
To evaluate an individual, pass in the population that it will match against.

- Consider some kind of sampling
- Consider both cases: p1 goes first, p1 goes second
'''

def evaluate(genome, genomeNum, popNum, population, scoreMatrix):
    # build the NN for the individual that we are evaluating.
    player1Net = NEAT.NeuralNetwork()
    player1Net.SetInputOutputDimentions(2, 1)
    genome.BuildPhenotype(player1Net)



    popGenomeList = NEAT.GetGenomeList(population)

    # For now, play two rounds with each of 5 individuals in the other population

    for i in rnd.sample(range(len(popGenomeList)),5):
        if popNum == 1:
            scoreMatrixEntry = scoreMatrix[genomeNum][i]
        else:
            scoreMatrixEntry = scoreMatrix[i][genomeNum]

        if scoreMatrixEntry == [0,0,0]:
            p2Genome = popGenomeList[i]
            # build opponent NN
            player2Net = NEAT.NeuralNetwork()
            player2Net.SetInputOutputDimentions(2, 1)
            p2Genome.BuildPhenotype(player2Net)

            # Game where p1 goes first
            curPlayer = 1
            winner = 0
            game = MyConnectFour(1)
            numMoves = 0
            p1FirstWins = 0
            p1SecondWins = 0
            p1FirstTies = 0
            p1SecondTies = 0
            while (True):
                if curPlayer == 1:
                    makeMove(1, player1Net, game)
                    outcome = game.getGameOutcome(game.grid)
                    numMoves += 1
                elif curPlayer == 2:
                    makeMove(2, player2Net, game)
                    outcome = game.getGameOutcome(game.grid)
                    numMoves += 1
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
                print("TIE FOUND !!!!!!!!")


            # Game where p2 goes first
            curPlayer = 2
            winner = 0
            game = MyConnectFour(1)
            numMoves2 = 0
            while (True):
                if curPlayer == 1:
                    makeMove(1, player1Net, game)
                    outcome = game.getGameOutcome(game.grid)
                    numMoves2 += 1
                elif curPlayer == 2:
                    makeMove(2, player2Net, game)
                    outcome = game.getGameOutcome(game.grid)
                    numMoves2 += 1
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
                print("TIE FOUND !!!!!!!!")

            if popNum == 1:
                scoreMatrixEntry[0]=p1FirstWins + p1SecondWins
                scoreMatrixEntry[1]=p1FirstTies + p1SecondTies
                scoreMatrixEntry[2]=2-p1FirstWins-p1SecondWins-p1FirstTies-p1SecondTies
            else:
                scoreMatrixEntry[0]=2-p1FirstWins-p1SecondWins-p1FirstTies-p1SecondTies
                scoreMatrixEntry[1]=p1FirstTies + p1SecondTies
                scoreMatrixEntry[2]=p1FirstWins + p1SecondWins
            #print("player in pop "+str(popNum)+" won "+str(p1FirstWins + p1SecondWins)+" and tied "+str(p1FirstTies + p1SecondTies))
            #print(scoreMatrixEntry)
    print("evaluated "+str(genomeNum)+" from "+str(popNum))

def getNetOutputs(player, playerNet, game, symmetry):
    playerPotentials = game.getPotentialDoubleGridsFlat(player)
    outputList = []
    for i in range(len(playerPotentials)):
        listOfMinimums = []
        if (isinstance(playerPotentials[i], list)):
            for j in range(len(playerPotentials[i])):
                if playerPotentials[i][j] != None:
                    # print(playerPotentials[i][j])
                    # game.printGrid(playerPotentials[i][j].getDoubleGrid())
                    inputs = playerPotentials[i][j].makeIntoList()
                    inputs.append(1.0)
                    playerNet.Input(inputs)
                    playerNet.Activate()
                    # print("\n")
                    for output in playerNet.Output():
                        listOfMinimums.append(output)
                        # print(output)
                    # print("\n")
                    if symmetry:
                        inputs = playerPotentials[i][j].makeIntoReverseList()
                        inputs.append(1.0)
                        playerNet.Input(inputs)
                        playerNet.Activate()
                        # print("\n")
                        for output in playerNet.Output():
                            listOfMinimums.append(output)
                            # print(output)
                        # print("\n")

        elif game.isDoubleGrid(playerPotentials[i]):
            inputs = playerPotentials[i][j].makeIntoList()
            inputs.append(1.0)
            playerNet.Input(inputs)
            playerNet.Activate()
            # print("\n")
            for output in playerNet.Output():
                listOfMinimums.append(output)
                # print(output)
            # print("\n")
            if symmetry:
                inputs = playerPotentials[i][j].makeIntoList()
                inputs.append(1.0)
                playerNet.Input(inputs)
                playerNet.Activate()
                # print("\n")
                for output in playerNet.Output():
                    listOfMinimums.append(output)
                    # print(output)
                # print("\n")
        outputList.append(listOfMinimums)
    return outputList

def makeMove(player, playerNet, game):

    outputList = getNetOutputs(player, playerNet, game, True)

    bestIndexSoFar = -1
    bestMinSoFar = -10000
    for i in range(len(outputList)):
        # print(outputList[i])
        if outputList[i] != [] and outputList[i] != None:
            minimum = min(outputList[i])
            if minimum > bestMinSoFar:
                bestIndexSoFar = i
                bestMinSoFar = minimum

    moveoutcome = game.actualMove(bestIndexSoFar, player)
    if not moveoutcome:
        print("MADE AN ILLEGAL MOVE!!!!!!!!!!!!!!    ",+str(outputList))
        print playerPotentials
        game.printGrid(game.grid)


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




for generation in range(20):
    start = time.time()



    scoreMatrix = []
    for i in range(len(NEAT.GetGenomeList(pop1))):
        scoreMatrix.append([])
        for j in range(len(NEAT.GetGenomeList(pop2))):
            scoreMatrix[i].append([0,0,0])

    for i in range(len(NEAT.GetGenomeList(pop1))):
        evaluate(NEAT.GetGenomeList(pop1)[i], i, 1, pop2, scoreMatrix)
        fitness = 0
        for j in range(len(NEAT.GetGenomeList(pop2))):
            fitness += scoreMatrix[i][j][0]
            fitness += scoreMatrix[i][j][0]*.5
        genome.SetFitness(fitness)

    for j in range(len(NEAT.GetGenomeList(pop2))):
        evaluate(NEAT.GetGenomeList(pop1)[j], j, 2, pop1, scoreMatrix)
        for i in range(len(NEAT.GetGenomeList(pop2))):
            fitness += scoreMatrix[i][j][2]
            fitness += scoreMatrix[i][j][1]*.5
        genome.SetFitness(fitness)

    pop1.Epoch()
    pop2.Epoch()

    end = time.time()
    print("generation "+str(generation)+" "+str(end - start))


playAgainstHuman(NEAT.GetGenomeList(pop1)[5])


####### end added code



#
#
#
# # the simple 2D substrate with 3 input points, 2 hidden and 1 output for XOR
#
# substrate = NEAT.Substrate([(-1, -1), (-1, 0), (-1, 1)],
#                            [(0, -1), (0, 0), (0, 1)],
#                            [(1, 0)])
#
# substrate.m_allow_input_hidden_links = False
# substrate.m_allow_input_output_links = False
# substrate.m_allow_hidden_hidden_links = False
# substrate.m_allow_hidden_output_links = False
# substrate.m_allow_output_hidden_links = False
# substrate.m_allow_output_output_links = False
# substrate.m_allow_looped_hidden_links = False
# substrate.m_allow_looped_output_links = False
#
# substrate.m_allow_input_hidden_links = True
# substrate.m_allow_input_output_links = False
# substrate.m_allow_hidden_output_links = True
# substrate.m_allow_hidden_hidden_links = False
#
# substrate.m_hidden_nodes_activation = NEAT.ActivationFunction.SIGNED_SIGMOID
# substrate.m_output_nodes_activation = NEAT.ActivationFunction.UNSIGNED_SIGMOID
#
# substrate.m_with_distance = True
#
# substrate.m_max_weight_and_bias = 8.0
#
# try:
#     x = pickle.dumps(substrate)
# except:
#     print('You have mistyped a substrate member name upon setup. Please fix it.')
#     sys.exit(1)
#
#
# def evaluate(genome):
#     net = NEAT.NeuralNetwork()
#     try:
#         genome.BuildHyperNEATPhenotype(net, substrate)
#
#         error = 0
#         depth = 5
#
#         # do stuff and return the fitness
#         net.Flush()
#
#         net.Input([1, 0, 1])
#         [net.Activate() for _ in range(depth)]
#         o = net.Output()
#         error += abs(o[0] - 1)
#
#         net.Flush()
#         net.Input([0, 1, 1])
#         [net.Activate() for _ in range(depth)]
#         o = net.Output()
#         error += abs(o[0] - 1)
#
#         net.Flush()
#         net.Input([1, 1, 1])
#         [net.Activate() for _ in range(depth)]
#         o = net.Output()
#         error += abs(o[0] - 0)
#
#         net.Flush()
#         net.Input([0, 0, 1])
#         [net.Activate() for _ in range(depth)]
#         o = net.Output()
#         error += abs(o[0] - 0)
#
#         return (4 - error) ** 2
#
#     except Exception as ex:
#         print('Exception:', ex)
#         return 1.0
#
#
# params = NEAT.Parameters()
#
# params.PopulationSize = 150
#
# params.DynamicCompatibility = True
# params.CompatTreshold = 2.0
# params.YoungAgeTreshold = 15
# params.SpeciesMaxStagnation = 100
# params.OldAgeTreshold = 35
# params.MinSpecies = 5
# params.MaxSpecies = 10
# params.RouletteWheelSelection = False
#
# params.MutateRemLinkProb = 0.02
# params.RecurrentProb = 0
# params.OverallMutationRate = 0.15
# params.MutateAddLinkProb = 0.08
# params.MutateAddNeuronProb = 0.01
# params.MutateWeightsProb = 0.90
# params.MaxWeight = 8.0
# params.WeightMutationMaxPower = 0.2
# params.WeightReplacementMaxPower = 1.0
#
# params.MutateActivationAProb = 0.0
# params.ActivationAMutationMaxPower = 0.5
# params.MinActivationA = 0.05
# params.MaxActivationA = 6.0
#
# params.MutateNeuronActivationTypeProb = 0.03
#
# params.ActivationFunction_SignedSigmoid_Prob = 0.0
# params.ActivationFunction_UnsignedSigmoid_Prob = 0.0
# params.ActivationFunction_Tanh_Prob = 1.0
# params.ActivationFunction_TanhCubic_Prob = 0.0
# params.ActivationFunction_SignedStep_Prob = 1.0
# params.ActivationFunction_UnsignedStep_Prob = 0.0
# params.ActivationFunction_SignedGauss_Prob = 1.0
# params.ActivationFunction_UnsignedGauss_Prob = 0.0
# params.ActivationFunction_Abs_Prob = 0.0
# params.ActivationFunction_SignedSine_Prob = 1.0
# params.ActivationFunction_UnsignedSine_Prob = 0.0
# params.ActivationFunction_Linear_Prob = 1.0
#
# params.AllowLoops = False
#
# def getbest(i):
#     g = NEAT.Genome(0,
#                     substrate.GetMinCPPNInputs(),
#                     0,
#                     substrate.GetMinCPPNOutputs(),
#                     False,
#                     NEAT.ActivationFunction.TANH,
#                     NEAT.ActivationFunction.TANH,
#                     0,
#                     params)
#
#     pop = NEAT.Population(g, params, True, 1.0, i)
#     pop.RNG.Seed(i)
#
#     for generation in range(2000):
#         genome_list = NEAT.GetGenomeList(pop)
#         # if sys.platform == 'linux':
#         #    fitnesses = EvaluateGenomeList_Parallel(genome_list, evaluate, display=False)
#         # else:
#         fitnesses = EvaluateGenomeList_Serial(genome_list, evaluate, display=False)
#         [genome.SetFitness(fitness) for genome, fitness in zip(genome_list, fitnesses)]
#
#         print('Gen: %d Best: %3.5f' % (generation, max(fitnesses)))
#
#         best = max(fitnesses)
#
#         pop.Epoch()
#         generations = generation
#
#         if best > 15.0:
#             break
#
#     return generations
#
#
# gens = []
# for run in range(100):
#     gen = getbest(run)
#     gens += [gen]
#     print('Run:', run, 'Generations to solve XOR:', gen)
# avg_gens = sum(gens) / len(gens)
#
# print('All:', gens)
# print('Average:', avg_gens)
