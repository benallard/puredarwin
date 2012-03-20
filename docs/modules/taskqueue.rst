Task-Queue
==========

The task queue is a collection of ``FiFo``\s. One for each Warrior
keeping track of the current tasks running for each Warrior.

Sub-process
-----------

MUXs
^^^^

One to direct the input to the right FIFO, another one to read the
right task from the right FIFO.

Sub-modules
-----------

FIFO
^^^^

It is a FIFO that can queue two tasks in the same cycle.

One synchronous sub-process that reacts on ``clk`` and ``rst_n``.

