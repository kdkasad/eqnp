# eqnp
A simple expression parser/calculator

## Goal

The goal of eqnp is to be a program which can parse expressions (and maybe
equations at some point) and can manipulate them in various ways. This might
include:

 * Simplifying
 * Differentiating (finding derivatives)
 * Integrating (finding integrals)
 * Solving (isolating variables)

In addition, this is a project that I'm creating only from my own knowledge. My
goal is to not use any resources relating to the actual function of eqnp.
(Python documentation is acceptable, of course.)

## Usage

Import the `parse_expression()` function from `eqnp.parser`:

```python
from eqnp.parser import parse_expression

# or

from eqnp import *
```

Then run `parse_expression(...)`, passing in a string which is an expression.
[See below](#expression-string-syntax) for syntax.

### Expression string syntax

Currently, the following operators, functions, and other syntactical structures
are supported (`...` means an expression):

| Syntax      | Meaning                                                         |
| ---         | ---                                                             |
| `... + ...` | Addition -- Must have operands on either side                   |
| `... - ...` | Subtraction -- Must have operands on either side                |
| `... * ...` | Multiplication -- Must have operands on either side             |
| `... / ...` | Division -- Must have operands on either side                   |
| `(...)`     | Grouping -- used to group operations to enforce a certain order |
| `\|...\|`     | Absolute value -- same as `abs(...)`                            |
| `abs(...)`  | Absolute value                                                  |
| `sin(...)`  | Sine function                                                   |
| `cos(...)`  | Cosine function                                                 |
| `tan(...)`  | Tangent function                                                |
| `csc(...)`  | Cosecant function                                               |
| `sec(...)`  | Secant function                                                 |
| `cot(...)`  | Cotangent function                                              |
| `-n`        | Negation -- `n` must be a constant number                       |

## To do

There are still a lot of features that I want to implement. Some are listed as
`# TODO:` comments in the source code, but I'll put a list here too:

* Pull all constants out of nested multiplication expressions
* Flip negative exponents in fractions to opposite side
* Add inverse trigonometric functions
* Implement integration
