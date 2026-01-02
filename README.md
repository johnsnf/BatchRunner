BatchRunner is a library designed to batch run python scripts with ease of implementation.

This library requires only a script function call "main" that returns data in the form of a
python dictionary. Data is then saved as a numpy file (.npz) including both the input 
parameters and the output results. IMPORTANT NOTE: variable data is passed as kwargs not args.

PBatch.py is the main batch runner script, PBatchUtility.py is a script for building the 
case sets.

PBatch use:
	python3 PBatch.py <runScript.py> <batchCases.csv>
		 OPT: --parallel <Number of workers in parallel run>
		--skipTrial <0 or 1 - if 1, it skips the trial run otherwise executed (0) to test proper functionality before dispatching to multiprocessing step>

Notes on runScript.py:
	-Requires a "main(**kwargs)" function that returns a dictionary of any data 
		interested in saving
	-Example:
		def main(a,b,c):
			d = a + b
			e = b + c 
			return {
				'd':d,
				'e':e,
				}

Notes on batchCases.csv:
	-Comma delimited 
	-Variable names MUST match the kwargs from "main(**kwargs)" above.
	-Example:
		FileName, a, b, c
		MyFile1, 1,2,3
		MyFile2, 2,3,4
		MyFile3, 4,5,6 
	-Other than the first row, each row reflects a single batch case to be run 
	-See PBatchUtility.py for automatically building this file 

Notes on PBatchUtility.py:
	-Run the script and follow instructions
	-Note, values are selected by one of the following:
		1) Latin Hypercube Sampling (LHS)
		2) Linspace
		3) Constant
	-Ranges are specified, then total run cases are prescribed. All cases selected
		at random 
	-For runs containing both (1) and (2), all permutations between sets are considered
		e.g. if linspace generates 10 elements, each of those 10 elements will have
			a run including all selections of the LHS space. This permeates 
			creating a very massive run.


