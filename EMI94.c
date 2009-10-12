/************************************/
/*                                  */
/*            EMI94.c               */
/*                                  */
/* Execute MARS Instruction ala     */
/* ICWS'94 Draft Standard.          */
/*                                  */
/* Last Update: November 8, 1995    */
/*                                  */
/************************************/

/* This ANSI C function is the benchmark MARS instruction   */
/* interpreter for the ICWS'94 Draft Standard.              */


/* The design philosophy of this function is to mirror the  */
/* standard as closely as possible, illuminate the meaning  */
/* of the standard, and provide the definitive answers to   */
/* questions of the "well, does the standard mean this or   */
/* that?" variety.  Although other, different implemen-     */
/* tations are definitely possible and encouraged; those    */
/* implementations should produce the same results as this  */
/* one does.                                                */


/* The function returns the state of the system.  What the  */
/* main program does with this information is not defined   */
/* by the standard.                                         */

enum SystemState {
   UNDEFINED,
   SUCCESS
};


/* Any number of warriors may be executing in core at one   */
/* time, depending on the run-time variable set and how     */
/* many warriors have failed during execution.  For this    */
/* implementation, warriors are identified by the order in  */
/* which they were loaded into core.                        */

typedef unsigned int Warrior;


/* An Address in Core War can be any number from 0 to the   */
/* size of core minus one, relative to the current          */
/* instruction.  In this implementation, core is an array   */
/* of instructions; therefore any variable types which      */
/* contain an Address can be considered to be of type       */
/* unsigned int.  One caveat: for the purposes of this      */
/* standard, unsigned int must be considered to have no     */
/* upper limit.  Depending on the size of core, it may be   */
/* necessary to take precautions against overflow.          */

typedef unsigned int Address;


/* The FIFO task queues and supporting functions are not    */
/* presented.   The function Queue() attempts to add a task */
/* pointer to the back of the currently executing warrior's */
/* task queue.  No special actions are to be taken if       */
/* Queue() is unsuccessful, which it will be if the warrior */
/* has already reached the task limit (maximum allowable    */
/* number of tasks).                                        */

extern void Queue(
   Warrior  W,
   Address  TaskPointer
);


/* There is one support function used to limit the range of */
/* reading from Core and writing to Core relative to the    */
/* current instruction.  Behaviour is as expected (a small  */
/* core within Core) only if the limits are factors of the  */
/* size of Core.                                            */

static Address Fold(
   Address  pointer,    /* The pointer to fold into the desired range.  */
   Address  limit,      /* The range limit.                             */
   Address  M           /* The size of Core.                            */
) {
   Address  result;

   result = pointer % limit;
   if ( result > (limit/2) ) {
      result += M - limit;
   };
   return(result);
}


/* Instructions are the principle data type.  Core is an    */
/* array of instructions, and there are three instruction   */
/* registers used by the MARS executive.                    */

enum Opcode {
   DAT,
   MOV,
   ADD,
   SUB,
   MUL,
   DIV,
   MOD,
   JMP,
   JMZ,
   JMN,
   DJN,
   CMP, /* aka SEQ */
   SNE,
   SLT,
   SPL,
   NOP,
};

enum Modifier {
   A,
   B,
   AB,
   BA,
   F,
   X,
   I
};

enum Mode {
   IMMEDIATE,
   DIRECT,
   A_INDIRECT,
   B_INDIRECT,
   A_DECREMENT,
   B_DECREMENT,
   A_INCREMENT,
   B_INCREMENT,
};

typedef struct Instruction {
   enum Opcode    Opcode;
   enum Modifier  Modifier;
   enum Mode      AMode;
   Address        ANumber;
   enum Mode      BMode;
   Address        BNumber;
} Instruction;


/* The function is passed which warrior is currently        */
/* executing, the address of the warrior's current task's   */
/* current instruction, a pointer to the Core, the size of  */
/* the Core, and the read and write limits.  It returns the */
/* system's state after attempting instruction execution.   */

