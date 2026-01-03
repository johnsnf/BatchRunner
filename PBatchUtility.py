import csv 
import numpy as np
from scipy.stats import qmc
import random
import argparse


parser = argparse.ArgumentParser(description="Creates run file for batching python jobs. These run files are generated either by linspace/LHS/constant of specified variable/design space.")
parser.add_argument("--test", type = bool, default = 0, help = "Test flag for proving functionality")
args = parser.parse_args()
testFlag = args.test

def scaledLHS(samplesCount, valRange):
    '''
    scaledLHS - Generates LHS samples based on desired count and specified value range
    
    :param samplesCount: Integer refering to total sampels
    :param valRange: Each row represents a variable, column 0 is the min, column 1 is the max [numpy array]
    '''
    
    varCount = valRange.shape[0]
    engine = qmc.LatinHypercube(d=varCount)
    samples = engine.random(n = samplesCount)
    
    #Scaling each variable 
    for i, r in enumerate(valRange):
        netRange = np.abs(r[1] - r[0])
        samples[:,i] = samples[:,i]*netRange + np.min(r) 
    
    return samples 

# def defaultNameFiles(samples):
#     F = [] 
#     for s in samples:
#         f = "BatchRun" 
#         for data in s:
#             f += f"_{data:.02f}" 
#         F.append(f)
#     return F 

def defaultNameFiles(samples):
    
    F = [] 
    rowCount = samples.shape[0] 
    randVals = [] 
    for _ in range(rowCount*5):
        randVals.append(random.randint(10000,99999))
    
    randVals = np.array(randVals)
    randVals = np.unique(randVals)
    
    for i in range(rowCount):
        F.append("BatchRun_"+str(randVals[i])) 

    return F 


def joinLists(samples,names,headers):
    '''
    Compiles all data into a list that is suitable for writing to csv file 
    
    :param samples: numpy array containing sample information for each run 
    :param names: List of strings (names) for each run case
    :param headers: Variable names 
    '''
    sampCount = samples.shape[0]
    samples = samples.tolist() 
    for i in range(sampCount):
        samples[i] = [names[i]] + samples[i] 

    
    outData = [headers] + samples 
    
    return outData


def scaledLIN(NumSamples, valRange_LIN, sampleCount):
    samples = []
    for i in range(valRange_LIN.shape[0]):
        start = np.min(valRange_LIN[i,:])
        end = np.max(valRange_LIN[i,:])
        samples.append(np.linspace(start,end,sampleCount[i]).reshape((sampleCount[i],)))

    return samples 

def joinSamples(samplesLHS, samplesLIN, valRange_CON, valSelect, meshgrid = True):
    
    #Building mesh grid:
    LHSIndex = np.arange(0,samplesLHS.shape[0],1, dtype = np.int64)
    if samplesLHS.shape[1] >= 1:
        LinVars = [LHSIndex]
    else:
        LinVars = []
    # for i in range(samplesLIN.shape[1]):
    #     LinVars.append(samplesLIN[:,i]) 
    for i in range(len(samplesLIN)):
        LinVars.append(samplesLIN[i])
    
    MeshedGrid = list(np.meshgrid(*LinVars))
    
    meshShape = MeshedGrid[0].shape
    eleCount = 1
    for dim in meshShape:
        eleCount *= dim 
    
    if len(MeshedGrid) > 1:
        
        #Extracting index portion of MeshedGrid
        if samplesLHS.shape[1] >= 1:
            LHSIndex = MeshedGrid[0].reshape((eleCount,1))
            MeshedGrid.pop(0) #dropping it from main list 
        
        if not isinstance(MeshedGrid,list):
            MeshedGrid = [MeshedGrid]     
        
        #Rebuilding samplesLIN:
        for i in range(len(MeshedGrid)):
            MeshedGrid[i] = MeshedGrid[i].reshape((eleCount,1))
        samplesLIN_final = np.concatenate(MeshedGrid,axis = 1) #Rejoining into full matrix 
        
        #Rebuilding samplesLHS with new index set:
        samplesLHS_final = np.zeros((eleCount,samplesLHS.shape[1])) 
        for i in range(samplesLHS.shape[1]):
            samplesLHS_final[:,i] = samplesLHS[LHSIndex,i].reshape((eleCount,))
    else:
        samplesLHS_final = samplesLHS
        
        if isinstance(samplesLIN,list):
            # if len(samplesLIN) > 1:
            #     samplesLIN_final = samplesLIN[0]
            #     samplesLIN_final = samplesLIN_final.reshape((samplesLIN_final.shape[0],1))
            # else:
            #     samplesLIN_final = samplesLIN[0]
            
            print(samplesLIN)
            
            if len(samplesLIN) >= 1:
                samplesLIN_final = samplesLIN[0]
                samplesLIN_final = samplesLIN_final.reshape((samplesLIN_final.shape[0],1))
            else:
                samplesLIN_final = []
        else:
            samplesLIN_final = samplesLIN
        
        # print(type(samplesLIN_final))
        # print(samplesLIN_final.shape)
    
    #Stitching together all sample matrix sets  
    i_LHS = 0 
    i_LIN = 0 
    i_CON = 0 
    samples = np.zeros((eleCount,len(valSelect)))
    for i in range(len(valSelect)):
        if valSelect[i] == 'LHS':
            samples[:,i] = samplesLHS_final[:,i_LHS]
            i_LHS += 1
        elif valSelect[i] == 'LIN':
            samples[:,i] = samplesLIN_final[:,i_LIN]
            i_LIN += 1
        elif valSelect[i] == 'CON':
            samples[:,i] = np.ones((eleCount,)) * valRange_CON[i_CON]
            i_CON += 1
    
    samples = np.unique(samples,axis = 0)

    return samples


