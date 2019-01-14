'''This module contains the Artificial Primary Investigator
(API). It only run programs at night to keep CPU speed constant.
It keeps the main log and decides which algorithms to test 
against each other.'''
def main():
    the_api = API()
    the_api.run()
class API:
    import time, algorithms, inspect, bayseian
    def __init__(self):
        pass
    def get_time(self,line):
        '''Returns the number before the first ':' '''
        i = line.index(':')
        return float(line[0:i])
    def get_command(self,line):
        '''Returns the string after the first ':' '''
        i = line.index(':')
        return line[i+1:]
    def get_new_commands(self):
        ''' Looks in the appropriate file and returns a list
        of the new commands from human_friendly '''
        f = open("Results/human_friendly_to_api.txt", "r")
        lines = f.readlines()
        f.close()
        result = []
        for line in lines:
            t = self.get_time( line )
            if t > previous_command_time:
                result.append( self.get_command( line ) )
                previous_command_time = t
       return result
    def execute_commands(self):
        '''Looks for commands and executes them -- puts them on the log.
        If a command is quit, adjourn, or reload,
        this method executes the other commands first, and
        then ends. The caller has to deal with quit, adjourn,
        or reload.'''
        self.should_adjourn = False
        commands = self.get_new_commands()
        f = open("api.log","a")
        highest_priority = None
        for i in commands:
            f.write( time.asctime() + ": " + "Got command \'" + i + "\'" + "\n" )
            if i = 'quit':
                self.should_quit = True
            elif i = 'adjourn':
                self.should_adjourn = True
            elif time.localtime()[3] >= 14 and time.localtime()[4] >= 30:
                self.should_reload = True
            elif i = 'reload':
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
    def run(self):
        #I need a way to run this during daytime.***
        self.NUM_PLAYERS = 5
        self.previous_command_time = 0
        self.should_quit = False
        self.should_adjourn = False
        self.should_reload = False
        self.confidence = 0.99
        self.max_time = 300 * 100
        self.min_time = 30
        self.max_trials = 100
        self.min_trials = 5
        try:
            f.open("api.log","r")
            l = f.readlines()
            f.close()
            if "Official: Quitting" not in l[ len(l) - 1 ]:
                raise Exception("It seems that the previous session of API did not quit!")
        catch IOError:
            pass
        while not self.should_quit:
            self.execute_commands()
            if ( not self.should_quit ) and ( not self.should_adjourn ):
                #Read the log and update the algorithm list and priorities
                self.use_log()
            self.should_reload = False
            self.execute_commands()
            if ( not self.should_quit ) and ( not self.should_adjourn ) and ( not self.should_reload ) :
                #Choose a comparison and do it. Repeat. Check for commands every 5 min
                self.do_comparisons()
            if ( not self.should_quit ) and ( self.should_adjourn ):
                self.adjourn()
        f = open("api.log","a")
        f.write( time.asctime() + ": " + "Official: Quitting" )
        f.close()
    def adjourn(self):
        f = open("api.log","a")
        f.write( time.asctime() + ": " + "Adjourning" )
        f.close()
        while self.should_adjourn:
            time.sleep( 300 )
            self.execute_commands()
    def check_for_proceses(self):
        '''Checks whether a CPU-intensive process is running.'''
        import os
        os.system("top -stats command -l 1 > top-output.txt")#Write the activity monitor to a file    
        f=open("top-output.txt","r")
        process_active = False
        for line in f:
            if ('firefox' in line) or ('Google Chrome' in line) or ('Safari' in line and 'SafariCloudHisto' not in line and 'com.apple.Safari' not in line and 'SafariBook' not in line) or ('mprime' in line) or ('Mathematica' in line):
                process_active = True
                break	       	 
        f.close()
        return process_active
    def use_log(self):
        list_algorithms = inspect.getmembers( algorithms, inspect.ismethod)
        #***Make sure we can only get algorithms without aux_ in __name__
        f = open("api.log","r")
        lines = f.readlines()
        f.close()
        lines = lines.reverse()
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
        self.comparsions = {}
        for a in list_algorithms:
            for b in list_algorithms:
                DEFAULT = 0.5
                current_confidence = DEFAULT
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
                self.comparisons[ (a,b) ] = current_confidence 
                if not found:
                    f = open("api.log","a")
                    f.write( time.asctime() + ": " + key + str(current_confidence) + "\n" )
                    f.close()
    def do_comparisons(self):
        '''Choose a comparison and do it. Repeat. Check for commands every 5 min'''
        most_recent_check = time.time()
        closest = 0
        for x in self.comparisons.values():
            if abs( x - 0.5) < abs(closest - 0.5):
                closest = x
        for current_pair in self.comparisons.keys():
            if self.comparisons[current_pair] == closest:
                break
        
        
