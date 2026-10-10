# Professor David

A symbolic mathematics engine built from scratch in Python.

The project represents mathematical expressions using custom classes (with many features under the hood for caching frequency tables, which is very important for commutative matching).
It uses symbolic manipulation rules to simplify, differentiate, and solve mathematical expressions.

## Features

* Optimized internal representation for symbolic computation
* Built in assumption system (that can deduce facts!)
* Algebraic simplification
* Pattern-based rewrite rules
* Symbolic differentiation
* Symbolic equation solving
* LaTeX rendering of expressions

### Equation Solving

The solver currently supports selected classes of:

* Linear equations
* Polynomial equations
* Exponential equations
* Logarithmic equations
* Nonlinear equations using substitutions

Examples:

```python
>>> solve(Equals(
    3*x + 7,
    19
), x)
(4Ⓩ,)

>>> solve(Equals(
    x**2 - 5*x + 6,
    0
), x)
(3Ⓩ, 2Ⓩ)


>>> solve(Equals(
    x**10 * (x + 1),
    0
), x)
(0Ⓩ, -1)  # Note that -1 has a different representation to normal numbers

>>> solve(Equals(
    e**(2*x) - 4 * e**x,
    -4
), x)
(Log❲𝑒❳[2Ⓩ],)


>>> solve(Equals(
    e**(3*x),
    7
), x)
(Multiply[Power[3Ⓩ, -1], Log❲𝑒❳[7Ⓩ]],)  # 1/3 ln(7)

>>> solve(Equals(
    Log(e, x),
    3
), x)
(Power[𝑒, 3Ⓩ],)
```

See all above examples in `demo.py`.

### Symbolic Differentiation

The differentiation engine applies symbolic differentiation rules to differentiate arbitrary expressions.

In particular, it combines the product rule and chain rule to differentiate ANY expression. These are sufficient as any other differentiation rules, like the quotient rule, are just the chain rule and product rule under the hood.
This does lead to very large expressions, so they have to be simplified using the simplification rules of `simplify()`.

Examples:


```python
>>> differentiate(
    x**3 + 2 * x**2 - 5*x + 1,
    x
)
Add[Multiply[5Ⓩ, -1], Multiply[4Ⓩ, x], Multiply[3Ⓩ, Power[x, 2Ⓩ]]]

>>> differentiate(
    x**2 * Sin(x),
    x
)
Add[Multiply[2Ⓩ, x, sin[x]], Multiply[Power[x, 2Ⓩ], cos[x]]]

>>> differentiate(
    e**x,
    x
)
Power[𝑒, x]

>>> differentiate(
    Log(e, x),
    x
)
Power[x, -1]

>>> differentiate(
    Sin(x**2),
    x
)
Multiply[2Ⓩ, x, cos[Power[x, 2Ⓩ]]]

>>> differentiate(
    x**x,
    x
)
Multiply[Power[x, x], Add[1Ⓩ, Log❲𝑒❳[x]]]


```

See all above examples in `demo.py`.

## Implementation

Expressions are represented using custom symbolic structures rather than being evaluated directly as numerical Python expressions.

Symbolic manipulation is performed using pattern-matching operated by a custom pattern matcher. This allows me to implement arbitrary rewrite rules for simplifying expressions in a way similar to how a human would.

The equation solver analyses the structure of an expression and attempts different solving strategies. These include include:

* Collection (reducing the number of instances of a variable)
* Isolation (bringing terms closer together, and if there is just 1 instance, solve directly by reversing operations around the single instance - like an onion!)
* Homogenization (attempting to find a common substitution between terms to transform an equation into a polynomial)
* PolySolve (used to solve polynomials given a mapping of exponents to coefficients)

The project is still experimental and there are some serious bugs. These include a limited support for complex roots and trigonometry (which I am working on!)

### Pattern optimisation for commutative pattern matching

One of the largest issues was matching terms in commutative structures like addition or multiplication, because there are just so many possibilities. The matcher contains several optimisations to reduce unnecessary search:

* Pattern terms are reordered before commutative matching
* Frequency tables avoid repeatedly scanning identical terms
* Already resolved wildcards are matched directly against the remaining frequency table
* Contradictory wildcard assignments are rejected as soon as they are detected
* Sequence matching can match all remaining compatible terms when there is only one sequence wildcard

Which reduces a problem of many, MANY (looking at you Γ function) possibilities, to something more manageable!