enum SystemState EMI94(

/* W indicates which warrior's code is executing.           */

   Warrior  W,

/* PC is the address of this warrior's current task's       */
/* current instruction.                                     */

   Address  PC,

/* Core is just an array of Instructions.  Core has been    */
/* initialized and the warriors have been loaded before     */
/* calling this function.                                   */

   Instruction Core[],

/* M is the size of Core.                                   */

   Address     M,

/* ReadLimit is the limitation on read distances.           */

   Address     ReadLimit,

/* WriteLimit is the limitation on write distances.         */

   Address     WriteLimit


) {


/* This MARS stores the currently executing instruction in  */
/* the instruction register IR.                             */

   Instruction IR;

/* This MARS stores the instruction referenced by the       */
/* A-operand in the instruction register IRA.               */

   Instruction IRA;

/* This MARS stores the instruction referenced by the       */
/* B-operand in the instruction Register IRB.               */

   Instruction IRB;

/* All four of the following pointers are PC-relative       */
/* (relative to the Program Counter).  Actual access of     */
/* core must add-in the Program Counter (mod core size).    */

/* The offset to the instruction referred to by the         */
/* A-operand for reading is Read Pointer A (RPA).           */

   Address     RPA;

/* The offset to the instruction referred to by the         */
/* A-operand for writing is Write Pointer A (WPA).          */

   Address     WPA;

/* The offset to the instruction referred to by the         */
/* B-operand for reading is Read Pointer B (RPB).           */

   Address     RPB;

/* The offset to the instruction referred to by the         */
/* A-operand for writing is Write Pointer B (WPB).          */

   Address     WPB;

/* Post-increment operands need to keep track of which      */
/* instruction to increment.                                */

   Address     PIP;

/* Before execution begins, the current instruction is      */
/* copied into the Instruction Register.                    */

   IR = Core[PC];


/* Next, the A-operand is completely evaluated.             */

/* For instructions with an Immediate A-mode, the Pointer A */
/* points to the source of the current instruction.         */

   if (IR.AMode == IMMEDIATE) {
      RPA = WPA = 0;
   } else {

/* For instructions with a Direct A-mode, the Pointer A     */
/* points to the instruction IR.ANumber away, relative to   */
/* the Program Counter.                                     */
/* Note that implementing Core as an array necessitates     */
/* doing all Address arithmetic modulus the size of Core.   */

      RPA = Fold(IR.ANumber, ReadLimit, M);
      WPA = Fold(IR.ANumber, WriteLimit, M);

/* For instructions with A-indirection in the A-operand     */
/* (A-number Indirect, A-number Predecrement,               */
/* and A-number Postincrement A-modes):                     */

      if (IR.AMode == A_INDIRECT
          || IR.AMode == A_DECREMENT
          || IR.AMode == A_INCREMENT) {

/* For instructions with Predecrement A-mode, the A-Field   */
/* of the instruction in Core currently pointed to by the   */
/* Pointer A is decremented (M - 1 is added).               */

         if (IR.AMode == A_DECREMENT) {
            Core[((PC + WPA) % M)].ANumber =
               (Core[((PC + WPA) % M)].ANumber + M - 1) % M;
         };

/* For instructions with Postincrement A-mode, the A-Field  */
/* of the instruction in Core currently pointed to by the   */
/* Pointer A will be incremented.                           */

         if (IR.AMode == A_INCREMENT) {
            PIP = (PC + WPA) % M;
         };

/* For instructions with A-indirection in the A-operand,    */
/* Pointer A ultimately points to the instruction           */
/* Core[((PC + PCA) % M)].ANumber away, relative to the     */
/* instruction pointed to by Pointer A.                     */

         RPA = Fold(
            (RPA + Core[((PC + RPA) % M)].ANumber), ReadLimit, M
         );
         WPA = Fold(
            (WPA + Core[((PC + WPA) % M)].ANumber), WriteLimit, M
         );

      };

/* For instructions with B-indirection in the A-operand     */
/* (B-number Indirect, B-number Predecrement,               */
/* and B-number Postincrement A-modes):                     */

      if (IR.AMode == B_INDIRECT
          || IR.AMode == B_DECREMENT
          || IR.AMode == B_INCREMENT) {

/* For instructions with Predecrement A-mode, the B-Field   */
/* of the instruction in Core currently pointed to by the   */
/* Pointer A is decremented (M - 1 is added).               */

         if (IR.AMode == DECREMENT) {
            Core[((PC + WPA) % M)].BNumber =
               (Core[((PC + WPA) % M)].BNumber + M - 1) % M;
         };

/* For instructions with Postincrement A-mode, the B-Field  */
/* of the instruction in Core currently pointed to by the   */
/* Pointer A will be incremented.                           */

         if (IR.AMode == INCREMENT) {
            PIP = (PC + WPA) % M;
         };

/* For instructions with B-indirection in the A-operand,    */
/* Pointer A ultimately points to the instruction           */
/* Core[((PC + PCA) % M)].BNumber away, relative to the     */
/* instruction pointed to by Pointer A.                     */

         RPA = Fold(
            (RPA + Core[((PC + RPA) % M)].BNumber), ReadLimit, M
         );
         WPA = Fold(
            (WPA + Core[((PC + WPA) % M)].BNumber), WriteLimit, M
         );

      };
   };

/* The Instruction Register A is a copy of the instruction  */
/* pointed to by Pointer A.                                 */

   IRA = Core[((PC + RPA) % M)];

/* If the A-mode was post-increment, now is the time to     */
/* increment the instruction in core.                       */

   if (IR.AMode == A_INCREMENT) {
           Core[PIP].ANumber = (Core[PIP].ANumber + 1) % M;
           }
   else if (IR.AMode == B_INCREMENT) {
           Core[PIP].BNumber = (Core[PIP].BNumber + 1) % M;
           };

/* The Pointer B and the Instruction Register B are         */
/* evaluated in the same manner as their A counterparts.    */

   if (IR.BMode == IMMEDIATE) {
      RPB = WPB = 0;
   } else {
      RPB = Fold(IR.BNumber, ReadLimit, M);
      WPB = Fold(IR.BNumber, WriteLimit, M);
      if (IR.BMode == A_INDIRECT
          || IR.BMode == A_DECREMENT
          || IR.BMode == A_INCREMENT) {
         if (IR.BMode == A_DECREMENT) {
            Core[((PC + WPB) % M)].ANumber =
               (Core[((PC + WPB) % M)].ANumber + M - 1) % M
            ;
         } else if (IR.BMode == A_INCREMENT) {
            PIP = (PC + WPB) % M;
         };
         RPB = Fold(
            (RPB + Core[((PC + RPB) % M)].ANumber), ReadLimit, M
         );
         WPB = Fold(
            (WPB + Core[((PC + WPB) % M)].ANumber), WriteLimit, M
         );
      };
      if (IR.BMode == B_INDIRECT
          || IR.BMode == B_DECREMENT
          || IR.BMode == B_INCREMENT) {
         if (IR.BMode == B_DECREMENT) {
            Core[((PC + WPB) % M)].BNumber =
               (Core[((PC + WPB) % M)].BNumber + M - 1) % M
            ;
         } else if (IR.BMode == B_INCREMENT) {
            PIP = (PC + WPB) % M;
         };
         RPB = Fold(
            (RPB + Core[((PC + RPB) % M)].BNumber), ReadLimit, M
         );
         WPB = Fold(
            (WPB + Core[((PC + WPB) % M)].BNumber), WriteLimit, M
         );
      };
   };
   IRB = Core[((PC + RPB) % M)];

   if (IR.BMode == A_INCREMENT) {
           Core[PIP].ANumber = (Core[PIP].ANumber + 1) % M;
           }
   else if (IR.BMode == INCREMENT) {
           Core[PIP].BNumber = (Core[PIP].BNumber + 1) % M;
           };

/* Execution of the instruction can now proceed.            */

   switch (IR.Opcode) {

/* Instructions with a DAT opcode have no further function. */
/* The current task's Program Counter is not updated and is */
/* not returned to the task queue, effectively removing the */
/* task.                                                    */

   case DAT: noqueue:
      break;


/* MOV replaces the B-target with the A-value and queues    */
/* the next instruction.                                    */

   case MOV:
      switch (IR.Modifier) {

/* Replaces A-number with A-number.                         */

      case A:
         Core[((PC + WPB) % M)].ANumber = IRA.ANumber;
         break;

/* Replaces B-number with B-number.                         */

      case B:
         Core[((PC + WPB) % M)].BNumber = IRA.BNumber;
         break;

/* Replaces B-number with A-number.                         */

      case AB:
         Core[((PC + WPB) % M)].BNumber = IRA.ANumber;
         break;

/* Replaces A-number with B-number.                         */

      case BA:
         Core[((PC + WPB) % M)].ANumber = IRA.BNumber;
         break;

/* Replaces A-number with A-number and B-number with        */
/* B-number.                                                */

      case F:
         Core[((PC + WPB) % M)].ANumber = IRA.ANumber;
         Core[((PC + WPB) % M)].BNumber = IRA.BNumber;
         break;

/* Replaces B-number with A-number and A-number with        */
/* B-number.                                                */

      case X:
         Core[((PC + WPB) % M)].BNumber = IRA.ANumber;
         Core[((PC + WPB) % M)].ANumber = IRA.BNumber;
         break;

/* Copies entire instruction.                               */

      case I:
         Core[((PC + WPB) % M)] = IRA;
         break;

      default:
         return(UNDEFINED);
         break;
      };

/* Queue up next instruction.                               */
      Queue(W, ((PC + 1) % M));
      break;

/* Arithmetic instructions replace the B-target with the    */
/* "op" of the A-value and B-value, and queue the next      */
/* instruction.  "op" can be the sum, the difference, or    */
/* the product.                                             */

#define ARITH(op) \
      switch (IR.Modifier) { \
      case A: \
         Core[((PC + WPB) % M)].ANumber = \
            (IRB.ANumber op IRA.ANumber) % M \
         ; \
         break; \
      case B: \
         Core[((PC + WPB) % M)].BNumber = \
            (IRB.BNumber op IRA.BNumber) % M \
         ; \
         break; \
      case AB: \
         Core[((PC + WPB) % M)].BNumber = \
            (IRB.ANumber op IRA.BNumber) % M \
         ; \
         break; \
      case BA: \
         Core[((PC + WPB) % M)].ANumber = \
            (IRB.BNumber op IRA.ANumber) % M \
         ; \
         break; \
      case F: \
      case I: \
         Core[((PC + WPB) % M)].ANumber = \
            (IRB.ANumber op IRA.ANumber) % M \
         ; \
         Core[((PC + WPB) % M)].BNumber = \
            (IRB.BNumber op IRA.BNumber) % M \
         ; \
         break; \
      case X: \
         Core[((PC + WPB) % M)].BNumber = \
            (IRB.ANumber op IRA.BNumber) % M \
         ; \
         Core[((PC + WPB) % M)].ANumber = \
            (IRB.BNumber op IRA.ANumber) % M \
         ; \
         break; \
      default: \
         return(UNDEFINED); \
         break; \
      }; \
      Queue(W, ((PC + 1) % M)); \
      break;

   case ADD: ARITH(+)
   case SUB: ARITH(+ M -)
   case MUL: ARITH(*)

/* DIV and MOD replace the B-target with the integral       */
/* quotient (for DIV) or remainder (for MOD) of the B-value */
/* by the A-value, and queues the next instruction.         */
/* Process is removed from task queue if A-value is zero.   */

#define ARITH_DIV(op) \
      switch (IR.Modifier) { \
      case A: \
         if (IRA.ANumber != 0) \
            Core[((PC + WPB) % M)].ANumber = IRB.ANumber op IRA.ANumber; \
         break; \
      case B: \
         if (IRA.BNumber != 0) \
            Core[((PC + WPB) % M)].BNumber = IRB.BNumber op IRA.BNumber; \
         else goto noqueue; \
         break; \
      case AB: \
         if (IRA.ANumber != 0) \
            Core[((PC + WPB) % M)].BNumber = IRB.BNumber op IRA.ANumber; \
         else goto noqueue; \
         break; \
      case BA: \
         if (IRA.BNumber != 0) \
            Core[((PC + WPB) % M)].ANumber = IRB.ANumber op IRA.BNumber; \
         else goto noqueue; \
         break; \
      case F: \
      case I: \
         if (IRA.ANumber != 0) \
            Core[((PC + WPB) % M)].ANumber = IRB.ANumber op IRA.ANumber; \
         if (IRA.BNumber != 0) \
            Core[((PC + WPB) % M)].BNumber = IRB.BNumber op IRA.BNumber; \
         if ((IRA.ANumber == 0) || (IRA.BNumber == 0)) \
            goto noqueue; \
         break; \
      case X: \
         if (IRA.ANumber != 0) \
            Core[((PC + WPB) % M)].BNumber = IRB.BNumber op IRA.ANumber; \
         if (IRA.BNumber != 0) \
            Core[((PC + WPB) % M)].ANumber = IRB.ANumber op IRA.BNumber; \
         if ((IRA.ANumber == 0) || (IRA.BNumber == 0)) \
            goto noqueue; \
         break; \
      default: \
         return(UNDEFINED); \
         break; \
      }; \
      Queue(W, ((PC + 1) % M)); \
      break;

   case DIV: ARITH_DIV(/)
   case MOD: ARITH_DIV(%)

/* JMP queues the sum of the Program Counter and the        */
/* A-pointer.                                               */

   case JMP:
      Queue(W, RPA);
      break;


/* JMZ queues the sum of the Program Counter and Pointer A  */
/* if the B-value is zero.  Otherwise, it queues the next   */
/* instruction.                                             */

   case JMZ:
      switch (IR.Modifier) {
      case A:
      case BA:
         if (IRB.ANumber == 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
      case AB:
         if (IRB.BNumber == 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
      case X:
      case I:
         if ( (IRB.ANumber == 0) && (IRB.BNumber == 0) ) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* JMN queues the sum of the Program Counter and Pointer A  */
/* if the B-value is not zero.  Otherwise, it queues the    */
/* next instruction.                                        */

   case JMN:
      switch (IR.Modifier) {
      case A:
      case BA:
         if (IRB.ANumber != 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
      case AB:
         if (IRB.BNumber != 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
      case X:
      case I:
         if ( (IRB.ANumber != 0) || (IRB.BNumber != 0) ) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* DJN (Decrement Jump if Not zero) decrements the B-value  */
/* and the B-target, then tests if the B-value is zero.  If */
/* the result is not zero, the sum of the Program Counter   */
/* and Pointer A is queued.  Otherwise, the next            */
/* instruction is queued.                                   */

   case DJN:
      switch (IR.Modifier) {
      case A:
      case BA:
         Core[((PC + WPB) % M)].ANumber =
            (Core[((PC + WPB) % M)].ANumber + M - 1) % M
         ;
         IRB.ANumber -= 1;
         if (IRB.ANumber != 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
      case AB:
         Core[((PC + WPB) % M)].BNumber =
            (Core[((PC + WPB) % M)].BNumber + M - 1) % M
         ;
         IRB.BNumber -= 1;
         if (IRB.BNumber != 0) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
      case X:
      case I:
         Core[((PC + WPB) % M)].ANumber =
            (Core[((PC + WPB) % M)].ANumber + M - 1) % M
         ;
         IRB.ANumber -= 1;
         Core[((PC + WPB) % M)].BNumber =
            (Core[((PC + WPB) % M)].BNumber + M - 1) % M
         ;
         IRB.BNumber -= 1;
         if ( (IRB.ANumber != 0) || (IRB.BNumber != 0) ) {
            Queue(W, RPA);
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* SEQ/CMP compares the A-value and the B-value. If there   */
/* are no differences, then the instruction after the next  */
/* instruction is queued.  Otherwise, the next instrution   */
/* is queued.                                               */

   case CMP:
      switch (IR.Modifier) {
      case A:
         if (IRA.ANumber == IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
         if (IRA.BNumber == IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case AB:
         if (IRA.ANumber == IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case BA:
         if (IRA.BNumber == IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
         if ( (IRA.ANumber == IRB.ANumber) &&
              (IRA.BNumber == IRB.BNumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case X:
         if ( (IRA.ANumber == IRB.BNumber) &&
              (IRA.BNumber == IRB.ANumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case I:
         if ( (IRA.Opcode == IRB.Opcode) &&
              (IRA.Modifier == IRB.Modifier) &&
              (IRA.AMode == IRB.AMode) &&
              (IRA.ANumber == IRB.ANumber) &&
              (IRA.BMode == IRB.BMode) &&
              (IRA.BNumber == IRB.BNumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* SNE compares the A-value and the B-value. If there       */
/* is a difference, then the instruction after the next     */
/* instruction is queued.  Otherwise, the next instrution   */
/* is queued.                                               */

   case SNE:
      switch (IR.Modifier) {
      case A:
         if (IRA.ANumber != IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
         if (IRA.BNumber != IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case AB:
         if (IRA.ANumber != IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case BA:
         if (IRA.BNumber != IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
         if ( (IRA.ANumber != IRB.ANumber) ||
              (IRA.BNumber != IRB.BNumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case X:
         if ( (IRA.ANumber != IRB.BNumber) ||
              (IRA.BNumber != IRB.ANumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case I:
         if ( (IRA.Opcode != IRB.Opcode) ||
              (IRA.Modifier != IRB.Modifier) ||
              (IRA.AMode != IRB.AMode) ||
              (IRA.ANumber != IRB.ANumber) ||
              (IRA.BMode != IRB.BMode) ||
              (IRA.BNumber != IRB.BNumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* SLT (Skip if Less Than) queues the instruction after the */
/* next instruction if A-value is less than B-value.        */
/* Otherwise, the next instruction is queued.  Note that no */
/* value is less than zero because only positive values can */
/* be represented in core.                                  */

   case SLT :
      switch (IR.Modifier) {
      case A:
         if (IRA.ANumber < IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case B:
         if (IRA.BNumber < IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case AB:
         if (IRA.ANumber < IRB.BNumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case BA:
         if (IRA.BNumber < IRB.ANumber) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case F:
      case I:
         if ( (IRA.ANumber < IRB.ANumber) &&
              (IRA.BNumber < IRB.BNumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      case X:
         if ( (IRA.ANumber < IRB.BNumber) &&
              (IRA.BNumber < IRB.ANumber)
         ) {
            Queue(W, ((PC + 2) % M));
         } else {
            Queue(W, ((PC + 1) % M));
         };
         break;
      default:
         return(UNDEFINED);
         break;
      };
      break;


/* SPL queues the next instruction and also queues the sum  */
/* of the Program Counter and Pointer A.                    */

   case SPL:
      Queue(W, ((PC + 1) % M));
      Queue(W, RPA);
      break;


/* NOP queues the next instruction.                         */

   case NOP:
      Queue(W, ((PC + 1) % M));
      break;


/* Any other opcode is undefined.                           */

   default:
      return(UNDEFINED);
   };


/* We are finished.                                         */

   return(SUCCESS);
}
