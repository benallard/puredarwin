Introduction
============

**puredarwin** is a pure Hardware Implementation of CoreWar.

Darwin ???
----------

:doc:`darwin` is the predecessor of the CoreWar *game*.

CoreWar ?
---------

( `corewar.co.uk`_ | `corewar.info`_ | `corewars.org`_ )

.. _corewar.co.uk: http://corewar.co.uk/
.. _corewar.info: http://www.corewar.info/
.. _corewars.org: http://www.corewars.org

In Corewar, programs are fighting each other in the same memory space,
the goal is to kill the other programs by making them execute illegal
instructions.

Programs are written in assembly, :doc:`redcode` is the name of the
assembly used.

pure Hardware Implementation ?
------------------------------

Our world is made of two kind of people, the one that write software,
and the one that design hardware. In the past, the former were slaved
by the later, this is less and less true. Anyway, I made my study in
the hardware field, and I'm now spending my day at $paying_job writing
software.

Our goal here is to achieve a silicon running CoreWar game engine.

Actually, when I speak about an implementation of CoreWar, I am truly
speaking about an implementation of MARS (**M**\emory **A**\rray
**R**\edcode **S**\imulator) ... even if my implementation is everything
but a simulator !

This implementation is split into :doc:`modules`.

The code is written in an unexpected language when in comes to
Hardware Design, I choose Python to help me with that task. Bare
Python is of course not able to describe Hardware Modules, that's
where MyHDL comes into the scene. MyHDL
advertise itself as being able to output VHDL as well as Verilog, I'm
curious of the result. Anyway, I don't own any FPGA, ASIC or even
Lattice right now, so gtkwave will be my best guess when it comes to
simulation for some time.

.. _MyHDL: http://www.myhdl.org/