def run():
    print("Generating a batch run file leveraging LHS sampling...")
    NumVar = int(input("How many variables are there?\n>> "))
    NumSamples = int(input("How many samples would you like (LHS)?\n>> "))
    print("Iterating through each variable...") 
    Headers = ["Variable Names"] 
    valRange = np.zeros((NumVar,2)) 
    valSelect = []
    sampleCount = []
    for i in range(NumVar):
        print(f"Processing variable {i}")
        valSelectStrat = str(input("\tData selection strategy (LHS - Latin Hypercube, LIN - linspace, CON - constant)\n>>"))
        Name = str(input("\tWhat would you like to call the variable? \n>> ")) 
        
        if valSelectStrat == 'LHS':
            Lower = float(input("\tWhat is the lower bounds of this variable\n>> "))
            Upper = float(input("\tWhat is the upper bounds of this variable\n>> "))
            valRange[i,0] = Lower 
            valRange[i,1] = Upper 
        elif valSelectStrat == 'LIN':
            #Need to add this section otherwise LHS and LIN are the same. Need to seperate
            Lower = float(input("\tWhat is the lower bounds of this variable\n>> "))
            Upper = float(input("\tWhat is the upper bounds of this variable\n>> "))
            sampleCount.append(int(input("How many increments for this variable\n>>")))
            valRange[i,0] = Lower 
            valRange[i,1] = Upper 
        else:
            Lower = float(input("\tWhat is the constant value\n>> "))
            valRange[i,0] = Lower 
        
        Headers.append(Name) 
        valSelect.append(valSelectStrat)
    
    if len(valSelect) == 1 and valSelect[0] == 'CON':
        raise ValueError("Cannot create a batch script for a single constant value run.")
    
    #Extracting entries for LHS
    boolMask = np.array([b == 'LHS' for b in valSelect],dtype = np.bool)
    valRange_LHS = valRange[boolMask,:]
    
    #Extracting entries for LIN
    boolMask = np.array([b == 'LIN' for b in valSelect],dtype = np.bool)
    valRange_LIN = valRange[boolMask,:]
    
    #Extracting entries for CON
    boolMask = np.array([b == 'CON' for b in valSelect],dtype = np.bool)
    valRange_CON = valRange[boolMask,0]
    
    print("Generating batch cases...") 
    
    samplesLHS = scaledLHS(NumSamples, valRange_LHS) #LHS cases 
    samplesLIN = scaledLIN(NumSamples, valRange_LIN, sampleCount) #LIN cases 
    
    samples = joinSamples(samplesLHS, samplesLIN, valRange_CON, valSelect)
    
    names = defaultNameFiles(samples) 
    
    outData = joinLists(samples,names,Headers)
    print("-"*40)
    print("Finished generating data!")
    
    #Writing CSV
    fileName = str(input("What would you like to name the output batch file?\n>> "))
    
    
    if not testFlag:
        with open(fileName, "wt") as fp:
            writer = csv.writer(fp, delimiter=",")
            writer.writerows(outData)
    else:
        print(f'Samples shape: *{samples.shape}*')
    
    
    return samples
    
    

if __name__ == "__main__":
    a = run()
    # print(a)
    # print(a.shape)

    
    
    
#FUTURE TODO:
# -Have some kind of design space visualization tool (how well are the samples representing the space?) 