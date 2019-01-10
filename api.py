'''This module contains the Artificial Primary Investigator
(API). It only run programs at night to keep CPU speed constant.
It keeps the main log and decides which algorithms to test 
against each other.'''
previous_command_time = 0
def get_time(line):
    '''Returns the number before the first ':' '''
    i = line.index(':')
    return float(line[0:i])
def get_command(line):
    '''Returns the string after the first ':' '''
    i = line.index(':')
    return line[i+1:]
def get_new_commands():
    ''' Looks in the appropriate file and returns a list
    of the new commands from human_friendly '''
    f = open("Results/human_friendly_to_api.txt", "r")
    lines = f.readlines()
    f.close()
    result = []
    for line in lines:
        t = get_time( line )
        if t > previous_command_time:
            result.append( get_command( line ) )
            previous_command_time = t
    return result
def execute_commands():
    commands = get_new_commands()
    f = open("api.log","a")
    for i in commands:
        f.write( time.asctime() + ": " + "Got command \'" + i + "\'" )
    
