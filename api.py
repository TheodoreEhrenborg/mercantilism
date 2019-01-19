'''This module contains the Artificial Primary Investigator
(API). It only run programs at night to keep CPU speed constant.
It keeps the main log and decides which algorithms to test 
against each other.'''
def main(daytime_run = False):
    should_run = True
    while should_run:
        the_api = API()
        should_run = the_api.run(daytime_run)
class API:
    def __init__(self):
        pass
    def get_time(self,line):
        '''Returns the number before the first ':' '''
        i = line.index(':')
        return float(line[0:i])
    def get_command(self,line):
        '''Returns the string after the first ':' and before the newline'''
        i = line.index(':')
        return line[i+1:-1]
    def get_new_commands(self):
        ''' Looks in the appropriate file and returns a list
        of the new commands from human_friendly '''
        try:
            f = open("Results/human_friendly_to_api.txt", "r")
            lines = f.readlines()
            f.close()
        except IOError:
            lines = []
        result = []
        for line in lines:
            t = self.get_time( line )
            if t > self.previous_command_time:
                result.append( self.get_command( line ) )
                previous_command_time = t
        return result
    def execute_commands(self):
        '''Looks for commands and executes them -- puts them on the log.
        If a command is quit, adjourn, or reload,
        this method executes the other commands first, and
        then ends. The caller has to deal with quit, adjourn,
        or reload.'''
        import time
        self.should_adjourn = False
        commands = self.get_new_commands()
        f = open("Results/api.log","a")
        highest_priority = None
        if time.localtime()[3] >= 14 and time.localtime()[4] >= 30 and not self.daytime_run:
            self.should_adjourn = True
        for i in commands:
            f.write( time.asctime() + ": " + "Got command \'" + i + "\'" + "\n" )
            if i == 'quit':
                self.should_quit = True
            elif i == 'adjourn':
                self.should_adjourn = True
            elif i == 'reload':
                self.should_reload = True
            elif 'reset' in i:
                f.write( time.asctime() + ": Official R" + i[1:] + "\n" ) 
                self.should_reload = True
            elif 'confidence' in i and 'current' not in i:
                f.write( time.asctime() + ": Official C" + i[1:] + "\n" )
                self.should_reload = True
            elif 'max_trials' in i:
                f.write( time.asctime() + ": Official M" + i[1:] + "\n" )
                self.should_reload = True
            elif 'min_trials' in i:
                f.write( time.asctime() + ": Official M" + i[1:] + "\n" )
                self.should_reload = True
            elif 'max_time' in i:
                f.write( time.asctime() + ": Official M" + i[1:] + "\n" )
                self.should_reload = True
            elif 'min_time' in i:
                f.write( time.asctime() + ": Official M" + i[1:] + "\n" )
                self.should_reload = True
            else:
                f.write( time.asctime() + ": " + "Could not understand command!" + "\n" )
        if self.should_reload:
            self.should_quit = True
        f.close()
    def run(self,daytime_run = False):
        #I need a way to run this during daytime.***
        import os,time
        self.NUM_PLAYERS = 5
        self.TOKENS = range(1, 15+1)
        self.previous_command_time = time.time()
        self.should_quit = False
        self.should_adjourn = False
        self.should_reload = False
        self.confidence = 0.99
        self.max_time = 300 * 100
        self.min_time = 30
        self.max_trials = 100
        self.min_trials = 5
        self.DEFAULT = 0.5
        self.sleep_time = 300
        self.daytime_run = daytime_run
        if self.daytime_run:
            self.sleep_time = 3
#        print self.sleep_time
        try:
            f = open("Results/api.log","r")
        except IOError:
#            os.system("mkdir Results") #human_friendly already does this
            f = open("Results/api.log","w")
            f.close()
        else:
            l = f.readlines()
            f.close()
            if len(l) > 0:
                if "Official: Quitting" not in l[ len(l) - 1 ]:
                    raise Exception("It seems that the previous session of API did not quit!")       
        self.execute_commands()
