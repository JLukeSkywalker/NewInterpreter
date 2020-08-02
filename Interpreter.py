"""
    File:               Interpreter.py
    Associated Files:   LICENSE.txt
    Packages Needed:    sys, numpy, time
    Date Created:       7/27/2020
    Created By:         John Lukowski (https://github.com/JLukeSkywalker)
    License:            CC BY-NC 4.0  (https://creativecommons.org/licenses/by-nc/4.0/)

    Purpose:            Interpret and run files written in this language.
                        Language created to be a simple to use and learn language while
                        acting as a stepping stone into lower level languages like assembly.

    Required:
        name
        optimize as much as possible, first step, try to remove all .'s from inside loops
        stress test
        try to find uncaught bugs
        try to find interpreter bugs (might currently be errors with lists and strings)
        find a better way to print error line numbers, maybe a tuple of lineNum, command when the file is read in instead of just commands
        i think runCode can be merged into runLine and get rid of 1 while loop,
            another option would be to have runLine take in an actual line of code, not a line number,
            this might allow run to use it for functions instead of a new interpreter (variable scope though)
    Possible:
        functions have their own scope, maybe remove that
        add graphics maybe
        read and write file to/from string list
        random
        basic math appears to be slow, should probably limit to 2 inputs, then have function for sum/prod of list
        variable method is somehow a little slow
"""

# Imports
import sys, numpy, time

# Base function declarations, don't require class variables to run
"""
    Params:     err (str, Error code)
                description (str, description)
                line (int, line the error occurred on)
    Returns:    (None, should exit code)
    Purpose:    Print out the error statement and end the interpreter
"""
def printError(err, description='', line=-1):
    print(err + ' Error' + (': ' + description if description != '' else '') + ('' if line == -1 else ' || line ' + str(line+1)))
    sys.exit()

"""
    Params:     *_rest (the comment itself, not needed)
    Returns:    (bool True, just go to the next line)
    Purpose:    Don't do anything, just go to the next line
"""
def comment(*_rest):
    return True

"""
    Params:     *_rest (the error to print out, not needed here)
    Returns:    (str, 'User' Error, tells the runCode function to call printError)
    Purpose:    stop the code and show the User defined error
"""
def throwErr(*_rest):
    return 'User'

