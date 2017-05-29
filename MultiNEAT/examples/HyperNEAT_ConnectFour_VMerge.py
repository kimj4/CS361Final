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

# sys.path.insert(0, '/accounts/sharpeg/CS361Final')
# sys.path.insert(0, '/home/ubuntu/CS361Final')
sys.path.insert(0, '/home/juyun/CS361Final')
import MultiNEAT as NEAT
from MultiNEAT import GetGenomeList, ZipFitness, EvaluateGenomeList_Serial, EvaluateGenomeList_Parallel

import ConnectFour2
from ConnectFour2 import Game, GameTree, PossibleMove, printGame

def play(player1, player2, substrate, symmetry, printing, hyper):
    game = Game()
    if isinstance(player1, NEAT.Genome):
        player1Net = NEAT.NeuralNetwork()
        if hyper:
            player1.BuildHyperNEATPhenotype(player1Net,substrate)
        else:
            player1.BuildPhenotype(player1Net)
    if isinstance(player2, NEAT.Genome):
        player2Net = NEAT.NeuralNetwork()
        if hyper:
            player2.BuildHyperNEATPhenotype(player2Net,substrate)
        else:
            player2.BuildPhenotype(player2Net)

    curPlayer = 1
    numMoves = 0
    while True:
        if printing:
            game.printGrid()
        if curPlayer == 1:
            player = player1
        else:
            player = player2
        if player=="Human":
            moveFound = 0
            while not moveFound:
                humanMove = input("your move [1, 7]")
                moveFound = game.makeMove(curPlayer, humanMove - 1)
        elif player=="Random":
            #game.printGrid(game.grid)
            moveFound = 0
            while not moveFound:
                randomMove = rnd.randint(0,6)
                moveFound = game.makeMove(curPlayer, randomMove)
            #game.printGrid(game.grid)
        else:
            if curPlayer == 1:
                makeMove(1,player1Net,game,symmetry)
            else:
                makeMove(2,player2Net,game,symmetry)
        outcome = game.evaluate()
        curPlayer = 3-curPlayer
        numMoves += 1
        if outcome != 0:
            winner = outcome
            break
    #print str(numMoves)
    return winner

def makeMove(player, playerNet, game, symmetry):
    ''' Analyzes the game tree to a certain depth, feeds those trees as input to
    the NN, and makes the move depending on what it thought each outcome was
    worth.
    '''
    if symmetry:
        gameTree = GameTree(1, game, player)
    else:
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
    indices = range(gameTree.length())
    rnd.shuffle(indices)
    for i in indices:
        if outputList[i] < bestValueSoFar:
            bestValueSoFar = outputList[i]
            bestIndexSoFar = gameTree.getPMAt(i).moves[0]

    game.makeMove(player, bestIndexSoFar)

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

def evaluate(genomeNum, popGenomeList, gameMatrix, gamesSoFar, substrate, symmetry, hyper):
    # build the NN for the individual that we are evaluating.
    p1Genome = popGenomeList[genomeNum]
    player1Net = NEAT.NeuralNetwork()
    player1Net.SetInputOutputDimentions(2, 1)
    if hyper:
        p1Genome.BuildHyperNEATPhenotype(player1Net,substrate)
    else:
        p1Genome.BuildPhenotype(player1Net)

    numToPlay = (10 - sum(gamesSoFar[genomeNum]))/2.0
    indicesToPlay = []
    #see how many games you have to play, find that many you havent played and play them
    while len(indicesToPlay)< numToPlay:
        try:
            i = rnd.randint(0,len(popGenomeList)-1)
            #dont play someone that is you, that youve played, or who has all their games, or you're already gonna play
            canPlay = True
            if i == genomeNum:
                canPlay = False
            if gameMatrix[genomeNum][i] == True:
                canPlay = False
            if i in indicesToPlay:
                canPlay = False
            if canPlay:
                indicesToPlay.append(i)
        except(IndexError):
            pass

    #play each of the randomly selected genomes twice
    for i in indicesToPlay:
        # print("printprint")

        p2Genome = popGenomeList[i]
        # build opponent NN
        player2Net = NEAT.NeuralNetwork()
        player2Net.SetInputOutputDimentions(2, 1)
        if hyper:
            p2Genome.BuildHyperNEATPhenotype(player2Net, substrate)
        else:
            p2Genome.BuildPhenotype(player2Net)

        winner1 = play(p1Genome, p2Genome, substrate, symmetry, False, False)
        winner2 = play(p2Genome, p1Genome, substrate, symmetry, False, False)

        p1wins,p2wins,ties = 0,0,0
        if winner1 == 1:
            p1wins += 1
        elif winner1 == 2:
            p2wins += 1
        else:
            ties += 1

        if winner2 == 1:
            p2wins += 1
        elif winner2 == 2:
            p1wins += 1
        else:
            ties += 1

        gameMatrix[genomeNum][i]=True
        gameMatrix[i][genomeNum]=True

        gamesSoFar[genomeNum][0]+=p1wins
        gamesSoFar[genomeNum][1]+=ties
        gamesSoFar[genomeNum][2]+=p2wins

        gamesSoFar[i][0]+=p2wins
        gamesSoFar[i][1]+=ties
        gamesSoFar[i][2]+=p1wins

    #then play random 4 times
    winner1 = play(p1Genome, "Random", substrate, symmetry, False, False)
    winner2 = play("Random", p1Genome, substrate, symmetry, False, False)
    winner3 = play(p1Genome, "Random", substrate, symmetry, False, False)
    winner4 = play("Random", p1Genome, substrate, symmetry, False, False)

    p1wins,p2wins,ties = 0,0,0
    if winner1 == 1:
        p1wins += 1
    elif winner1 == 2:
        p2wins += 1
    else:
        ties += 1

    if winner2 == 1:
        p2wins += 1
    elif winner2 == 2:
        p1wins += 1
    else:
        ties += 1

    if winner3 == 1:
        p1wins += 1
    elif winner3 == 2:
        p2wins += 1
    else:
        ties += 1

    if winner4 == 1:
        p2wins += 1
    elif winner4 == 2:
        p1wins += 1
    else:
        ties += 1

    gamesSoFar[genomeNum][0]+=p1wins
    gamesSoFar[genomeNum][1]+=ties
    gamesSoFar[genomeNum][2]+=p2wins

