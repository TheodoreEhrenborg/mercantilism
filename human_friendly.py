'''This module manages the interaction with the user and
sends the user's commands to a file read by the artificial
primary investigator.'''
def main():
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
                  know how API thinks. Be careful.'''
  error = '''Sorry, I did not recognize that command. Are you sure you typed it correctly?'''
  quitting = '''I told the Artificial Primary Investigator (API) to quit. I'll tell you when it has quit.'''
  done_quitting = '''The API has quit. I have quit too.'''
  
  