#        self.should_quit = True
        if ( not self.should_quit ) and ( not self.should_adjourn ):
            #Read the log and update the algorithm list and priorities
            self.use_log()
        while not self.should_quit:
            self.execute_commands()
            if ( not self.should_quit ) and ( not self.should_adjourn ) and (not self.check_for_processes() ) :
                #Choose a comparison and do it. Repeat. Check for commands every 5 min
                self.do_comparisons()
            if  ( not self.should_quit ) and ( self.should_adjourn  or self.check_for_processes() ):
                self.adjourn()
        self.execute_commands()
        f = open("Results/api.log","a")
        f.write( time.asctime() + ": " + "Official: Quitting\n" )
        f.close()
        return self.should_reload
    def adjourn(self):
        import time
        f = open("Results/api.log","a")
        f.write( time.asctime() + ": " + "Adjourning" + "\n" )
        f.close()
        while ( not self.should_quit ) and ( self.should_adjourn  or self.check_for_processes() ):
#            print self.sleep_time
            time.sleep( self.sleep_time )
            self.execute_commands()
    def check_for_processes(self):
        '''Checks whether a CPU-intensive process is running.'''
        import os
        if self.daytime_run:
            return False #Ignore any processes
        os.system("top -stats command -l 1 > Results/top-output.txt")#Write the activity monitor to a file    
        f=open("Results/top-output.txt","r")
        process_active = False
        for line in f:
            if ('firefox' in line) or ('Google Chrome' in line) or ('Safari' in line and 'SafariCloudHisto' not in line and 'com.apple.Safari' not in line and 'SafariBook' not in line) or ('mprime' in line) or ('Mathematica' in line):
                process_active = True
                break	       	 
        f.close()