"""
    Purpose:    Run given code file line by line by calling functions from the 3 letter commands
"""
class Interpreter:
    def __init__(self, data=None, variables=None, functions=None, functionName=None):
        # hold a dictionary of all functions to run based on the 3 letter commands
        self.builtIn = {'imp':self.importFun,   # imports the functions from the file, or imports the listed functions
                        'ias':self.importAs,    # imports the function and renames it
                        'out':self.out,         # prints out the variables listed
                        'inp':self.getIn,       # stores the given input into given variable
                        'sec':self.getTime,     # returns time in seconds since epoch, usually January 1, 1970 (Unix)
                        'add':self.add,         # sums all numbers listed, stores in the new variable named
                        'sub':self.subtract,    # subtracts all numbers listed from the first one, stores in the new variable named
                        'mul':self.multiply,    # multiplies all numbers listed together, stores in the new variable named
                        'div':self.divide,      # divide each number listed from the first, stores in the new variable named
                        'int':self.integer,     # makes the named number
                        'str':self.string,      # makes the named string
                        'dbl':self.double,      # makes the named double
                        'boo':self.boolean,     # makes the named boolean
                        'ils':self.intList,     # makes the named list of numbers
                        'sls':self.strList,     # makes the named list of strings
                        'dls':self.dblList,     # makes the named list of doubles
                        'bls':self.booList,     # makes the named list of booleans
                        'vls':self.varList,     # makes the named list of variables
                        'pop':self.pop,         # stores list without the last element into the new list
                        'put':self.put,         # stores new list with the added element or list at the end or beginning
                        'idx':self.index,       # get the value at given index of given list
                        'len':self.length,      # get the length of given list
                        'cpy':self.copy,        # copy variable given to the named variable
                        'del':self.delete,      # delete given variables
                        'val':self.isAvailable, # check if given name is undeclared, store result in given boolean
                        'rel':self.relation,    # treat as relation with variables, stores bool in new variable named
                        'err':throwErr,         # throw custom error
                        'com':comment,          # comment, do nothing
                        'rif':self.runIf,       # runs the named function if variable given is True
                        'run':self.run}         # runs the provided function name with the listed variables, stores in the variable(s) named

        self.variables = {}     # hold all variables created
        self.functions = {}     # hold all functions from the file

        # This handles whether the Interpreter was started to run a function or to run a file
        if type(data) is str:
            # noinspection PyBroadException
            try:
                # Keep a copy of the original code to do error checking and report line numbers
                # WARNING, using semicolons to put 2 lines on the same will slightly mess up error reporting line numbers
                with open(data) as f:   self.original = f.read().replace(' ', '').replace('_',' ').replace(';','\n').splitlines()
                # Strip all whitespace from the file, so just in the format 3 letter command and params (comparams,params,params ...)
                self.code = list(filter(None, self.original))
            except:     printError('File', "unable to read file: '" + data+"'")
            # extract all commands and parameters into two lists
            self.commands,self.params = [i[:3] for i in  self.code],[i[3:].split(',') for i in  self.code]
            # extract all functions into a dict for later
            self.extractFunctions()
        # The Interpreter was given a function
        elif type(data) is list and not variables is None and not functions is None and not functionName is None:
            self.original = data
            self.functions = functions
            function = self.functions[functionName]
            self.returnName = function[0][0]
            paramNames = function[0][1:]
            if len(paramNames) != len(variables):   printError('Type','incorrect number of parameters passed',self.original.index('fun'+functionName+','+','.join(function[0])))
            [self.variable(paramNames[i],variables[i]) for i in range(len(paramNames))]
            self.commands = function[1]
            self.params = function[2]
        else:   printError('Run','no file or function dictionary found')

    """
        Params:     None
        Returns:    None
        Purpose:    remove all functions from the file and load them into a dictionary of name:(return var name, commands list, params list)
    """
    def extractFunctions(self):
        while 'fun' in  self.commands:
            start = self.commands.index('fun')
            params = self.params[start]
            if 'ret' not in self.commands:  printError('Function', 'missing return statement', self.original.index(self.commands[start]+','.join(params)))
            if params[0] in self.functions: printError('Function', "function '"+params[0]+"' has already been defined", self.original.index(self.commands[start]+','.join(params)))
            if params[0] == '':             printError('Function', 'no function name given', self.original.index(self.commands[start]+','.join(params)))
            end = self.commands.index('ret')
            self.functions.update({params[0] : (params[1:], self.commands[start+1:end], self.params[start+1:end])})
            del self.commands[start:end+1]
            del self.params[start:end+1]
        if 'ret' in self.commands:          printError('Function','return with no function', self.original.index(self.commands[self.commands.index('ret')]+','.join(self.params[self.commands.index('ret')])))

    """
        Params:     line(int)
                    result(None, defaulting error catching variable)
        Returns:    (int, the next line number to run)
        Purpose:    run for loops or call functions based on the command found
    """
    def runLine(self,line, result=None):
        if self.commands[line]=='for':
            if len(self.params[line]) == 2:
                iterations,lines = self.params[line]
                iterations = self.variables[iterations] if iterations in self.variables else int(iterations)
                lines = self.variables[lines] if lines in self.variables else int(lines)
                runLine = self.runLine
                for i in range(iterations):
                    loopLine = line + 1
                    maxLines = len(self.commands)
                    while loopLine < line + 1 + lines:
                        if loopLine >= maxLines:   printError('Loop','EOF reached while iterating',self.original.index(self.commands[line] + ','.join(self.params[line])))
                        loopLine = runLine(loopLine)
                return line + 1 + lines
            else:   printError('Type',"incorrect parameter type or number of parameters for command '" + self.commands[line] + "'",self.original.index(self.commands[line] + ','.join(self.params[line])))
        else:
            try:
                result = self.builtIn[self.commands[line]](*self.params[line])
            except KeyError:                printError('Type',"not a recognized command '" + self.commands[line] + "'",self.original.index(self.commands[line] + ','.join(self.params[line])))
            except (TypeError,ValueError):  printError('Type', "incorrect parameter type or number of parameters for command '" + self.commands[line] + "'",self.original.index(self.commands[line] + ','.join(self.params[line])))
            except IndexError:              printError('Index',"invalid index while executing '" + self.commands[line] + ' ' + ','.join(self.params[line]) + "'",self.original.index(self.commands[line] + ','.join(self.params[line])))
            except NameError:               printError('Variable', 'attempting to use an undeclared variable',self.original.index(self.commands[line] + ','.join(self.params[line])))
            except Exception as e:          print(repr(e));printError('', "executing '" + self.commands[line] + ' ' + ','.join(self.params[line]) + "'",self.original.index(self.commands[line] + ','.join(self.params[line])))
            if result is True:              return line + 1
            if result is None:              printError('', "incorrect syntax or parameters for command '" + self.commands[line] + ' ' + ','.join(self.params[line]) + "'", self.original.index(self.commands[line] + ','.join(self.params[line])))
            elif result == 'Variable':      printError('Variable', "variable '" + self.params[line][0] + "' has already been declared",self.original.index(self.commands[line] + ','.join(self.params[line])))
            elif result == 'Type':          printError('Type', "incorrect parameter type",self.original.index(self.commands[line] + ','.join(self.params[line])))
            elif result == 'Name':          printError('Variable', 'attempting to use an undeclared variable',self.original.index(self.commands[line] + ','.join(self.params[line])))
            elif result == 'User':          printError('User',','.join(self.params[line]),self.original.index(self.commands[line] + ','.join(self.params[line])))

    """
        Params:     func (bool, whether this was run as a function or file)
                    line (int, the line to start at)
        Returns:    (value/Bool True, value of the variable the function returns, or just True
        Purpose:    runs all of the command+param pairs in the current Interpreter object
    """
    def runCode(self, func=False, line=0):
        runLine = self.runLine
        while line < len(self.commands):    line = runLine(line)
        return self.variables[self.returnName] if func else True

    # Built-In Function Definitions, Runners for all the 3 character commands
    """
        Params:     func (bool, whether this was run as a function or file)
                    line (int, the line to start at)
        Returns:    (value/Bool True, value of the variable the function returns, or just True
        Purpose:    runs all of the command+param pairs in the current Interpreter object
    """
    def out(self,*argv):
        print(''.join([str(self.variables[arg]) if arg in self.variables else eval(arg) for arg in argv]).replace('\\n','\n'))
        return True

    """
        Params:     dest (str, variable name to store user input)
        Returns:    (value/Bool True, error code if error storing variable, else True)
        Purpose:    gets user input and stores it into the given variable name
    """
    def getIn(self, dest):
        return self.variable(dest,input("Enter value for variable '"+ (self.variables[dest]+' ' if dest in self.variables else '') +dest+"': "))

    """
        Params:     dest (str, variable name to store time)
                    startTime (float/int, time to start from, defaulted to 0)
        Returns:    (value/Bool True, error code if error storing variable, else True)
        Purpose:    gets the time since Epoch, usually January 1, 1970 (Unix) or time since startTime
    """
    def getTime(self, dest, startTime=0):
        return self.variable(dest,time.time()-(float(self.variables[startTime]) if startTime in self.variables else float(startTime)))

    """
        Params:     dest (str, variable name to store answer)
                    first (value, either a variable name or number/string)
                    second (value, either a variable name or number/string)
                    rest (values, either variable names or numbers/strings)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    adds the collection of variable values, numbers and strings together. Cannot add strings and numbers
    """
    def add(self,dest,first,second,*rest):
        if dest in self.variables and not self.variables[dest] in ['int','dbl','str','boo']:    return 'Variable'
        elif not dest in self.variables or self.variables[dest] in ['int','dbl']:               return self.variable(dest, sum([self.variables[arg] if arg in self.variables else float(arg) for arg in (first, second) + rest]))
        elif self.variables[dest] == 'str':                                                     return self.variable(dest, ''.join([str(self.variables[arg]) if arg in self.variables else eval(arg) for arg in (first, second) + rest]))
        return 'Type'

    """
        Params:     dest (str, variable name to store answer)
                    first (value, either a variable name or number)
                    second (value, either a variable name or number)
                    rest (values, either variable names or numbers)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    subtracts the collection of variable values and numbers from the first one. 
    """
    def subtract(self,dest,first,second,*rest):
        # noinspection PyBroadException
        try:    inputs = [float(self.variables[arg]) if arg in self.variables else float(arg) for arg in (first, second) + rest]
        except: return 'Type'
        if dest not in self.variables:
            return self.variable(dest,inputs[0]-sum(inputs[1:]))
        elif self.variables[dest] in ['int','dbl']:
            return self.variable(dest,inputs[0]-sum(inputs[1:]))
        elif self.variables[dest] == 'boo':
            return 'Type'
        return 'Variable'

    """
        Params:     dest (str, variable name to store answer)
                    first (value, either a variable name or number)
                    second (value, either a variable name or number)
                    rest (values, either variable names or numbers)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    multiply the collection of variable values and numbers together.
    """
    def multiply(self,dest,first,second,*rest):
        # noinspection PyBroadException
        try:                                            inputs = [float(self.variables[arg]) if arg in self.variables else float(arg) for arg in (first, second) + rest]
        except:                                         return 'Type'
        if dest not in self.variables:                  return self.variable(dest,numpy.prod(inputs))
        elif self.variables[dest] in ['int', 'dbl']:    return self.variable(dest,numpy.prod(inputs))
        elif self.variables[dest] == 'boo':             return 'Type'
        return 'Variable'

    """
        Params:     dest (str, variable name to store answer)
                    first (value, either a variable name or number)
                    second (value, either a variable name or number)
                    rest (values, either variable names or numbers)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    divide the collection of variable values and numbers from the first one. 
    """
    def divide(self,dest,first,second,*rest):
        # noinspection PyBroadException
        try:                                            inputs = [float(self.variables[arg]) if arg in self.variables else float(arg) for arg in (first, second) + rest]
        except:                                         return 'Type'
        if dest not in self.variables:                  return self.variable(dest,inputs[0]/numpy.prod(inputs[1:]))
        elif self.variables[dest] in ['int', 'dbl']:    return self.variable(dest,inputs[0]/numpy.prod(inputs[1:]))
        elif self.variables[dest] == 'boo':             return 'Type'
        return 'Variable'

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def integer(self,name,value=None):
        return self.variable(name,int(value) if value else 'int')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def string(self,name,value='str'):
        return self.variable(name,str(eval(value)))

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def double(self,name,value=None):
        return self.variable(name,float(value) if value else 'dbl')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def boolean(self,name,value=None):
        return self.variable(name, bool(eval(value)) if value else 'boo')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def intList(self,name,*rest):
        return self.variable(name,[int(i) if not i in self.variables else int(self.variables[i]) for i in rest] if len(rest)>0 else 'ils')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def strList(self,name,*rest):
        return self.variable(name,[str(i) if not i in self.variables else str(self.variables[i]) for i in rest] if len(rest)>0 else 'sls')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def dblList(self,name,*rest):
        return self.variable(name,[float(i) if not i in self.variables else float(self.variables[i]) for i in rest] if len(rest)>0 else 'dls')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def booList(self,name,*rest):
        return self.variable(name,[bool(eval(i)) if not i in self.variables else bool(self.variables[i]) for i in rest] if len(rest)>0 else 'bls')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    create a variable and store the value give, or default to the data type
    """
    def varList(self,name,*rest):
        return self.variable(name,[self.variables[i] if i in self.variables else eval(i) for i in rest] if len(rest)>0 else 'vls')

    """
        Params:     name (str, variable name)
                    value (value for variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    convert the value to the given type and store it in the variable
    """
    def variable(self,name,value=None):
        if name not in self.variables:      self.variables.update({name:value})
        elif self.variables[name] == 'int': self.variables.update({name: int(value)})
        elif self.variables[name] == 'str': self.variables.update({name: str(value)})
        elif self.variables[name] == 'dbl': self.variables.update({name: float(value)})
        elif self.variables[name] == 'boo': self.variables.update({name: bool(eval(value))})
        elif self.variables[name] =='ils':  self.variables.update({name: [int(i) for i in value]})
        elif self.variables[name] =='sls':  self.variables.update({name: [str(i) for i in value]})
        elif self.variables[name] =='dls':  self.variables.update({name: [float(i) for i in value]})
        elif self.variables[name] =='bls':  self.variables.update({name: [bool(eval(i)) for i in value]})
        elif self.variables[name] =='vls':  self.variables.update({name: value})
        else:   return 'Variable'
        return True

    """
        Params:     dest (str, variable name to store copied variable)
                    varIn (variable to copy)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    take the value of one variable and store it in another
    """
    def copy(self, dest, varIn):
        if varIn in self.variables:     return self.variable(dest,self.variables[varIn])
        return 'Name'

    """
        Params:     dest (str, variable name to store new list)
                    listIn (value for list variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    remove the last element from a list and store the new list
    """
    def pop(self, dest, listIn):
        if listIn in self.variables:    return self.variable(dest,self.variables[listIn][:-1]) if type(self.variables[listIn]) is list else 'Type'
        return 'Name'

    """
        Params:     dest (str, variable name to store new list)
                    var1 (value for list variable, default the data type specified)
        Returns:    (str/Bool True, error code if error storing variable, else True)
        Purpose:    remove the last element from a list and store the new list
    """
    def put(self, dest, var1, var2):
        if var1 in self.variables and var2 in self.variables:
            if type(self.variables[var1]) is list and type(self.variables[var2]) is list:   return self.variable(dest, self.variables[var1]+self.variables[var2])
            elif type(self.variables[var1]) is list:                                        return self.variable(dest, self.variables[var1] + [self.variables[var2]])
            elif type(self.variables[var2]) is list:                                        return self.variable(dest, [self.variables[var1]] + self.variables[var2])
            else:   return 'Type'
        return 'Name'

    """
        Params:     dest (str, variable name to store data)
                    listIn (value for list variable, default the data type specified)
                    index (int variable or entered in)
        Returns:    (str/Bool True, error code if error storing variable or if not a list/str, else True)
        Purpose:    get given element of the list or string
    """
    def index(self,dest,listIn,index):
        if listIn in self.variables:    return self.variable(dest,self.variables[listIn][self.variables[index] if index in self.variables else int(index)]) if type(self.variables[listIn]) in [list,str] else 'Type'
        return 'Name'

    """
        Params:     dest (str, variable name to store length)
                    listIn (value for list variable, default the data type specified)
                    index (int variable or entered in)
        Returns:    (str/Bool True, error code if error storing variable or if not a list/str, else True)
        Purpose:    remove the last element from a list and store the new list
    """
    def length(self,dest,listIn):
        if listIn in self.variables:    return self.variable(dest,len(self.variables[listIn])) if type(self.variables[listIn]) in [list,str] else 'Type'
        return 'Name'

    """
        Params:     rest (list of variables to delete)
        Returns:    (str/Bool True, error code if variable doesnt exist, else True)
        Purpose:    delete listed variables from variables dictionary
    """
    def delete(self,*rest):
        for variable in rest:
            if not variable in self.variables:  return 'Name'
            self.variables.pop(variable)
        return True

    """
        Params:     dest (str, variable name to store boolean)
                    name (str, name of variable to check)
        Returns:    (str/Bool True, error code if error storing variable or if not a list, else True)
        Purpose:    check to see if a variable is declared (False stored in dest) else True
    """
    def isAvailable(self, dest, name):
        return self.variable(dest,(self.variables[name] in ['int','dbl','str','boo','ils','dls','sls','bls']) if name in self.variables else True)

    """
        Params:     dest (str, variable name to store boolean)
                    rest (list of variables, relations, and,or,not,etc)
        Returns:    (str/Bool True, error code if error storing variable or if not a list, else True)
        Purpose:    convert into expression with variables and or entered values and store if it is true/false
    """
    def relation(self,dest, *rest):
        relation = ''
        for token in rest:
            if token in self.variables: relation += str(self.variables[token]) if not type(self.variables[token]) is str else "'"+self.variables[token]+"'"
            else:                       relation += ' '+token+' '
        return self.variable(dest,eval(relation))

    """
        Params:     name (str or variable for name of the function to run)
                    dest (str, variable name to store returned value)
                    rest (list of variables to pass to function)
        Returns:    (str/Bool True, error code if error storing variable or if not a list, else True)
        Purpose:    run given function with the given return variables and parameters
    """
    def run(self, name, dest, *rest):
        try:
            handler = Interpreter(data=self.original,variables=[self.variables[arg] if arg in self.variables else arg for arg in rest],functions=self.functions,functionName=self.variables[name] if name in self.variables else name)
            if not self.variable(dest,handler.runCode(func=True)):   printError('Variable', "variable '" + dest + "' has already been declared",self.original.index('run'+name+',' +dest+','+ ','.join(rest)))
            return True
        except ValueError:  printError('', "in running function '"+name+"'",self.original.index('run' + name + ',' + dest + ',' + ','.join(rest)))

    """
        Params:     boolean (bool or variable)
                    name (str or variable for name of the function to run)
                    dest (str, variable name to store returned value)
                    rest (list of variables to pass to function)
        Returns:    (str/Bool True, error code if error storing variable or if not a list, else True)
        Purpose:    run given function with the given return variables and parameters if boolean is True
    """
    def runIf(self,boolean,name, dest, *rest):
        if boolean in self.variables:
            if self.variables[boolean]: return self.run(name,dest,*rest)
            else:                       return self.variable(dest, '') if dest in self.variables and self.variables[dest] in ['str','sls'] else self.variable(dest,'0')
        elif eval(boolean) is True:     return self.run(name, dest, *rest)
        elif eval(boolean) is False:    return self.variable(dest, '') if dest in self.variables and self.variables[dest] in ['str', 'sls'] else self.variable(dest, '0')

    """
        Params:     fileName (bool or variable)
                    rest (list of functions to import)
        Returns:    (bool True, if no errors)
        Purpose:    import the list of functions from the file
    """
    def importFun(self, fileName, *rest):
        handler = Interpreter(self.variables[fileName] if fileName in self.variables else fileName)
        for fun in rest if len(rest)>0 else handler.functions:
            if fun in self.variables:           fun = self.variables[fun]
            if fun in self.functions:           printError('Import',"function '" + fun + "' already defined in this file",self.original.index('imp'+fileName+','+ ','.join(rest)))
            if fun not in handler.functions:    printError('Import', "function '" + fun + "' function not declared in '"+fileName+"'",self.original.index('imp' + fileName + ',' + ','.join(rest)))
            self.functions.update({fun:handler.functions[fun]})
        return True

    """
        Params:     fileName (bool or variable)
                    rest (list of functions to import with nicknames)
        Returns:    (bool True, if no errors)
        Purpose:    import the list of functions from the file in the format function1,newName1,function2,newName2,...
    """
    def importAs(self,fileName,*rest):
        handler = Interpreter(self.variables[fileName] if fileName in self.variables else fileName)
        if len(rest)%2 != 0:                        printError('Type', "incorrect parameters or number of parameters for command '" + 'ias' + fileName + ',' + ','.join(rest) + "'",self.original.index('ias' + fileName + ',' + ','.join(rest)))
        for var in range(0,len(rest),2):
            fun =  self.variables[rest[var]] if rest[var] in self.variables else rest[var]
            nick = self.variables[rest[var+1]] if rest[var+1] in self.variables else rest[var+1]
            if nick in self.functions:          printError('Import', "function '" + nick + "' already defined in this file",self.original.index('ias' + fileName + ',' + ','.join(rest)))
            if fun not in handler.functions:    printError('Import', "function '" + fun + "' function not declared in '" + fileName + "'",self.original.index('ias' + fileName + ',' + ','.join(rest)))
            self.functions.update({nick: handler.functions[fun]})
        return True
# END OF CLASS INTERPRETER

# Run this method if Interpreter.py was directly run
def main():
    file = 'test.txt'
    if len(sys.argv) > 2:       printError('Interpreter','only takes in 1 parameter (fileName)')
    elif len(sys.argv) == 2:    file = sys.argv[1]
    else:                       file = 'factorial.txt'#input('Enter file name to interpret: ')
    return Interpreter(data=file).runCode()
if __name__ == '__main__':
    import profile
    profile.run('main()')