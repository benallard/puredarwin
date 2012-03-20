RedCode Instruction Set
=======================

One feature of a processor running RedCode is that it has to implement
some OS functionnalities at the silicon level. I'm mainly speacking
here of the ``SPL`` instruction, and derivated ones. That
instruction queue a new task in the task queue. For an unix
developer, it is a :manpage:`fork(2)` at the silicon level. 

The typical example is:

.. code-block:: nasm

   SPL 0            ; execution starts here
   MOV 0, 1

Since the ``SPL`` points to itself, after one cycle the processes will
be like this:

.. code-block:: nasm

   SPL 0            ; second process is here
   MOV 0, 1         ; first process is here

After both of the processes have executed, the core will now look like:

.. code-block:: nasm

   SPL 0            ; third process is here
   MOV 0, 1         ; second process is here
   MOV 0, 1         ; first process is here

So this code evidently launches a series of imps, one after
another. It will keep on doing this until the imps have circled the
whole core and overwrite the ``SPL``. 
