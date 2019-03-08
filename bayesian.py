import decimal, random, time, math
Decimal = decimal.Decimal
import numpy as np
class SuperFloat:
    def __init__(self, f, exp = 0):
        import math
        if f == 0:
            self.__value = 0
            self.__exp = 0
        else:
            self.__exp = int( math.log( abs(f), 10 ) )
            self.__value = f * 10 ** -self.__exp
            self.__exp += exp
            #Here we should use format(2**320, "E").partition("E+") to get the 
            #exp and value without multiplying by large numbers
    def get_exp(self):
        return self.__exp
    def get_value(self):
        return self.__value
    def __add__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        if self.get_exp() > other.get_exp():
            other_float = other.get_value() * 10 **(other.get_exp() - self.get_exp())
            return SuperFloat( self.get_value() + other_float, self.get_exp())
        else:
            self_float = self.get_value() * 10 ** (self.get_exp() - other.get_exp())
            return SuperFloat( other.get_value() + self_float, other.get_exp())
    def __sub__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return self + SuperFloat( -1 * other.get_value(), other.get_exp())
    def __mul__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return SuperFloat( self.get_value() * other.get_value(), self.get_exp() + other.get_exp())
    def __div__(self,other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        return SuperFloat( self.get_value() / other.get_value(), self.get_exp() - other.get_exp())
    def old_pow(self,other):
        if not isinstance(other, int) or other < 0:
            raise Exception("Other is not a nonnegative integer")
        start = SuperFloat( 1 )
        for x in range( other ):
            start *= self
        return start
    def __pow__(self,other):
        if not isinstance(other, int) or other < 0:
            raise Exception("Other is not a nonnegative integer")
        start = SuperFloat( 1 )
        current_square = self
        in_base_2 = to_base_2(other)
        in_base_2.reverse()
        for x in in_base_2:
            if x:
                start *= current_square
            current_square = current_square * current_square 
        return start
    def as_float(self):
        return float(self.get_value() * 10 ** self.get_exp())
    def __cmp__(self, other):
        if not isinstance(other, SuperFloat):
            raise Exception("Other is not a SuperFloat")
        x = self - other
        if x.get_value() == 0:
            return 0
        elif x.get_value() > 0:
            return 1
        else:
            return -1
    def __repr__(self):
        return "SuperFloat(" + str( self.get_value()) +str(" , ") + str( self.get_exp() ) + str(")")
def main(game_results = range(32), trials = 1e5, test_case = None, final_diff_exp = -10):
    '''Uses five dimensions with multiplicities and the Decimal class'''
    #Note that game_results is of the form ( x , y , ... , w )
    #where each value is the number of times a game has had a certain outcome (like the first and third players tie)
    #However, the first element of game_results is zero because all players cannot all lose
    #import Monte Carlo integration algorithm from scikit-monaco library
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Got game_results = " + str(game_results) + 
            " Got trials = " + str(trials) + "\n")
    f.close()
    #n is the number of players
    n = int( math.log( len(game_results) , 2) )
    compressed = []
    multiplicities = []
    weights = []
    for x in range(n+1):
        compressed.append(0)
        multiplicities.append(0)
        weights.append(0)
    for i in range( 1, len(game_results) ):
        base_2 = to_base_2(i)
        c = sum(base_2)
        if base_2[-1] == 0:
            compressed[0] += game_results[i]
            multiplicities[0] += 1
            weights[0] = 0 #Note that losses come first, then wins, 2-ties, ..., n-ties
        else:
            compressed[c] += game_results[i]
            multiplicities[c] += 1
            weights[c] =  float(n)/c
    if test_case != None:
        compressed = test_case
