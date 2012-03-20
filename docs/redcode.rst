RedCode
=======

RedCode is the assembly language used to program the MARS Virtual
Machine.

We will regard here only the the details we need to look at as
hardware designer. The rest is left to the dozen of good tutorials you
will find on the Internet. If you don't know where to start, Google_
might be your friend that time. That said, don't expect any easy talk
in there.

.. _Google: http://www.google.com/search?q=redcode+tutorial+corewar+mars+assembly+core

They are different version of the standard defining the RedCode
language, ranging from '86, '88 and extended ('94 has never been
confirmed as a standard). We will try to implement most of the
extended feature, while keeping compatibility with the previous
standards.

Instruction Set
---------------

See :doc:`redcode/ISA`.

Address Mode
------------

First thing to kno. Is that memory access inside the MARS are relative
to the current instruction pointer (noted IP here below). As seen from
a program, all addresses are relative to the one of the currently
executed instruction.

To keep a low memory footprint, RedCode has 5 address mode:

.. table:: RedCode address modes

   =========================================== ==================== ========================== ============ ============
    Name                                        Relative operation   Absolute operation         A-Notation   B-Notation 
   =========================================== ==================== ========================== ============ ============
    Immediate Memory Addressing                 0                    IP                         ``#``        ``#``
    Direct Memory Addressing                    *x*                  IP + *x*                   ``$``        ``$``
    Indirect Memory Adressing                   [IP + *x*\]          IP + *x* + [IP + *x*\]     ``*``        ``@``
    Post Increment Indirect Memory Addressing   [IP + *x*\]++        IP + *x* + [IP + *x*]++    ``{``        ``<``
    Pre Decrement Indirect Memory Addressing    --[IP + *x*\]        IP + *x* + --[IP + *x*/]   ``}``        ``>``
   =========================================== ==================== ========================== ============ ============

The last three one actually count double as we can address the first
operand or the second operand on those addresses in Memory.

Out of those one, the last two one are pretty unusual, even for an
experienced assembly programmer, just because of the fact that those
Memory addressing modes *modify* the memory content instead of just
pointing to it.

Examples
--------

 * :doc:`redcode/IMP`
 * :doc:`redcode/Dwarf`
 * :doc:`redcode/Gemini`