#        if not process_active:
#            os.system("rm -f top-output.txt")
        return process_active
    def use_log(self):
        import time, algorithms,inspect
        reload(algorithms)
        list_algorithms = inspect.getmembers( algorithms, inspect.ismethod)
        print list_algorithms
        self.should_quit = True
        #***Make sure we can only get algorithms without aux_ in __name__
        f = open("Results/api.log","r")
        lines = f.readlines()
        f.close()
        lines.reverse()
        for line in lines:
            if "Official: Confidence: " in line:
                self.confidence = float( line.partition("Official: Confidence: ")[2] )
                break
        for line in lines:
            if "Official: Min_time: " in line:
                self.confidence = int( line.partition("Official: Min_time: ")[2] )
                break
        for line in lines:
            if "Official: Max_time: " in line:
                self.confidence = int( line.partition("Official: Max_time: ")[2] )
                break
        for line in lines:
            if "Official: Min_trials: " in line:
                self.confidence = int( line.partition("Official: Min_trials: ")[2] )
                break
        for line in lines:
            if "Official: Max_trials: " in line:
                self.confidence = int( line.partition("Official: Max_trials: ")[2] )
                break
        self.comparisons = {}
        for a in list_algorithms:
            for b in list_algorithms:
                current_confidence = self.DEFAULT
                key = "Official: Current Confidence: " + str(a) + " " + str(b) + " "
                found = False
                for line in lines:
                    if "Official: Reset " + str(a) + " " + str(b) in line:
                        break
                    if "Official: Reset " + str(a) + " " + "all" in line:
                        break
                    if "Official: Reset " + "all" + " " + str(b) in line:
                        break
                    if "Official: Reset " + "all" + " " + "all" in line:
                        break
                    if key in line:
                        current_confidence = float( line.partition(key)[2] )
                        found = True
                        break
                self.comparisons[ (a,b) ] = (current_confidence, 0, 0)#(confidence, num_trials, total_time) 
                if not found:
                    f = open("Results/api.log","a")
                    f.write( time.asctime() + ": " + key + str(current_confidence) + "\n" )
                    f.close()
    def do_comparisons(self):
        '''Choose a comparison and do it. Repeat. Check for commands every 5 min'''
        import time, copy
        most_recent_check = time.time()
        if len(self.comparisons) == 0:
            f = open("Results/api.log","a")
            f.write( time.asctime() + ": Uh-oh. There are no comparisons to make.\n" )
            f.close()
            return
        while (not self.should_quit) and (not self.should_adjourn) and ( not self.check_for_processes() ):
            closest = 0
            for x in self.comparisons.values():
                if abs( x[0] - 0.5) < abs(closest - 0.5):
                    closest = x[0]
            for current_pair in self.comparisons.keys():
                if self.comparisons[current_pair][0] == closest:
                    break
            #Now that we have a current_pair, we check the probability
            fixed, invader = current_pair
            self.check_probability(current_pair)
            algorithm_list = []
            for x in range(self.NUM_PLAYERS-1):
                algorithm_list.append( fixed )
            algorithm_list.append( invader )
            algorithm_tuple = tuple( algorithm_list )
            games = []
            keep_going = True
            while not should_stop:
                g = Game( copy.copy(algorithm_tuple), copy.copy(self.TOKENS) )
                games.append( g )
                if time.time() - most_recent_check > 300:
                    processes_running = self.check_for_processes()
                    if not processes_running:
                        for g in games:
                            g.write()
                    games = []
                    should_stop = processes_running
                    if processes_running:
                        f = open("Results/api.log","a")
                        f.write( time.asctime() + ": " + "Other CPU-intensive Process Detected\n" )
                        f.close()       
                    self.execute_commands()
                    should_stop = should_stop and self.should_quit and self.should_adjourn
                    self.check_probability( current_pair )
                    should_stop = should_stop and self.experimental_conditions(current_pair)
    def experimental_conditions(self, current_pair):
        current_confidence, all_game_trials, all_game_time  = self.comparisons[current_pair]
        if all_game_time < self.min_time:
            return True
        if all_game_time > self.max_time:
            return False
        if all_game_trials < self.min_trials:
            return True
        if all_game_trials > self.max_trials:
            return False
        return 1 - self.confidence < current_confidence and current_confidence < self.confidence
    def check_probablility(self, algorithm_tuple):
        import time, bayesian
        f = open("Results/api.log","r")
        lines = f.readlines()
        f.close()
        lines = lines.reverse()
        a, b = algorithm_tuple
        current_confidence = self.DEFAULT
        to_write = "Official: Current Confidence: " + str(a) + " " + str(b) + " "
        key = "Official: Game where " + str(a) + " is invaded by " + str(b) + "."
        found = False
        all_game_results = []
        for x in range(NUM_PLAYERS + 1):
            all_game_results.append(0)
        all_game_trials = 0
        all_game_time = 0
        for line in lines:
            if "Official: Reset " + str(a) + " " + str(b) in line:
                break
            if "Official: Reset " + str(a) + " " + "all" in line:
                break
            if "Official: Reset " + "all" + " " + str(b) in line:
                break
            if "Official: Reset " + "all" + " " + "all" in line:
                break
            if key in line:
                all_game_trials += 1
                this_game_results = eval( line.partition(key)[2] )
                all_game_time += this_game_results[1]
                current_game_tuple = this_game_results[0]
                invader_score = current_game_tuple[ len(current_game_tuple) - 1 ]
                #I keep the type of score (win, tie, loss)
                if invader_score == 0:
                    all_game_results[ len(all_game_results) - 1 ] = all_game_results[ len(all_game_results) - 1 ] + 1
                else:
                    inverse = float(self.NUM_PLAYERS)/invader_score
                    all_game_results[ inverse - 1 ] = all_game_results[ inverse - 1 ] + 1
        all_game_results = tuple( all_game_results )
        current_confidence = bayesian.main( all_game_results )
        self.comparisons[ (a,b) ] = (current_confidence, all_game_trials, all_game_time ) 
        if not found:
            f = open("Results/api.log","a")
            f.write( time.asctime() + ": " + to_write + str(current_confidence) + "\n" )
            f.close()
