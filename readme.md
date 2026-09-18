# Professor David

A symbolic mathematics engine built from scratch in Python.

The project represents mathematical expressions using custom classes (with many features under the hood for caching frequency tables, which is very important for commutative matching).
It uses symbolic manipulation rules to simplify, differentiate, and solve mathematical expressions.

## Features

* Custom symbolic expression representation
* Expression parsing and manipulation
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

```text
3x + 7 = 19
→ x = 4

x² - 5x + 6 = 0
→ x = 3, 2

x¹⁰(x + 1) = 0
→ x = 0, -1

e²ˣ - 4eˣ = -4
→ x = ln(2)

e³ˣ = 7
→ x = ln(7)/3

ln(x) = 3
→ x = e³
```

In code: see all above examples in `demo.py`.

An example in code (to demonstrate the syntax):

```python
>>> solve(Equals(
    3*x + 7,
    19
), x)
(4Ⓩ,)
```

### Symbolic Differentiation

The differentiation engine applies symbolic differentiation rules to differentiate arbitrary expressions.

In particular, it combines the product rule and chain rule to differentiate ANY expression. These are sufficient as any other differentiation rules, like the quotient rule, are just the chain rule and product rule under the hood.
This does lead to very large expressions, so they have to be simplified using the simplification rules of `simplify()`.

Examples:

```text
d/dx (x³ + 2x² - 5x + 1)
→ 3x² + 4x - 5

d/dx (x² sin(x))
→ 2x sin(x) + x² cos(x)

d/dx (eˣ)
→ eˣ

d/dx (ln(x))
→ 1/x

d/dx (sin(x²))
→ 2x cos(x²)

d/dx (x^√x)
→ x^√x (ln(x)/(2√x) + 1/(2x))
```

In code: see all above examples in `demo.py`.

An example:

```python
>>> differentiate(x**2, x)
Multiply[2Ⓩ, x]
```

## Implementation

Expressions are represented using custom symbolic structures rather than being evaluated directly as numerical Python expressions.

Symbolic manipulation is performed using pattern-matching operated by a custom pattern matcher. This allows me to implement arbitrary rewrite rules for simplifying expressions in a way similar to how a human would.

The equation solver analyses the structure of an expression and attempts different solving strategies. These include include:

* Collection (reducing the number of instances of a variable)
* Isolation (bringing terms closer together, and if there is just 1 instance, solve directly by reversing operations around the single instance - like an onion!)
* Homogenization (attempting to find a common substitution between terms to transform an equation into a polynomial)
* PolySolve (used to solve polynomials given a mapping of exponents to coefficients)

The project is still experimental and there are some serious bugs. These include a limited support for complex roots and trigonometry (which I am working on!)


## Equation Solving

At a high level, an equation is processed as follows:

```text
Equation
   ↓
Inspect expression structure
   ↓
Is the variable isolated?
   ├── Yes → Reverse the operations to isolate it
   │
   └── No
        ↓
Move everything to one side
        ↓
Simplify / collect terms (to reduce number of instances of variable)
        ↓
Is it a polynomial?
   ├── Yes → Extract coefficients → Polynomial solver
   │
   └── No
        ↓
Can the expression be transformed by substitution?
   ├── Yes → Homogenise → Solve recursively → Back-substitute
   │
   └── No → Equation is currently unsupported
```

### 1. Isolated variables

For equations where the variable is contained inside a sequence of reversible operations, the solver works backwards through the expression tree.

For example:

```text
3x + 7 = 19

3x = 12
x = 4
```

The solver identifies the outer operation and applies its inverse, recursively reducing the expression until the variable is isolated (the onion!)

### 2. Polynomial solving

When an equation can be reduced to a polynomial, the solver extracts its coefficients and passes them to a polynomial-solving routine.

For example:

```text
x² - 5x + 6 = 0

→ coefficients [6, -5, 1]

→ x = 3, 2
```

This also allows factored expressions to be handled naturally:

```text
x¹⁰(x + 1) = 0

→ x¹⁰ = 0  or  x + 1 = 0

→ x = 0, -1
```

This also handles cases where each term's exponent has a common GCD that is greater than 1:

```
x⁴ - 10 x² + 25 = 0
Would find u = x², solve u² + 10u + 25 = 0
Then, back substitute u = 5 as x² = 5 to give solutions in x
```

