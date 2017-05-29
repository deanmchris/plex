import sys
import re
import unittest

sys.path.insert(0, '..')
from plex.lexer import Lexer, LexerError


def token_types(lexer):
    return [t.type for t in lexer]


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        
        @self.lexer.on_match('\d+(\.\d+)?')
        def DIGIT(self, token):
            return token
        
        @self.lexer.on_match('[a-zA-Z]+([0-9a-zA-Z_]+)?')
        def ID(self, token):
            return token
        
        @self.lexer.on_match('(\+|\-|\*|/)')
        def OP(self, token):
            return token
        
        @self.lexer.on_match('[()]')
        def PAREN(self, token):
            return token   

    def assertTokenTypes(self, buffer, types):
        self.lexer.setup(buffer)
        self.assertEqual(token_types(self.lexer), types)

    def test_single_tokens(self):
        self.assertTokenTypes('12', ['DIGIT'])
        self.assertTokenTypes('+', ['OP'])
        self.assertTokenTypes('(', ['PAREN'])
        self.assertTokenTypes('255.678', ['DIGIT'])
        self.assertTokenTypes('x', ['ID'])
        self.assertTokenTypes(')', ['PAREN'])
        self.assertTokenTypes('*', ['OP'])
        self.assertTokenTypes('abc', ['ID'])
        self.assertTokenTypes('1.2345', ['DIGIT'])
        

    def test_multiple_tokens(self):
        self.assertTokenTypes('1.75 + 3', ['DIGIT', 'OP', 'DIGIT'])
        self.assertTokenTypes('255a + 67.2', ['DIGIT', 'ID', 'OP', 'DIGIT'])
        self.assertTokenTypes('7y * (3 * 3) - 4.6x', ['DIGIT', 'ID', 'OP', 'PAREN',
                                                      'DIGIT', 'OP', 'DIGIT', 'PAREN',
                                                      'OP', 'DIGIT', 'ID'])
        self.assertTokenTypes('a2 + b2 + c2', ['ID', 'OP', 'ID', 'OP', 'ID'])
        self.assertTokenTypes('(1) + 2 * (xy - 3) / 4z', ['PAREN', 'DIGIT', 'PAREN', 'OP',
                                                          'DIGIT', 'OP', 'PAREN', 'ID',
                                                          'OP', 'DIGIT', 'PAREN', 'OP',
                                                          'DIGIT', 'ID'])


    def test_errors(self):
        self.lexer.setup('#')
        self.assertRaises(LexerError, token_types, self.lexer)

        ln, col = self.lexer.get_pos()
        self.assertEqual(ln, 0)
        self.assertEqual(col, 0)


        self.lexer.setup('1x + 2\n2.356 * (6 /^ 7)')
        self.assertRaises(LexerError, token_types, self.lexer)

        ln, col = self.lexer.get_pos()
        self.assertEqual(ln, 1)
        self.assertEqual(col, 12)
    

        self.lexer.setup('11.75 + (2)\n(1 + 7)\n\n10 + (4 * @) - 7')
        self.assertRaises(LexerError, token_types, self.lexer)

        ln, col = self.lexer.get_pos()
        self.assertEqual(ln, 3)
        self.assertEqual(col, 10)

    
if __name__ == '__main__':
    unittest.main()
