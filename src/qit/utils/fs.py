import os

def makedir_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
