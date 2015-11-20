from .preprocessor import PreProcessorAdapter
import re
import ast

class EvaluateMathematically(PreProcessorAdapter):

    def process(self, input_text):
        """
        Takes a statement string.
        Returns the simplified statement string
        with the mathematical terms "solved".
        """

        # Getting the mathematical terms within the input statement
        expression, string = self.simplify_chunks( self.normalize( input_text ) )

        # Returning important information
        try:
            string += '= ' + str( eval( string ) )#self.evaluate( string ) )

            return string, True
        except:
            return string, False


    def simplify_chunks(self, input_text):
        """
        Separates the incoming text.
        """

        expression = []
        string = ''

        for chunk in input_text.split( ' ' ):

            is_integer = self.isInteger( chunk )

            if is_integer == False:
                is_float = self.isFloat( chunk )

                if is_float == False:
                    is_operator = self.isOperator( chunk )

                    if is_operator == False:
                        continue
                    else:
                        expression.append( is_operator )

                        string += str( is_operator ) + ' '
                else:
                    expression.append( is_float )

                    string += str( is_float ) + ' '
            else:
                expression.append( is_integer )

                string += str( is_integer ) + ' '

        return expression, string


    def evaluate( self, expression ):
        """
        Evaluates a set of expressions
        and produces an answer. Then,
        it returns the answer.
        """

        return eval( expression )


    def isFloat(self, string):
        """
        If the string is a float, returns
        the float of the string. Otherwise,
        it returns False.
        """

        try:
            float( integer )

            return float( integer );
        except:
            return False


    def isInteger(self, string):
        """
        If the string is an integer, returns
        the int of the string. Otherwise,
        it returns False.
        """

        if string.isdigit():
            return int( string )
        else:
            return False


    def isOperator(self, string):
        """
        If the string is an operator, returns
        said operator. Otherwise, it returns
        false.
        """

        if string in "+-/*^\(\)":
            return string
        else:
            return False


    def normalize(self, string):
        """
        Normalizes input text, reducing errors
        and improper calculations.
        """

        # Setting all words to lowercase
        string = string.lower()

        # Removing punctuation
        string = re.sub( '[.!?/:;]', '', string )

        # Removing words
        string = self.substitute_words( string )

        # Returning normalized text
        return string


    def substitute_words(self, string):
        """
        Substitutes numbers for words.
        """

        nums = { "one" : 1, "two" : 2, "three" : 3, "four" : 4 }
        words = { "and" : '+', "plus" : '+', "minus" : '-', "times" : '*', 'divided by' : '/' }
        scales = { 'hundred' : '* 100', 'thousand' : '* 1000' }

        condensed_string = '_'.join( string.split( ' ' ) )

        for word in words:
            condensed_string = re.sub( '_'.join( word.split( ' ' ) ), words[ word ], condensed_string )

        for number in nums:
            condensed_string = re.sub( number, str( nums[ number ] ), condensed_string )

        for scale in scales:
            condensed_string = re.sub( "_" + scale, " " + scales[ scale ], condensed_string)

        condensed_string = condensed_string.split( '_' )
        for chunk_index in range( 0, len( condensed_string ) ):
            value = ""

            try:
                value = str( eval( condensed_string[ chunk_index ] ) )

                condensed_string[ chunk_index ] = value
            except:
                pass

        return ' '.join( condensed_string )
