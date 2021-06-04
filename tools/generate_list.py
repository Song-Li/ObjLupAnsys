# this tool is used to generate a list of input files of the folder
import sys
import os

def generate_list(dir_path):
    """
    list the folders and return a list 
    """
    dir_list = [os.path.join(dir_path, i) for i in os.listdir(dir_path)]
    # all the package should be folders
    res = []
    for d in dir_list:
        if os.path.isdir(d):
            res.append(os.path.abspath(d))
    return res

input_dir = sys.argv[1]
generated_list = generate_list(input_dir)
with open("result.list", 'w') as fp:
    fp.write('\n'.join(generated_list))