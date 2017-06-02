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

# sys.path.insert(0, '/Accounts/kimj4/CS361Final')
# sys.path.insert(0, '/accounts/sharpeg/CS361Final')
# sys.path.insert(0, '/home/ubuntu/CS361Final')
#sys.path.insert(0, '/home/juyun/CS361Final')
sys.path.insert(0, '/home/test/CS361Final')
import MultiNEAT as NEAT
from MultiNEAT import GetGenomeList, ZipFitness, EvaluateGenomeList_Serial, EvaluateGenomeList_Parallel

import ConnectFour2
from ConnectFour2 import Game, GameTree, PossibleMove, printGame, vectorPrint, printInputMatrix

def play(player1, player2, substrate, symmetry, printing, hyper, depth):
    game = Game()
    if isinstance(player1, NEAT.Genome):
        player1Net = NEAT.NeuralNetwork()
        player1Net.SetInputOutputDimentions(6*14, 10)
        if hyper:
            player1.BuildHyperNEATPhenotype(player1Net,substrate)
        else:
            player1.BuildPhenotype(player1Net)
    if isinstance(player2, NEAT.Genome):
        player2Net = NEAT.NeuralNetwork()
        player2Net.SetInputOutputDimentions(6*14, 10)
        if hyper:
            player2.BuildHyperNEATPhenotype(player2Net,substrate)
        else:
            player2.BuildPhenotype(player2Net)

    curPlayer = 1
    numMoves = 0
    while True:
        if printing:
            printGame(game.gameGrid)
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
            #game.printGame(game.grid)
            moveFound = 0
            while not moveFound:
                randomMove = rnd.randint(0,6)
                moveFound = game.makeMove(curPlayer, randomMove)
            #game.printGame(game.grid)
        elif player=="Left":
            for move in range(7):
                moveFound = game.makeMove(curPlayer, move)
                if moveFound:
                    break
        else:
            if curPlayer == 1:
                makeMove(1,player1Net,game,symmetry, depth)
            else:
                makeMove(2,player2Net,game,symmetry, depth)
        outcome = game.evaluate()
        curPlayer = 3 - curPlayer
        numMoves += 1
        if outcome != 0:
            winner = outcome
            if (printing):
                printGame(game.gameGrid)
            break
    return winner

def makeMove(player, playerNet, game, symmetry, depth):
    ''' Analyzes the game tree to a certain depth, feeds those trees as input to
    the NN, and makes the move depending on what it thought each outcome was
    worth.
    TODO: add different workings for using symmetry
    '''
    gameTree = GameTree(depth, game, player)
    outputList = []
    repeats = 3
    for i in range(gameTree.length()):

        # executed for all
        iList = gameTree.getPMAt(i).getInputFormatVec(player)
        line = []
        for a in iList:
            line.append(a)

        output2 = 100000

        playerNet.Flush()
        playerNet.Input(line)
        [playerNet.Activate() for _ in range(repeats)]

        tempOutput = []
        for output in playerNet.Output():
            # outputList.append(output)
            tempOutput.append(output)
        #print("Number of things in the output: %s" % len(tempOutput))
        #print(tempOutput)
        output1 = sum(tempOutput)


        if (symmetry):
            iList = gameTree.getPMAt(i).getInputFormatVecMirrored(player)
            line = []
            for a in iList:
                line.append(a)

            playerNet.Flush()
            playerNet.Input(line)
            [playerNet.Activate() for _ in range(repeats)]
            # output list is size 1
            output2 = sum(playerNet.Output())
        outputList.append(min(output1,output2))
    #print(outputList)
    # print(len(outputList))



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

