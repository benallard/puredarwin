ToDo
====

Loader
------

Description of the trouble
^^^^^^^^^^^^^^^^^^^^^^^^^^

My main trouble at the moment is to find a way to Load the programms
inside the Virtual Machine. The MARS had been designed as a **closed
system**, with absolutely no input, and one output, namely the result
of the *fight*.

That means that my current question doesn't get answered by design: 

   How to get the programs in the Core of ``puredarwin`` MARS ?

I made a first try with an RS232 Module (self-designed) where the goal
would be to load the Programs via a serial line ... I'm not entirely
satisfied with that solution. Actually, I'm not sure that it would be
practical.

Solution
^^^^^^^^

Do not use any loader
~~~~~~~~~~~~~~~~~~~~~

For the moment, I would advice using ``rev 548b16a67881`` and
`traceProc.py`_ as a main to simulate. This testModule also has a
correct simulation implementation for the Queue and the Core. This
shouldn't be a trouble to test a program on this MARS.

.. _traceProc.py: http://bitbucket.org/benallard/puredarwin/src/tip/traceProc.py

Quality of this solution
~~~~~~~~~~~~~~~~~~~~~~~~

This solution makes some sense as the MyHDL module are actually not
*directly* intended for synthesis. So, using simulation *tricks*
in order to *simulate* is not seen as a betrayal.
