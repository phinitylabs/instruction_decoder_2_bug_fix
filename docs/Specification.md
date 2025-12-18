Instruction decoder is a fully combinational instruction-decoding block that receives a 5-bit opcode, a condition-code bit, and an instruction-enable signal, and produces all internal control signals for the microcode sequencer, stack subsystem, register subsystem, arithmetic datapath selectors, and program-counter steering logic.

The module outputs a valid set of outputs only when the identification value is 2.

When the module does not receive a valid identification code , the following behaviour is exhibited :

--> The output of the adder is 0. The carry input to the adder is discarded.

--> Stack is untouched.

--> The output of full adder is disabled.

--> The auxiliary register is disabled.

--> The auxiliary register mux selects the external data input.

--> The full adder value is held in the program counter.

--> The stack submodule receives the program counter value.

--> The result register holds its current value.

The list of valid instructions are as follows :

**1. Instruction Disable** 
-----------------------
Pattern: 0100011

--> The output of adder is 0. The carry input to the adder is discarded.

--> Stack is untouched.

--> The output of full adder is made available to result register.

--> The auxiliary register is disabled

--> The auxiliary register mux selects the external data input.

--> The full adder value is held in the program counter.

--> The stack submodule receives the program counter value.

--> The result register holds its current value.

Instruction 0 — Fetch PC to R
--------------------------------
Pattern: 01000x0

--> The program counter is routed to the output of the full adder. The carry-input of the adder is not considered.

--> The program counter value is selected for getting incremented.

--> Stack is untouched.

--> The auxiliary register mux selects the fedback full adder output. 

--> The auxiliary register is activated to receive data from auxiliary register mux.

--> The stack submodule receives program counter value.


Instruction 1 — FETCH R + D to R
------------------------------------
Pattern: 01001x0

--> The output of the adder is the summation of the auxiliary register and external data input. The carry-input of the adder is considered.

--> The program counter value is selected for getting incremented.

--> Stack is untouched.

--> The auxiliary register is enabled to receive data from auxiliary register mux.

--> The output of the full adder is routed through result register to the auxiliary register mux.

--> The stack submodule receives program counter value.


Instruction 2 — Load R
------------------------------
Pattern: 01010x0

--> The program counter is routed to the output of the full adder. The carry-input of the adder is not considered.

--> The program counter value is selected for getting incremented.

--> Stack is untouched.

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The result register holds its current value.

--> The stack submodule receives program counter value.


Instruction 3 — PUSH PC
-------------------------
Pattern: 01011x0

--> The program counter is routed to the output of the full adder. The carry-input of the adder is not considered.

--> The program counter value is selected for getting incremented.

--> The value of the program counter is selected to be pushed into the stack location given by the stack pointer

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The result register holds its current value.


I/O ports :
----------
## Input ports :
- `id` - 3-bit value to identify an instruction decoder instance.
- `instr_in` - 5-bit opcode indicating the operation to be performed
- `cc_in` - 1-bit code to determine whether a given instruction is unconditional or conditional. Its value is dont care for unconditional instructions.
- `instr_en` - 1-bit active low signal to enable the execution of an instruction

## Output ports:
- `cen` - 1-bit active high signal to enable the carry-input to full look-ahead adder
- `rst` - 1-bit active high reset signal of stack pointer to initialize it to location 0 of stack RAM.
- `oen` - 1-bit active high signal to enable the tristate buffer of full look-ahead adder
- `inc` - 1-bit active high signal to enable the increment of the pc incrementer submodule
- `rsel` - Signal to select the data at the auxiliary register mux submodule. It is used in combination with active low register enable signal to perform the selection. A value of 1 indicates to select full look-ahead adder output fedback from result register. A value of 0 indicates to select external data input.
- `rce` - 1-bit active high signal to enable the auxiliary register submodule to transfer its input to output. It is used in combination with active low register enable signal to perform the operation.
- `pc_mux_sel` - Signal to select the data at the pc submodule. A value of 1 is used for selecting the fedback program counter module data. A value of 0 is used for selecting the output of full look-ahead adder output.
- `a_mux_sel` - 2-bit signal to select the value of A-operand to full look-ahead adder. A value of 0 selects the external data input ; A value of 1 selects the output of auxiliary register ; A value of 2 selects constant 0.
- `b_mux_sel` - 2-bit signal to select the value of B-operand to full look-ahead adder. A value of 0 selects the program counter submodule's data ; A value of 1 selects output of lifo stack submodule ; A value of 2 selects constant 0 ; A value of 3 selects the output of auxiliary register submodule.
- `push` - 1-bit active high signal to perform increment of stack pointer
- `pop` - 1-bit active high signal to perform decrement of stack pointer
- `src_sel` - Signal to select the data at the lifo stack submodule. A value of 1 selects the external data input. A value of 0 selects the output of program counter submodule.
- `stack_we` - 1-bit active high signal to write a selected data from the stack multiplexer submodule to write into a stack ram location
- `stack_re` - 1-bit active high signal to read data from a selected stack ram location.
- `out_ce` - 1-bit active high signal to enable the result register latch.

## Hints:
1. The 5-bit opcode , cc_in , instr_en bits have to be considered in the case expression to generate control signals. Considering any one of these alone to generate control signals is wrong.
2. There will be a increment of stack pointer during a stack write.
3. When the program counter is selected for increment operation , the program counter mux select will have a value of 1 , unless explicitly stated.