#    print compressed, weights, multiplicities
    #Now I need to run below_average_cases. I should figure out the 
    #weights of each outcome -- a win is n points -- and the average 
    #utility points to beat. I'll do that here instead of in the 
    #thousands of runs of below_average_cases.
    average = 1
    abridged = game_results[1:]
    #integrate all probabilities over the hypercube
    #For n players, a game could end in 2^n - 1 ways
    best_point_tuple = tuple( normalize( compressed ) )
    old_lowers = None
    old_uppers = None
    results = np.array([ Decimal(0), Decimal(0) ])
    for e in range(final_diff_exp,1):
        diff = 2**e
        sample_lowers = np.zeros( (n,) )
        sample_uppers = np.ones( (n,) )
        for i in range(n):
            x = best_point_tuple[i]
            sample_lowers[i] = max( x - diff, 0)
            sample_uppers[i] = min(x + diff, 1) 
        results += integrate( both , args = [compressed, weights, average, multiplicities],
                            npoints = trials, lowers = sample_lowers, uppers = sample_uppers,
                            excluded_lowers = old_lowers, excluded_uppers = old_uppers)
        old_lowers = sample_lowers
        old_uppers = sample_uppers
    total = results[0]
    below = results[1]
    f = open("Results/bayesian.log","a")
    f.write(time.asctime() + ": Calculated total probability = " + str(total) + "\n")
    f.write(time.asctime() + ": Calculated below average probability = " + str(below) + "\n")
    f.close()
    #Divide to get the chance that 1 is not ES against 2
    #No, it's the chance that the fixed strategy is ES against the invader
    return  below / total
def both( point_tuple, args ):
    compressed_game_results = args[0]
    weights = args[1]
    average = args[2]
    multiplicities = args[3]
    point = list( point_tuple )
    point.sort()
    point = [0] + point + [1,]
    density = Decimal(1)
#    average_multiplier = 0
    for i in range( len(compressed_game_results) ):
        how_many_games = compressed_game_results[i]
        m = multiplicities[i]
        interval = Decimal( point[i+1] - point[i] )
#        print interval, how_many_games
#        average_multiplier += interval * m
        density *= interval ** how_many_games
        try:
            density *= interval ** (m-1)
        except decimal.InvalidOperation:
            print point, interval
#        density *= m ** interval
#    density *= average_multiplier
    result1 = density
    expected_utility = 0
    for i in range( len(weights) ):
        expected_utility += weights[i] *  ( point[i+1] - point[i] )
    if expected_utility < average:
        result2 = result1
    elif expected_utility > average:
        result2 = 0
    else:
        result2 = 0.5 * result1
#    print result1, result2, density
    return np.array( [result1,result2] ) 
def list_total( l ):
    t = 0
    for x in l:
        t += x
    return t
def normalize( l ):
    t = list_total( l )
    new = []
    this_value = 0
    for x in l[:-1]:
        this_value = float(x) / t + this_value
        new.append( this_value )
#    print new, l
    return new
def to_base_2(x):
    '''x is a positive integer. Returns a list that is x in base 2.
    For instance, 22 becomes [1, 0, 1, 1, 0] and 0 becomes []''' 
    x = int( x )
    result = []
    while x > 0:
        if x % 2:
            result.append(1)
        else:
            result.append(0)
        x = x/2
    result.reverse()
    return result
def integrate( function, args, npoints, lowers, uppers, excluded_lowers = None, excluded_uppers = None):
    '''Finds the integral of the function in the box from lowers to uppers, not including
    the box from excluded_lowers to excluded_uppers'''
    dim = len(lowers)
    if dim != len(uppers):
        raise Exception("Dimension error")
    #If the following is True, don't worry about excluded areas
    go_for_it = not isinstance(excluded_lowers, np.ndarray)
    total = np.array( [Decimal(0),Decimal(0)] )
    for i in range(npoints):
        this_point = np.zeros(dim)
        for j in range(dim):
            r = random.random()
            rand_value = lowers[j] + r * ( uppers[j] - lowers[j] )
            this_point[j] = rand_value
#        if not go_for_it:
#            print np.any(this_point - excluded_lowers) < 0
        if go_for_it or np.min(this_point - excluded_lowers) < 0 or np.min(excluded_uppers - this_point) < 0: 
            density = function( this_point, args )
#            print density
            total += density
#    print total, total/ float(npoints)
    volume = np.abs( np.product( uppers - lowers ) )
    return Decimal(volume) * total / Decimal(npoints)
        
