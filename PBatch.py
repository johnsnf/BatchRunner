import argparse
import csv 
import importlib.util
import numpy as np 
import os 
import sys
from pathlib import Path
from tqdm.contrib.concurrent import process_map  # or thread_map

'''
PBatch.py

All arguments required by the main() function call should be included in the batch script.
The main() function call should return data as a dictionary. Failure to do so will result in an error.
'''

# Print welcome script ... mention assumptions with data format, all input data is assumed to be floats, assumed output data as dictionarys

def load_main_from_path(script_path: str):
    script_path = Path(script_path).resolve()

    module_name = script_path.stem  # e.g. "myscript"
    spec = importlib.util.spec_from_file_location(module_name, script_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # important for multiprocessing
    spec.loader.exec_module(module)

    if not hasattr(module, "main"):
        raise AttributeError(f"{script_path} has no main() function")

    return module.main

# Creating parser
parser = argparse.ArgumentParser(description="Batch runs python python script employing multip processing and saving output data as numpy file")

# Adding arguments 
parser.add_argument("runScript", type = str, help = "Python script containing 'main' function to be executed") 
parser.add_argument("batchCases", type = str, help = "Text file with each row containing a single run. Column 1 is the batch name, column2 and on are input variables. File presented as a .csv")
parser.add_argument("--parallel", type = int, default = 2, help = "Number of parallel batches to run")
parser.add_argument("--skipTrial", type = int, default = 0, help = "0 - Run check before spooling up multiprocessing step to ensure function runs and returns data as expected. \nSelecting a value of '1' will bypass this check")

# Parsing arguments 
args = parser.parse_args()

# Extracting arguments
# runScript = args.runScript.replace(".py","") #Dont need the .py portion if it exists
runScript = args.runScript
batchCases = args.batchCases 
NUMPAR = args.parallel 
skipTrial = bool(args.skipTrial) #boolean indicating whether or not to skip trial run 

# Preparing to batch...
if __name__ == '__main__':
    print("Loading in files preparing to batch...") 
try: 
    main = load_main_from_path(runScript)
    if __name__ == '__main__':
        print("Function 'main' loaded from runScript sucessfully.")
except:
    raise Exception(f"Issue loading 'main' function from {runScript}.")
try: 
    with open(batchCases) as fp:
        reader = csv.reader(fp, delimiter = ",", quotechar = '"') 
        data = [row for row in reader]
        headerInfo = data[0][1:] #First row, skipping first column since that is file names
        NUMRUN = len(data) - 1 
except:
    raise Exception(f"Issue with reading in batchCases.")


    
# --------------------------------------------------------------------------------
# Creating a file directory to save run data to 

        # 1) Checking if '/run' exists
        # 1a) If it does, execute while loop adding integer to end until it isnt found (e.g. '/run1')
        # 2) Creating appropriate directory based on (1)
        
def makePath():
    if __name__ == '__main__':
        runPath = os.path.join(os.getcwd(),'run')
        if not os.path.isdir(runPath):
            os.mkdir(runPath)
        else:
            i = 0
            while os.path.isdir(runPath):
                runPath = os.path.join(os.getcwd(), 'run'+ str(i))
                i += 1 
            os.mkdir(runPath)
    else:
        runPath = os.path.join(os.getcwd(),'run0')
        if not os.path.isdir(runPath):
            runPath = os.path.join(os.getcwd(),'run')
        else:
            i = -1
            while os.path.isdir(runPath):
                i += 1       
                runPath = os.path.join(os.getcwd(), 'run'+ str(i))
            runPath = os.path.join(os.getcwd(), 'run'+ str(i-1))
    return runPath

runPath = makePath()
    
def runCase(runIndex):
    
    parameters = data[runIndex]
    fileName = parameters[0] 
    parameters.pop(0)
    
    pNew = [float(p) for p in parameters] #Casting all varibales to floats 
    
    #Converting data into dictionary so it is passed to function as KWARGS
    runParam = {}
    for i in range(len(pNew)):
        runParam[headerInfo[i]] = pNew[i]  #These can be treated as kwargs

    # returnData = main(*pNew) #Handing all data over 
    returnData = main(**runParam)
    if not isinstance(returnData,dict):
        raise TypeError("Expected function to return dictionary")
    

        
    mergedDictionary = runParam | returnData 
    
    fileName += '.npz' 
    filePath = os.path.join(runPath,fileName)
    
    np.savez(filePath, **mergedDictionary)
    
    #NOTE: to load file, run the following:
    # a = np.load(fileName)
    # a['<keyNameHere>'] -> returns data associated with that dictionary key



if __name__ == '__main__':
    #Running check case 
    if not skipTrial:
        print('Running check case...')
        runCase(1) 
        print('Run completed successfully') 

    # Parsing out tasks 
    N_WORKERS = os.cpu_count()
    if (N_WORKERS - 1) < NUMPAR:
        print(f'[INFO] User requested {NUMPAR} parallel tasks, however machine only has {N_WORKERS - 1} available. Updating accordingly')
        NUMPAR = N_WORKERS - 1
    RUNS_PER_WORKER = NUMRUN // NUMPAR
    
    
    if not skipTrial:
        r = process_map(runCase, range(2, NUMRUN), max_workers=NUMPAR)
    else:
        r = process_map(runCase, range(1, NUMRUN), max_workers=NUMPAR)






#Input definitions:
# 1) python script with function (main) for batch running 
# 2) Run info (row = run, col1 = saveName, col2 and on are run parameters)
# OPT) -parallel N where N is the number of parallel processes to run 




#PBatch utility - use LHS to generate runs?
# Push to github




#What to save:
# - Anything returned from execution of main() 
# - Input run parameters 







# import multiprocessing
# import os

# def print_info(title):
#     print(f"{title}")
#     print(f"module name: {__name__}")
#     print(f"parent process id: {os.getppid()}")
#     print(f"process id: {os.getpid()}\n")

# def my_function(name):
#     print_info('function f')
#     print(f"Hello, {name}!")

# if __name__ == '__main__':
#     print_info('main line')
#     p = multiprocessing.Process(target=my_function, args=('Bob',))
#     p.start()
#     p.join()
#     print("Main process finished execution.")