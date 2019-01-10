'''This module manages the interaction with the user and
sends the user's commands to a file read by the artificial
primary investigator.'''
import time, api
normal = '''The computer is currently running Theodore's AP Research project
              between midnight and 2:30 pm. Type 'quit' to safely quit the program.
              Type 'options' to get more options.'''
options = '''Type 'quit' to safely quit the program.
              Type 'options' to get this options message.
              Type 'adjourn' to get the program to cease operations until midnight.
              Type 'reload' to tell the Artificial Primary Investigator (API) that conditions may have changed.
              Type 'reset algorithm_name1 algorithm_name2' to get the API to reset all the trials where 
                  algorithm_name1 was tested to see if it is evolutionary stable (ES) against algorithm_name2.
              Type 'reset algorithm_name all' to get the API to reset all the trials where every algorithm was
                  tested to see if it is ES against algorithm_name.
              Type 'reset all algorithm_name' to get the API to reset all the trials where algorithm_name was
                  tested to see if it is ES against all other algorithms.
              Type 'reset all all' to get the API to reset ALL the trials. This is reversible, but you have to 
                  know how API thinks. Be careful.
              Type 'confidence value' to tell the API to reload and conduct trials aiming for confidence value.
                  You can set value to be anywhere in (0,1), but you probably want to choose 0.99 or 0.95, which 
                  means that the API tries to become 99% sure that a strategy is (or isn't) ES against another.
              Type 'maximum value' to tell the API the maximum number of trials it can run where one 
                  algorithm is testing for being ES against another. max_trials overrides 
                  any consideration of confidence.
              Type 'minumum value' to tell the API the minimum number of trials it must run where one
                  algorithm is testing for being ES against another. min_trials overrides 
                  any consideration of confidence.'''
error = '''Sorry, I did not recognize that command. Are you sure you typed it correctly?'''
starting = '''Starting the Artificial Primary Investigator (API)'''
quitting = '''I told the Artificial Primary Investigator (API) to quit. I'll tell you when it has quit.'''
done_quitting = '''The API has quit. I have quit too.'''
def main():
    print time.asctime() + starting
    response = ""
    while response != "quit":
        pass
    print time.asctime() + quitting
    #Contact API and tell it to quit
    print time.asctime() + done_quitting
  