def evaluate(genomeNum, popGenomeList, gameMatrix, gamesSoFar, substrate, symmetry, hyper, depth):

    # build the NN for the individual that we are evaluating.
    p1Genome = popGenomeList[genomeNum]
    player1Net = NEAT.NeuralNetwork()
    player1Net.SetInputOutputDimentions(6*14, 10)
    if hyper:
        p1Genome.BuildHyperNEATPhenotype(player1Net,substrate)
    else:
        p1Genome.BuildPhenotype(player1Net)

    numToPlay = (10 - sum(gamesSoFar[genomeNum]))/2.0
    indicesToPlay = []

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
        player2Net.SetInputOutputDimentions(6*14, 10)
        if hyper:
            p2Genome.BuildHyperNEATPhenotype(player2Net, substrate)
        else:
            p2Genome.BuildPhenotype(player2Net)

        winner1 = play(p1Genome, p2Genome, substrate, symmetry, False, False, depth)
        winner2 = play(p2Genome, p1Genome, substrate, symmetry, False, False, depth)

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


def configureParams():
    ''' Set the parameters that we need.
    '''
    params = NEAT.Parameters()
    params.PopulationSize = 25 #changed
    params.TournamentSize = 4 #changed

    params.DynamicCompatibility = True
    params.CompatTreshold = 2.0
    params.YoungAgeTreshold = 15
    params.SpeciesMaxStagnation = 3
    params.OldAgeTreshold = 10
    params.EliteFraction = 0.1

    params.MinSpecies = 1 #changed
    params.MaxSpecies = 6 #changed
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
    # params.MinActivationA = 0.05
    # params.MaxActivationA = 6.0

    params.MutateNeuronActivationTypeProb = 0.03

    params.ActivationFunction_SignedSigmoid_Prob = 1.0;
    params.ActivationFunction_UnsignedSigmoid_Prob = 1.0;
    params.ActivationFunction_Tanh_Prob = 1.0;
    params.ActivationFunction_TanhCubic_Prob = 1.0;
    params.ActivationFunction_SignedStep_Prob = 1.0;
    params.ActivationFunction_UnsignedStep_Prob = 1.0;
    params.ActivationFunction_SignedGauss_Prob = 1.0;
    params.ActivationFunction_UnsignedGauss_Prob = 1.0;
    params.ActivationFunction_Abs_Prob = 1.0;
    params.ActivationFunction_SignedSine_Prob = 1.0;
    params.ActivationFunction_UnsignedSine_Prob = 1.0;
    params.ActivationFunction_Linear_Prob = 1.0;
    params.ActivationFunction_Relu_Prob = 1.0;
    params.ActivationFunction_Softplus_Prob = 1.0;

    #
    # params.ActivationFunction_SignedSigmoid_Prob = 0.0
    # params.ActivationFunction_UnsignedSigmoid_Prob = 1.0
    # params.ActivationFunction_Tanh_Prob = 0.0
    # params.ActivationFunction_TanhCubic_Prob = 0.0
    # params.ActivationFunction_SignedStep_Prob = 0.0
    # params.ActivationFunction_UnsignedStep_Prob = 0.0
    # params.ActivationFunction_SignedGauss_Prob = 0.0
    # params.ActivationFunction_UnsignedGauss_Prob = 1.0
    # params.ActivationFunction_Abs_Prob = 0.0
    # params.ActivationFunction_SignedSine_Prob = 0.0
    # params.ActivationFunction_UnsignedSine_Prob = 1.0
    # params.ActivationFunction_Linear_Prob = 1.0
    # params.ActivationFunction_SignedSigmoid_Prob = 0.0
    # params.ActivationFunction_UnsignedSigmoid_Prob = 1.0
    # params.ActivationFunction_Tanh_Prob = 0.0
    # params.ActivationFunction_SignedStep_Prob = 0.0

    params.AllowLoops = False
    return params