def main():
    output_file = sys.argv[1]
    output_file = open(output_file,"w")

    symmetry = sys.argv[2]

    params = NEAT.Parameters()

    params.PopulationSize = 25 #changed
    params.TournamentSize = 2 #changed

    params.DynamicCompatibility = True
    params.CompatTreshold = 2.0
    params.YoungAgeTreshold = 15
    params.SpeciesMaxStagnation = 100
    params.OldAgeTreshold = 35

    params.MinSpecies = 2 #changed
    params.MaxSpecies = 4 #changed
    params.RouletteWheelSelection = False

    params.MutateRemLinkProb = 0.02
    params.RecurrentProb = 0
    params.OverallMutationRate = 0.30 #changed
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

    # set properties here

    inputCoordinateList = []
    for x in range(14):
        for y in range(6):
            inputCoordinateList.append((x,y))

    hiddenCoordinateList = []
    for x in range(14):
        for y in range(6):
            hiddenCoordinateList.append((x,y+6))

    substrate = NEAT.Substrate(inputCoordinateList,hiddenCoordinateList,[(0,0)])
    substrate.m_allow_input_hidden_links = True
    substrate.m_allow_input_output_links = False #do we really want this true
    substrate.m_allow_hidden_hidden_links = False
    substrate.m_allow_hidden_output_links = True
    substrate.m_allow_output_hidden_links = False
    substrate.m_allow_output_output_links = False
    substrate.m_allow_looped_hidden_links = False
    substrate.m_allow_looped_output_links = False


    substrate.m_hidden_nodes_activation = NEAT.ActivationFunction.SIGNED_SIGMOID
    substrate.m_output_nodes_activation = NEAT.ActivationFunction.UNSIGNED_SIGMOID

    substrate.m_with_distance = True

    substrate.m_max_weight_and_bias = 8.0

    #   params: (id,
    #            number of inputs,
    #            number of hidden (ignored for seed_type 0, specifies number of hidden nodes for seed_type 1)),
    #            number of outputs
    #            a_FS_NEAT,
    #            output activation function type,
    #            hidden activation function type,
    #            seed type,
    #            parameters object,
    genome = NEAT.Genome(0,
                    substrate.GetMinCPPNInputs(),
                    0,
                    substrate.GetMinCPPNOutputs(),
                    False,
                    NEAT.ActivationFunction.TANH,
                    NEAT.ActivationFunction.TANH,
                    0,
                    params)
    #                    (genome, params, ramdomize weights, random range, rng seed)
    pop1 = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed
    pop1.RNG.Seed(rnd.randint(1,10000))

    for generation in range(100):
        #play("Human",NEAT.GetGenomeList(pop1)[1],substrate,symmetry,True, False)
        print("generation: "+str(generation))
        gameMatrix = []
        gamesSoFar = []
        for i in range(params.PopulationSize):
            gameMatrix.append([])
            for j in range(params.PopulationSize):
                gameMatrix[i].append(False)
            gamesSoFar.append([0,0,0])

        for i in range(params.PopulationSize):
            if sum(gamesSoFar[i]) < 10:
                # genomeNum, popGenomeList, gameMatrix, gamesSoFar, substrate, symmetry, hyper
                evaluate(i, NEAT.GetGenomeList(pop1), gameMatrix, gamesSoFar, substrate, symmetry, False)
        print(gamesSoFar)

        for i in range(params.PopulationSize):
            games = sum(gamesSoFar[i])
            fitness = (gamesSoFar[i][0] + gamesSoFar[i][1] * .5) / games
            NEAT.GetGenomeList(pop1)[i].SetFitness(fitness)

        bestIndividual = findBestIndividual(pop1)

        randomWins = 0
        for i in range(7):
            winner1 = play("Random",bestIndividual,substrate,symmetry,False,False)
            winner2 = play(bestIndividual,"Random",substrate,symmetry,False,False)
            if winner1 == 2:
                randomWins += 1
            elif winner1 == 3:
                randomWins += .5
            if winner2 == 1:
                randomWins += 1
            elif winner2 == 3:
                randomWins += .5
            print str(winner1==2)+" "+str(winner2==1)
        output_file.write(str(generation)+","+str(randomWins)+"\n")
        print("gen "+str(generation)+" beats random "+str(randomWins)+" out of 14")
        pop1.Epoch()

        end = time.time()

    play("Human",NEAT.GetGenomeList(pop1)[bestFitnessIndex],substrate,symmetry,True, False)

main()
