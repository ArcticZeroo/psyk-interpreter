# Psyk Interpreter

An interpreter for the ficticious "psyk" language as featured in [MSU's CSE 450](https://www.cse.msu.edu/~cse450/) class.
Unfortunately I wasn't able to find the original document for the language's
source.

Tests were written by Dr. Rupp at MSU, with a few local fixes for those which were broken.

[program.psyk](program.psyk) contains the solutions to Day 1 of Advent of Code 2020.

## Usage

1. Write a `.psyk` file
2. Run `main.py <path to the file>`
3. ???
4. Profit, I guess

## Interesting Bits

- The type system and typechecking (fairly basic but it ended up working pretty well)
- Scalars which automatically resolve to memory or array-indexed memory
- Reclaiming scalars as they are disposed

## Strange bits

- Don't try to understand how arrays are stored in memory. It's not pretty.
- Instead of just installing rply, we were given a copy of rply to put in our project.