def configureSubstrate():
    inputCoordinateList = []
    for x in range(14):
        for y in range(6):
            inputCoordinateList.append((x,y))

    hiddenCoordinateList = []
    for x in range(14):
        for y in range(6):
            hiddenCoordinateList.append((x,y+6))

    outputCoordinatesList = []
    for x in range(5):
        outputCoordinatesList.append((x,0));

    substrate = NEAT.Substrate(inputCoordinateList,hiddenCoordinateList,outputCoordinatesList)
    substrate.m_allow_input_hidden_links = True
    substrate.m_allow_input_output_links = True #do we really want this true
    substrate.m_allow_hidden_hidden_links = False
    substrate.m_allow_hidden_output_links = True
    substrate.m_allow_output_hidden_links = False
    substrate.m_allow_output_output_links = False
    substrate.m_allow_looped_hidden_links = False
    substrate.m_allow_looped_output_links = False

    substrate.m_hidden_nodes_activation = NEAT.ActivationFunction.UNSIGNED_SIGMOID
    substrate.m_output_nodes_activation = NEAT.ActivationFunction.UNSIGNED_SIGMOID
    # substrate.m_hidden_nodes_activation = NEAT.ActivationFunction.SIGNED_SIGMOID
    # substrate.m_output_nodes_activation = NEAT.ActivationFunction.LINEAR #UNSIGNED_SIGMOID

    # substrate.m_with_distance = True

    # substrate.m_max_weight_and_bias = 8.0
    return substrate

def evaluatePopulationAgainstRandom(pop, numCycles, substrate, symmetry, hyper, depth):
    ''' Evaluates every individual against numCycles * 2 number of random
    players. Each cycle contains 2 games where each player get to go first.
    '''
    randomWinList = []
    for genome in NEAT.GetGenomeList(pop):
        randomWins = 0
        # Playing games against random players
        for j in range(10):
            winner1 = play("Random", genome, substrate, symmetry, printGames, hyper, depth)
            winner2 = play(genome, "Random", substrate, symmetry, printGames, hyper, depth)
            if winner1 == 2:
                randomWins += 1
            elif winner1 == 3:
                randomWins += .5
            if winner2 == 1:
                randomWins += 1
            elif winner2 == 3:
                randomWins += .5
        randomWinList.append(randomWins)



