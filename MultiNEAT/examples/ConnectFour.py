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

from ConnectFour import MyConnectFour

####### added code

params = NEAT.Parameters()
params.PopulationSize = 100
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
pop = NEAT.Population(genome, params, True, 1.0, 0) # the 0 is the RNG seed

'''
coevolution may be possible. in order to evaluate an individual.
To evaluate an individual, pass in the population that it will match against.

- Consider some kind of sampling
- Consider both cases: p1 goes first, p1 goes second
'''
def evaluate(genome, population):
    # build the NN for the individual that we are evaluating.
    player1Net = NEAT.NeuralNetwork()
    genome.BuildPhenotype(player1Net)

    p1FirstWins = 0
    p1SecondWins = 0
    p1FirstTies = 0
    p1SecondTies = 0


    # For now, play two rounds with each of the individuals in the population
    popGenomeList = NEAT.GetGenomeList(population)
    for p2Genome in popGenomeList:
        # build opponent NN
        player2Net = NEAT.NeuralNetwork(p2Genome)
        p2Genome.BuildPhenotype(player2Net)

        winner = 0
        # curPlayer = 1
        while (true):
            # make move as p1
            # see if someone won, if so, break
            # make move as p2
            # see if someone won, if so, break
        # if p1 won the above round, p1FirstWins += 1
        # if tied, p1FirstTies += 1

        while (true):
            # make move as p2
            # see if someone won, if so, break
            # make move as p2
            # see if someone won, if so, break
        # if p1 won the above round, p1SecondWins += 1
        # if tied, p1SecondTies += 1


    # let's input just one pattern to the net, activate it once and get the output
    net.Input( [ 1.0, 0.0, 1.0 ] )
    net.Activate()
    output = net.Output()

    # the output can be used as any other Python iterable. For the purposes of the tutorial,
    # we will consider the fitness of the individual to be the neural network that outputs constantly
    # 0.0 from the first output (the second output is ignored)

    fitness = SOME FITNESS MEASURE FOR THE FIRST GENOME dependent on
    return fitness

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