### 3. Substitution

For some nonlinear equations, the solver attempts to identify repeated structures and transform the equation into a simpler form.

For example, an equation involving repeated powers of `eˣ` can be transformed using a substitution such as:

```text
e²ˣ - 8eˣ + 20 = 0
u = eˣ
```

allowing the resulting equation to be solved as a polynomial before substituting back for `x`.

---

## Pattern Matching

Symbolic manipulation relies heavily on a custom pattern-matching system.

Patterns can contain:

* Numbers and known symbols
* Ordinary wildcards
* Sequence wildcards matching multiple terms
* Nested patterns
* Conditions restricting valid wildcard matches

For example, a rewrite rule can describe a general identity without knowing the actual expressions involved:

```text
a² - b² → (a - b)(a + b)
```

Here's a small subset of the simplification rewrite rules in `simplify()`:

```python
p, q, r = Wild('p'), Wild('q'), Wild('r')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)

SimplifyIdentities = IdentitySet(
   # Addition
   Identity(p + 0, p),
   Identity(u - u, internalize(0)),
   Identity(p + p, 2*p),
   Identity(p + u*p, p*(u + 1), {u: is_numeric}),
   Identity(u*p + v*p, (u + v)*p),
   
   # Multiplication
   Identity(1 * p, p),
   Identity(0 * p, internalize(0)),
   Identity(p / p, internalize(1), {p: lambda t: not eq_struct(t, internalize(0))}),

   ...
)
```

The matcher determines which subexpressions correspond to `a` and `b`, while ensuring that repeated wildcards receive consistent values. This is a big component of the matcher, explained below.

### Recursive structural matching

Expressions are represented as trees of operators and operands. The matcher recursively compares the structure of a pattern with the structure of a test expression.

For example:

```text
Pattern:
    x + y

Expression:
    3a + sin(b)

→ x = 3a
  y = sin(b)
```

Nested patterns are matched recursively, meaning rules can operate on arbitrarily deep expressions.

### Wildcard consistency

When a wildcard occurs multiple times, every occurrence must resolve to the same expression.

For example:

```text
Pattern:
    x + x

Expression:
    3a + 3a

→ x = 3a
```

but:

```text
Pattern:
    x + x

Expression:
    3a + 4a

→ no match
```

The matcher uses an internal function called `interrogate()` to cross check facts discovered during recursive matching. It is used to reject contradictory assignments.

### Commutative matching

Commutative operators such as addition and multiplication require special treatment because their operands do not have a fixed order.

For example:

```text
Pattern:
    x + 3

Expression:
    a + 3
```

and

```text
Pattern:
    x + 3

Expression:
    3 + a
```

should produce the same match.

The matcher therefore treats commutative expressions as multisets of terms rather than ordered sequences. It uses a frequency table to track which terms remain available and recursively explores possible assignments.

Pattern terms are ordered to reduce the search space, prioritising:

```text
constants → wildcards → structures → sequence wildcards
```

### Backtracking

When multiple terms could satisfy a wildcard, the matcher branches and explores each possible interpretation.

If a later part of the pattern produces a contradiction, that branch is discarded and another interpretation is tried.

This allows patterns containing multiple interacting wildcards to be matched without requiring the caller to specify which expression each wildcard should represent.

### Sequence wildcards

Sequence wildcards can match multiple terms within a commutative expression.

For example, a pattern

```python
p = Wild('p')
u = Wild('u', sequence=True)

an_amazing_pattern = Pattern(p + u)
```

Can match:

```python
>>> an_amazing_pattern.match(a + b + c)

→ {p=a, u = b+c}
→ {p=b, u = a+c}
→ {p=c, u = a+b}

# (The internal form is a bit messier than this though...)
```

That is, against an expression containing an arbitrary number of additive terms.

The matcher tracks the frequency of each term and determines which subset belongs to the sequence wildcard.

### Pattern optimisation

The matcher contains several optimisations to reduce unnecessary search:

* Pattern terms are reordered before commutative matching
* Already resolved wildcards are matched directly against the remaining frequency table
* Frequency tables avoid repeatedly scanning identical terms
* Contradictory wildcard assignments are rejected as soon as they are detected
* Sequence matching can match all remaining compatible terms when there is only one sequence wildcard

Which reduces a problem of many, MANY (looking at you Γ function) possibilities, to something more manageable!