class Game:
    def get_results():
        return tuple( self.results )
    def __init__(self, algorithm_tuple, tokens):
        import algorithms, random, collections, copy, time
        '''Calculates a list containing the utility points of
        each player'''
        #*** This really ought to write its thinking in a log.
        start_time = time.time()
        self.tokens = list(tokens)
        self.algorithm_list = []
        #Each element of this list is itself a list containing the algorithm, its current score, and
        #a list (where elements with larger indexes are later) of this algorithm's moves.
        for x in algorithm_tuple:
            self.algorithm_list.append( [ x, 0, [] ] )
        self.algorithm_tuple = algorithm_tuple
        self.name = str(int( time.time() )) + ":" + str(random.randint(0,10**9))
        #Each algorithm receives a list of the tokens left, of everyone's scores,
        #and everyone's prior moves. However, the opponents will be put in a 
        #random order.
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The players are " + str( self.algorithm_tuple ) + "\n" )
        f.close()
        while len(self.tokens) > 1:
            current_moves = []
            for i in range(len(self.algorithm_list)):
                others = copy.copy(self.algorithm_list)
                player_list = others.pop(i)
                random.shuffle( others )
                data = []
                data.append( player_list[1:] )
                for x in others:
                    data.append( x[1:] )#Does player_tuple[0] call the algorithm? ***
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Calling Player " + str(i) + " which is " + str(player_list[0] )  + "\n" )
                f.close()
                this_move = player_list[0]( copy.deepcopy(self.tokens), copy.deepcopy(data), self.name )
                current_moves.append( this_move )
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Player " + str(i) + " responds " + str(this_move )  + "\n" )
                f.close()
            c = Counter(current_moves)
            for i in range(len(self.algorithm_list)):
                player_list = self.algorithm_list[i]
                player_list[2].append(current_moves[i])
                if c[current_moves[i]] == 1:
                    player_list[1] += current_moves[i]
            new = []
            for x in self.tokens:
                if x not in current_moves:
                    new.append(x)
            self.tokens = new
            temp_scores = []
            for x in self.algorithm_list:
                temp_scores.append( x[1] )
            f = open( "Results/games.log", "a")
            f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The intermediate scores are " + str(temp_scores)  + "\n" )
            f.close()
        if len(self.tokens) == 1:
            item = self.tokens.pop(0)
            i = 0
            for player_list in self.algorithm_list:
                i += 1
                player_list[2].append( item )
                f = open( "Results/games.log", "a")
                f.write( time.asctime() + ": Game " + self.name + ". Player " + str(i) + " (having one move left) gets " + str(item)  + "\n" )
                f.close()
                if len(self.algorithm_list) == 1:#In the unusual 1-player case, the last token is won
                    player_list[1] += item
        for x in self.algorithm_list:
                temp_scores.append( x[1] )
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": Game " + self.name + ". The tokens are " + str(self.tokens) + ". The intermediate scores are " + str(temp_scores)  + "\n" )
        f.close()
        max = 0
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max < score:
                max = score
        self.results = []
        count = 0
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max == score:
                count += 1
        for player_list in self.algorithm_list:
            score = player_list[1]
            if max == score:
                self.results.append( float( len(self.algorithm_list) ) / count )
            else:
                self.results.append( 0 )
        self.duration = time.time() - self.start_time
        fixed = True
        for i in range(len(self.algorithm_tuple)-1):
            if self.algorithm_tuple[i] != self.algorithm_tuple[i+1]:
                fixed = False
        to_write = "Official: "
        if fixed:
            to_write += "Game where " + str(self.algorithm_tuple[0]) + " is invaded by " + str(self.algorithm_tuple[len(self.algorithm_tuple) -1 ] ) + ".\n\t"
        to_write += "The game had this player_tuple: " + str(self.algorithm_tuple) + ".\n\t"
        to_write += "Here is the score_tuple: " + str(self.results) + "\n\t"
        to_write += "This game's name is " + self.name + "\n\t"
        to_write += "This game took " + str( self.duration ) + " seconds.\n"
        self.to_write = to_write
        f = open( "Results/games.log", "a")
        f.write( time.asctime() + ": " + self.to_write )
        f.close()
    def write(self):
        '''Writes the results of the game (both who won and the time) to Results/api.log. '''
        import time
        f = open( "Results/api.log", "a")
        f.write( time.asctime() + ": " + self.to_write )
        f.close()
        
