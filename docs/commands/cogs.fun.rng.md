# cogs.fun.rng

Commands used for random number generation.

## `choice`

**Aliases:** `choose, c`

**Arguments:** `choices`

Choose from various choices. Choices are separated with spaces.

Multi-word choices should be enclosed in "quotes like this".

## `coin`

**Aliases:** `cflip, coinflip`

Flip a coin.

## `rng`

**Aliases:** `randint`

**Arguments:** `start end`

Random number generator.

* `start` - The lowest number that can be generated.
* `end` - The highest number that can be generated.

## `roll`

**Aliases:** `r`

**Arguments:** `expressions`

Roll some dice, using D&D syntax.

**Example usage**

* `roll 5d6+2` - Roll five six sided dice with a modifier of 2.
* `roll 1d20 2d8` - Roll one twenty sided die, and two eight sided dice.

Roll outcomes are always sorted in descending order.