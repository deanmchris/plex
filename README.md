Plex v0.1.0
====

**Plex** is a simple, easy to use, lightweight regex based lexer. Its design is inspired by the [sly](https://github.com/dabeaz/sly) lexer. Specificly, in the way token patterns are defined. **Plex** makes heavy use of Python's decorator syntax to provide an easy and readable way to specfiy token patterns. Plex also allows you to have "action" functions, which run when a certian token pattern is matched. This allows you to have a very fine degree of control over how the lexer works.

Installation
------------
To install **Plex**, download a copy of this repository and unzip the the folder. Once unzipped, enter the directory of the unzipped repository and run the `setup.py` file inside. eg:

`python setup.py install`

Alternatively, you can use `pip` instead. First, make sure you have the `pip` Python package manager installed. Once installed, run the following command from the terminal:

`pip install git+git://github.com/algerbrex/plex.git`.
  
As of now, **Plex** is **not** currently regisrted in the PyPi package index. 
 
Tests
-----
 
You can run the tests for **Plex** by executing the following command in the `tests/` folder located in the root reposistory directory: `python test_lexer.py`.
 
Quickstart
----------
 
As mentioned above, one of the biggest benifits of plex is that it allows you to define token patterns in a readable fasion using decorators.
 
Here is a simple example which tokenizes numbers and operators:
 
```python
from plex.lexer import Lexer

lexer = Lexer()

@lexer.on_match('\d+')
def DIGITS(self, token):
    return token
    
@lexer.on_match('(\+|\-|\*|/)')
def OPERATOR(self, token):
    return token
    
@lexer.on_error
def error(self, value):
    raise Exception('Value {} could not be matched'.format(value))
    
lexer.setup('1 + 2 * 3')
for token in lexer:
    print(token)
```

Which has the output:

```
Token(value=1, type=DIGITS, pos=(0, 0))
Token(value=+, type=OPERATOR, pos=(0, 2))
Token(value=2, type=DIGITS, pos=(0, 4))
Token(value=*, type=OPERATOR, pos=(0, 6))
Token(value=3, type=DIGITS, pos=(0, 8))
```

The `on_match()` decorator lets you map a function - an "action" - to a token pattern. Whenver _that_ specfic token pattern is matched, the mapped function will be run. `on_error` allows you to define a custom function for when the lexer encounters an un-lexeable character. Note however this is usally not nesscary, as the default error for the lexer is very informative and helpful.

Using **Plex** is as simple as that. The only cavent

Documention
----------- 
The public interface of **Plex** is well documented with comments in plex/lexer.py. For a full public API reference, you can use the `help()` function to display the docstirngs of the module, and the modules public classes.

Contributions
-------------

Contributions and suggestions are welcome. If you add functionality
to **Plex**, it would be appricated if you also wrote serval test for
it.

License
-------

This package is realesed under the MIT license. A full copy of the license can be found in `LICENSE`.
