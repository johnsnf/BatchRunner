import csv 
import numpy as np
from scipy.stats import qmc

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

def defaultNameFiles(samples):
    F = [] 
    for s in samples:
        f = "BatchRun" 
        for data in s:
            f += f"_{data:.02f}" 
        F.append(f)
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


def run():
    print("Generating a batch run file leveraging LHS sampling...")
    NumVar = int(input("How many variables are there?\n>> "))
    NumSamples = int(input("How many samples would you like?\n>> "))
    print("Iterating through each variable...") 
    Headers = ["Variable Names"] 
    valRange = np.zeros((NumVar,2)) 
    for i in range(NumVar):
        print(f"Processing variable {i}")
        Name = str(input("What would you like to call the variable? \n>> ")) 
        Lower = float(input("What is the lower bounds of this variable\n>> "))
        Upper = float(input("What is the upper bounds of this variable\n>> "))
        
        valRange[i,0] = Lower 
        valRange[i,1] = Upper 
        Headers.append(Name) 
    
    print("Generating batch cases...") 
    samples = scaledLHS(NumSamples, valRange) 
    names = defaultNameFiles(samples) 
    
    outData = joinLists(samples,names,Headers)
    print("-"*40)
    print("Finished generating data!")
    
    #Writing CSV
    fileName = str(input("What would you like to name the output batch file?\n>> "))
    with open(fileName, "wt") as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(outData)
    
    

if __name__ == "__main__":
    run()

    