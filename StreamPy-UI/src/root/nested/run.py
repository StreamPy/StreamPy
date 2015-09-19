'''
This module parses the input arguments and extracts the necessary
data structures from it, then calls the appropriate functions to
process it.

'''

import sys
import getpass

from Subgraph import *
from Multiprocessing import *


def dispatch(json_file_name):
    '''
    Looks at input JSON file and determines
    which functions should be called to
    process it.

    Parameters
    ----------
    json_file_name : str
        Path to JSON file to be executed

    Returns
    -------
    None

    '''

    # Convert JSON to my format
    agent_dict_json = make_json(json_file_name)

    # Extract the dictionary from JSON
    with open(agent_dict_json) as data_file:
        json_data = json.load(data_file)

    # Case 1: No groups -> no parallel processing
    if 'groups' not in json_data.keys():
        # First expose nested subgraphs
        agent_dict_json = unwrap_subgraph(agent_dict_json)
        # Then animate it
        make_js(agent_dict_json)

    # Case 2: Has groups -> parallel processing
    else:
        # Sort components into indicated processes
        big_dict = parallel_dict(json_data)
        # Then execute using multiprocessing
        run_parallel(big_dict)


###################################################
# If you're running from an IDE...

# Simple example with parameter arguments
var1 = 'JSON/multiplyparam.json'

# Example of an input JSON file that is already in the
# special agent descriptor dict format
var2 = 'JSON/agent_descriptor.json'

# Simple nested subgraph example
var3 = 'JSON/simplesubgraph.json'

# Graph with 3 nested subgraphs
var4 = 'JSON/doublenested.json'

# Multiprocessing example. Doesn't work yet!!
var5 = 'JSON/simplegroups.json'

# UNCOMMENT the following 3 lines to be prompted
# for a JSON file name at each run

# var = raw_input("Please enter path of JSON: ")
# var = str(var)
# dispatch(var)

# UNCOMMENT the following line to run the same
# file each run, replacing 'var1' with the
# path to the file you want

# dispatch(var1)

###################################################
# If you're running from terminal:
# Usage: navigate into the directory with this file
#        type: python run.py NAME_OF_JSON_FILE
user_os = sys.platform
user_name = getpass.getuser()

if user_os == 'darwin':
    path = '/Users/' + user_name + '/Downloads/'
elif user_os[:3] == 'win':
    path = 'C:/Users/' + user_name + '/Downloads/'
elif 'linux' in user_os:
    path = '/home/' + user_name + '/Downloads/'
else:
    path = ''

var = sys.argv
fullpath = path + var[1]
dispatch(fullpath)
