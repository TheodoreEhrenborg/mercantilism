"""This module manages the interaction with the user and
sends the user's commands to a file read by the artificial
primary investigator."""
normal = """The computer is currently running Theodore's AP Research project
              between midnight and 2:30 pm. Type 'quit' to safely quit the program.
              Type 'options' to get more options."""
options = """Type 'quit' to safely quit the program.
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
              Type 'max_trials value' to tell the API the maximum number of trials it can run where one
                  algorithm is testing for being ES against another. max_trials overrides
                  any consideration of confidence.
              Type 'min_trials value' to tell the API the minimum number of trials it must run where one
                  algorithm is testing for being ES against another. min_trials overrides
                  any consideration of confidence.
              Type 'max_time value' to tell the API the maximum amount of time (seconds) it can run where one
                  algorithm is testing for being ES against another. max_time overrides
                  any consideration of confidence or trials.
              Type 'min_time value' to tell the API the minimum amount of time (seconds) it must run where one
                  algorithm is testing for being ES against another. min_time overrides
                  any consideration of confidence or trials.
              Type 'redo_confidence' to tell API that it needs to redo all the confidences, but the trials
                  can be left alone. (This is a good option after you have fixed a bug in bayesian.py.)
              Type 'get_results' to tell API to make a short version of all its confidences, which will be
                  saved in the Results folder."""
error = (
    """Sorry, I did not recognize that command. Are you sure you typed it correctly?"""
)
starting = """Starting the Artificial Primary Investigator (API)"""
quitting = """I told the Artificial Primary Investigator (API) to quit. It will quit in a few minutes."""
# done_quitting = '''I have quit.'''
work_during_day = """WARNING: The API is set up to always work, which could affect the results
                         Only proceed if you are testing the program, and please reset everything
                         afterwards."""


def main(daytime_run=False):
    import time
    import api
    import os

    try:
        f = open("Results/human_friendly_to_api.txt", "a")
        f.close()
    except IOError:
        os.system("mkdir Results")
    try:
        f = open("Results/Readable/testing.txt", "a")
        f.close()
    except IOError:
        os.system("mkdir Results/Readable")
    print(time.asctime() + ": " + starting)
    if daytime_run:
        print(time.asctime() + ": " + work_during_day)
    #    t1 = multiprocessing.Process( target = api.main, args = [daytime_run] )
    #    t1 = threading.Thread( target = api.main, args = [daytime_run] )
    #    t1.start()
    #    #Starts the API here, using multi-processing
    #    #so human_friendly will be free to continue
    if not daytime_run:
        os.system("python -c 'import api;api.main()' &")
    else:
        os.system("python -c 'import api;api.main(True)' &")
    response = ""
    while True:
        print(time.asctime() + ": " + normal)
        response_OK = False
        while not response_OK:
            response = input().lower().rstrip().lstrip()
            if formatted(response):
                response_OK = True
            else:
                print(time.asctime() + ": " + error)
        # Do something based on the response
        if response == "options":
            print(time.asctime() + ": " + options)
        elif response == "quit":
            break
        else:
            # Contact API with the message
            f = open("Results/human_friendly_to_api.txt", "a")
            f.write(str(time.time()) + ":" + response + "\n")
            f.close()
    # Contact API and tell it to quit
    f = open("Results/human_friendly_to_api.txt", "a")
    f.write(str(time.time()) + ":" + response + "\n")
    f.close()
    print(time.asctime() + ": " + quitting)


#    #Wait until the API quits
#    t1.join()
#    print( time.asctime() + ": " + done_quitting )


def formatted(command):
    """Detects whether command is acceptable."""
    if "official" in command:
        return False
    new = command.split()
    if len(new) == 1:
        return new[0] in [
            "quit",
            "options",
            "adjourn",
            "reload",
            "redo_confidence",
            "get_results",
        ]
    elif len(new) == 3:
        return new[0] in ["reset"]
    elif len(new) == 2:
        return new[0] in [
            "confidence",
            "min_trials",
            "max_trials",
            "min_time",
            "max_time",
        ]
    else:
        return False