def runOneSim(hyper,printGames,symmetry):
    GLOBAL_DEPTH = 1

    # if (len(sys.argv) < 6):
    #     print("Two command line arguments expected.")
    #     print("output file")
    #     print("0 for no symmetry, 1 for symmetry")
    #     print("0 to silence games, 1 to view games")
    #     print("0 for NEAT, 1 for HyperNEAT")
    #     print("file to store the best individual in")
    #     print("generation number at which the best individual is stored")
    #     return

    output_file = sys.argv[1]
    genome_save_point = sys.argv[2]
    genome_save_generation = int(sys.argv[3])

    params = configureParams()
    substrate = configureSubstrate()
    params.Save(output_file+"params.txt")
    with open(output_file+"data.csv", "a") as f:
        # f.write("\nCommand line parameters\n")
        # f.write("symmetry: " + str(bool(symmetry)) + "\n")
        # f.write("HyperNEAT: " + str(bool(hyper)) + "\n")
        # f.write("Gen | Min | Avg | Max | RunTime\n")
        f.write("Hyper"+str(hyper)+" symmetry"+str(symmetry)+"\n")
    if hyper:
        genome = NEAT.Genome(0, substrate.GetMinCPPNInputs(), 0, substrate.GetMinCPPNOutputs(),
                      False, NEAT.ActivationFunction.UNSIGNED_SIGMOID, NEAT.ActivationFunction.UNSIGNED_SIGMOID,
                      0, params)

    else:
        genome = NEAT.Genome(0, 14 * 6, 0, 1, False, NEAT.ActivationFunction.UNSIGNED_SIGMOID,
                        NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)

    # use current time as the random seed
    pop1 = NEAT.Population(genome, params, True, 1.0, int(time.time()))
    numGens = 20

    for generation in range(numGens):
        begin = time.time()
        gameMatrix = []
        gamesSoFar = []
        for i in range(params.PopulationSize):
            gameMatrix.append([])
            for j in range(params.PopulationSize):
                gameMatrix[i].append(False)
            gamesSoFar.append([0,0,0])

        ### individuals playing each other ###
        for i in range(params.PopulationSize):
            if sum(gamesSoFar[i]) < 10:
                evaluate(i, NEAT.GetGenomeList(pop1), gameMatrix, gamesSoFar, substrate, symmetry, False, GLOBAL_DEPTH)

        ### assign fitnesses based on the game that they played with each other
        for genome in NEAT.GetGenomeList(pop1):
            games = sum(gamesSoFar[i])
            fitness = (gamesSoFar[i][0] + gamesSoFar[i][1] * .5) / (games*1.0)
            genome.SetFitness(fitness)

        stringToWrite = str(generation) + ','
        ### players that go on the leftmost available column ###
        # fitnesses = []
        # for genome in NEAT.GetGenomeList(pop1):
        #     leftWins = 0
        #     for j in range(10):
        #         winner1 = play("Left", genome, substrate, symmetry, printGames, hyper)
        #         winner2 = play(genome, "Left", substrate, symmetry, printGames, hyper)
        #         if winner1 == 2:
        #             leftWins += 1
        #         elif winner1 == 3:
        #             leftWins += .5
        #         if winner2 == 1:
        #             leftWins += 1
        #         elif winner2 == 3:
        #             leftWins += .5
        #     fitnesses.append(leftWins)
        #     genome.SetFitness(leftWins)

        ### players that go in random columns ###
        coFitnesses = []
        randFitnesses = []
        totalFitnesses = []
        for genome in NEAT.GetGenomeList(pop1):
            randomWins = 0
            # Playing games against random players
            for j in range(10):
                winner1 = play("Random", genome, substrate, symmetry, printGames, hyper, GLOBAL_DEPTH)
                winner2 = play(genome, "Random", substrate, symmetry, printGames, hyper, GLOBAL_DEPTH)
                if winner1 == 2:
                    randomWins += 1
                elif winner1 == 3:
                    randomWins += .5
                if winner2 == 1:
                    randomWins += 1
                elif winner2 == 3:
                    randomWins += .5

            # At this point, each genome has a fitness that's been assigned from
            #  playing others in the population. Get it, and alter it.
            coFitness = genome.GetFitness()
            randFitness = randomWins/20.0
            randomWeight = .96**generation

            coFitnesses.append(coFitness)
            randFitnesses.append(randFitness)
            totalFitnesses.append(genome.GetFitness() + (randomWins / 20.0))
            genome.SetFitness(genome.GetFitness()*(1-randomWeight) + (randomWins / 20.0)*randomWeight)

        gc.collect()
        # fitness assignment for every individual is complete. Gather it for
        #  analytics

        pop1.Epoch()
        end = time.time()
        stringToWrite = stringToWrite + "randMin:"+str(min(randFitnesses)) + ', randAvg:' + str(sum(randFitnesses) / len(randFitnesses)) + ', randMax:' + str(max(randFitnesses)) + ', totalMax:' + str(max(totalFitnesses)) + '\n'
        stringToWrite2 = str(sum(randFitnesses) / len(randFitnesses))
        with open(output_file, "a") as f:
            f.write(stringToWrite2)
        print(stringToWrite)

        # at the point where the genomes should be saved, save the whole population
        if (generation == genome_save_generation):
            with open(genome_save_point+str(hyper)+str(symmetry)+".txt", 'w') as f:
                pickle.dump(NEAT.GetGenomeList(pop1), f)

def main():
    for hyper in [0,1]:
        for symmetry in [0,1]:
            for run in range(3):
                print("running hyper"+str(hyper)+" symmetry"+str(symmetry)+" run"+str(run))
                runOneSim(hyper, 0, symmetry)
                gc.collect()
            gc.collect()
        gc.collect()

def test():
    substrate = configureSubstrate()
    params = configureParams()
    with open('genome.txt', 'r') as f:
        mygenome = pickle.load(f)
    play(mygenome, "Human", substrate, False, True, False, GLOBAL_DEPTH)
main()
# test()
