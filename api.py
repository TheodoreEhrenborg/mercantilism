'''This module contains the Artificial Primary Investigator
(API). It only run programs at night to keep CPU speed constant.
It keeps the main log and decides which algorithms to test 
against each other.'''
def main():
    the_api = API()
    the_api.run()
class API:
    import time
    def __init__(self):
        self.previous_command_time = 0
        self.should_quit = False
        self.should_adjourn = False
        self.should_reload = False
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
        '''Looks for commands and executes them.
        If a command is quit, adjourn, or reload,
        this method executes the other commands first, and
        then ends. The caller has to deal with quit, adjourn,
        or reload.'''
        commands = self.get_new_commands()
        f = open("api.log","a")
        highest_priority = None
        for i in commands:
            f.write( time.asctime() + ": " + "Got command \'" + i + "\'" )
            if i = 'quit':
                should_quit = True
            elif i = 'adjourn':
                should_adjourn = True
            elif i = 'reload':
                should_reload = True
            elif i = 
            else:
                f.write( time.asctime() + ": " + "Could not understand command!" )            
    def run(self):
        #I need a way to run this during daytime.***
        try:
            f.open("api.log","r")
            l = f.readlines()
            f.close()
            if "Official: Quitting" not in l[ len(l) - 1 ]:
                raise Exception("It seems that the previous session of API did not quit!")
        catch IOError:
            pass
        while not should_quit:
            self.execute_commands()
            if ( not should_quit ) and ( not should_adjourn ):
                #Read the log and update the algorithm list and priorities
            self.execute_commands()
            if ( not should_quit ) and ( not should_adjourn ) and ( not should_reload ) :
                #Choose a comparison and do it. Repeat. Check for commands every 5 min
            if ( not should_quit ) and ( should_adjourn ):
                f = open("api.log","a")
                f.write( time.asctime() + ": " + "Adjourning" )
                f.close()
                self.adjourn()
        f = open("api.log","a")
        f.write( time.asctime() + ": " + "Official: Quitting" )
        f.close()
    def adjourn(self):
        while should_adjourn:
            time.sleep( 300 )
            self.execute_commands()
    def search(self):
        '''I don't know if this method is complete. ***
        Checks whether a CPU-intensive process is running.'''
        import os
        os.system("top -stats command -l 1 > top-output.txt")#Write the activity monitor to a file    
        f=open("top-output.txt","r")
        process_active = False
        for line in f:
            if ('firefox' in line) or ('Google Chrome' in line) or ('Safari' in line and 'SafariCloudHisto' not in line and 'com.apple.Safari' not in line and 'SafariBook' not in line) or ('mprime' in line) or ('Mathematica' in line):
                process_active = True
                break	       	 
        f.close()
