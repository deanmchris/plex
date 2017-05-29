"""Lighweight regex based lexer.

This module provides a lighweight, easy to use regex based lexer. It can
be used for a varity of task and is very extensible.

The entry point of the module is lexer.Lexer(), which creates a new lexer
instance. Token regexes are specfied using decortators defined in the Lexer
class. The lexer also allows you to override its default error method using
a decorator. The functions that are decoratored can be used to take certain actions
when a token is found.

tokens returned by the lexer are Token objects. Each token object has
a value, a type, and a two-tuple position variable, representing the
tokens line and column number.


Whenever the  the lexer cannot match any rules specfied, a LexerError
is raised.


Here is a minmal example demonstrating the general structure of the
module's parts.

    from plex.lexer import Lexer, INTEGER_PAT

    lexer = Lexer()
    lexer.setup('1 + 2')

    @lexer.on_match(INTEGER_PAT)
    def INTEGER(self, token):
        return token

    @lexer.on_match('(\+|\-|\*|/)')
    def OPERATOR(self, token):
        return token
        
    for token in lexer:
        print(token)

While LexerError and Token are both considered public, they should only
be used to test the type of variables. They should not be called directly.
"""

__author__ = 'Christian Dean <c1dea2n@gmail.com>'
__all__ = ['Lexer', 'LexerError', 'Token']


import re


WHITESPACE = """\s+"""
LEXER_ERR_MSG = \
"""

lexing error at line {}, column {}:

     {}
     {}^

invalid character in source
"""
                

class PatternAction:
    __slots__ = ('pattern', 'action')
    def __init__(self, pattern, action):
        self.pattern = pattern
        self.action = action

    def __repr__(self):
        return 'PatternAction(pattern={}, action={})'.format(
            self.pattern, self.action.__name__
        )


class Token:
    """Object to hold token data.

    Each Token object has the
    following public fields:

        value : str
            The textual value of the token.

        type : str
            The type of the token.

        pos : tuple
            A two tuple variable, where the first element is the
            line number of the token, and the second is the column.
    """
    __slots__ = ('value', 'type', 'pos')
    def __init__(self, value, type, pos):
        self.value = value
        self.type = type
        self.pos = pos

    def __repr__(self):
        return 'Token(value={}, type={}, pos={})'.format(
            self.value, self.type, self.pos
        )


class LexerError(Exception):
    """Exception to raise if the parser encounters an error."""
    pass


class Lexer:
    """Lexer object.

    The lexer has the following public methods:

        setup:
            Feed the lexer an input buffer.

        get_pos:
            The the current position of the lexer.

        on_match:
            The decorator used for specifiy token regexes. Takes
            in a single pattern for matching a token, and the function
            itself for the action to be "done" when said token is found.

            The decorated function should accept two arguments. self, which
            is an instance of the Lexer class, and token, which is the token
            that will be given back to the function if the regex is matched.

        on_error:
            The decorator used to override the default error method of the
            Lexer class. The decorated function should accept one argument
            would be the character which could not be matched.

    The lexer as the following public attrbiutes. These can be used as
    "hooks", to customize how the lexer deals with certian things:

        buffer : str
            The buffer of text the lexer will lex.

        pos : int
            The current position of the lexer in the source.

        col_no : int
            The current column number the lexer is at.
    """
    def __init__(self): 
        self.buffer = ''
        self.pos = 0
        self.col_no = 0
        self._line_start = 0
        self._error_func = None
        self._ignore_ws = True
        self._ws_pattern = re.compile(WHITESPACE)
        self._rules = {}
       
        
    def setup(self, buffer, ignore_ws=True):
        """ Feed the lexer an input buffer.

        Parameters
        ----------
        buffer : str
            The stirng for the lexer to tokenize.

        ignore_ws : bool
            This deterimes wheather or not the lexer skips whitespace.
            The default is True.
        """
        self.buffer = buffer
        self.pos = 0
        self.col_no = 0
        self._ignore_ws = ignore_ws

    def _token(self):
        _buffer = self.buffer
        _ignore_ws = self._ignore_ws
        _rules = self._rules

        if self._ignore_ws:
            match = self._ws_pattern.match(_buffer, self.pos)
            if match:
                if '\n' in match.group(0):
                    self._line_start = match.end()
                self.pos = match.end()

        if self.pos >= len(_buffer):
            return None
        else:
            for token_name, pattern in _rules.items():
                match = pattern.pattern.match(_buffer, self.pos)
                if match:
                    token = Token(match.group(0), token_name, self.get_pos())
                    modfied_token = pattern.action(self, token)
                    self.pos = match.end()
                    return modfied_token
            self._error()

    def get_pos(self):
        """The current internal line and column number of the lexer."""
        line_no = self.buffer.count('\n', 0, self.pos)
        return line_no, self.pos - self._line_start
    
    def _error(self):
        if self._error_func is None:
            line, column = self.get_pos()
            source_line = self.buffer.split('\n')[line]

            error_msg = LEXER_ERR_MSG.format(
                line, column, source_line, ' ' * column
            ) 
            raise LexerError(error_msg)
        else:
            self._error_func(self, self.buffer[self._pos])

    def __iter__(self):
        return self

    def __next__(self):
        token = self._token()
        if token is not None:
            return token
        raise StopIteration()

    # Python 2 support
    next = __next__

    def on_match(self, pattern):
        """Decorator for specifying token rules.

        Rules given should be a valid regex. The name
        of the decorated function, will be used as the
        token type's name.

        Decorated functions should accept two arguments.
        The first is an instance of the lexer class, and
        the second is the token object created if the token
        pattern is matched.

        
        Parameters
        ----------
        pattern : str
            The pattern which defines the current
            token rule.


        Usage(assuming you've already made an instance of Lexer):

            @lexer.on_match('\d+')
            def DIGITS(self, token):
                print('found: %s' % token.value)
                return token

        The token rule above will match any whole number. If the token
        pattern does match, the function will be called, the lexer instance
        and the token object will be passed in, and the token will be returned.

        The decorated function is allowed to modify the token object in any
        way. But the function *MUST* return a Token object.
        """
        
        def decorator(func):
            compiled_pattern = re.compile(pattern)
            self._rules[func.__name__] = PatternAction(
                compiled_pattern , func
            )
            return func
        return decorator

    def on_error(self, func):
        """Decorator for overriding the default error function.

        Parameters
        ----------
        func:
            The decorated error function. The function is allowed
            to do whatever is sees fit when an error is encountered,
            including skipping the character to ignore unreconized
            characters.

        Usage(assuming you've already made an instance of Lexer):

            @lexer.on_error
            def error(self, value):
                raise Exception('My custom error!!')

        The decorated function should accept two arguments. The first is
        a lexer instance, the second is the value which caused the lexer
        to err out.

        Usage(assuming you've already made an instance of Lexer):
        """
        self._error_func = func
        return func

