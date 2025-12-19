### **Instruction Decoder Specification**

The instruction decoder is a fully combinational instruction-decoding block. It receives a 5-bit opcode, a condition-code bit, and an instruction-enable signal. It produces all internal control signals for the microcode sequencer, stack subsystem, register subsystem, arithmetic datapath selectors, and program-counter steering logic.

The module outputs a valid set of signals only when the identification value (`id`) is 2.

#### **Default Behavior (Invalid ID)**

When the module does not receive a valid identification code, the following behavior is exhibited:

* The output of the adder is 0. The carry input to the adder is discarded.
* The stack is untouched.
* The output of the full look-ahead adder is disabled.
* The auxiliary register is disabled.
* The auxiliary register mux selects the external data input.
* The full adder value is held in the program counter.
* The stack submodule receives the program counter value.
* The result register holds its current value.

---

### **Valid Instructions**

**1. Instruction Disable**

* **Pattern:** `0100011`
* The output of the adder is 0. The carry input to the adder is discarded.
* The stack is untouched.
* The output of the full adder is made available to the result register.
* The auxiliary register is disabled.
* The auxiliary register mux selects the external data input.
* The full adder value is held in the program counter.
* The stack submodule receives the program counter value.
* The result register holds its current value.

**Instruction 0 — Fetch PC to R**

* **Pattern:** `01000x0`
* The program counter is routed to the output of the full adder. The carry input of the adder is not considered.
* The program counter value is selected to be incremented.
* The stack is untouched.
* The auxiliary register mux selects the fed-back full adder output.
* The auxiliary register is activated to receive data from the auxiliary register mux.
* The stack submodule receives the program counter value.

**Instruction 1 — Fetch R + D to R**

* **Pattern:** `01001x0`
* The output of the adder is the summation of the auxiliary register and the external data input. The carry input of the adder is considered.
* The program counter value is selected to be incremented.
* The stack is untouched.
* The auxiliary register is enabled to receive data from the auxiliary register mux.
* The output of the full adder is routed through the result register to the auxiliary register mux.
* The stack submodule receives the program counter value.

**Instruction 2 — Load R**

* **Pattern:** `01010x0`
* The program counter is routed to the output of the full adder. The carry input of the adder is not considered.
* The program counter value is selected to be incremented.
* The stack is untouched.
* The auxiliary register mux selects the external data input.
* The auxiliary register is activated.
* The result register holds its current value.
* The stack submodule receives the program counter value.

**Instruction 3 — Push PC**

* **Pattern:** `01011x0`
* The program counter is routed to the output of the full adder. The carry input of the adder is not considered.
* The program counter value is selected to be incremented.
* The value of the program counter is selected to be pushed into the stack location determined by the stack pointer.
* The auxiliary register mux selects the external data input.
* The auxiliary register is activated.
* The result register holds its current value.

---

### **I/O Ports**

#### **Input Ports**

* `id` : 3-bit value to identify an instruction decoder instance.
* `instr_in` : 5-bit opcode indicating the operation to be performed.
* `cc_in` : 1-bit code to determine whether a given instruction is unconditional or conditional. Its value is "don't care" for unconditional instructions.
* `instr_en` : 1-bit active-low signal to enable the execution of an instruction.

#### **Output Ports**

* `cen` : 1-bit active-high signal to enable the carry input to the full look-ahead adder.
* `rst` : 1-bit active-high reset signal for the stack pointer, initializing it to location 0 of the stack RAM.
* `oen` : 1-bit active-high signal to enable the tristate buffer of the full look-ahead adder.
* `inc` : 1-bit active-high signal to enable the increment of the PC incrementer submodule.
* `rsel` : Signal to select the data at the auxiliary register mux submodule. It is used in combination with the active-low register enable signal to perform the selection. A value of `1` selects the full look-ahead adder output fed back from the result register. A value of `0` selects the external data input.
* `rce` : 1-bit active-high signal to enable the auxiliary register submodule to transfer its input to its output. It is used in combination with the active-low register enable signal to perform the operation.
* `pc_mux_sel` : Signal to select the data at the PC submodule. A value of `1` selects the fed-back program counter module data. A value of `0` selects the output of the full look-ahead adder.
* `a_mux_sel` : 2-bit signal to select the value of the A-operand for the full look-ahead adder.
* `0`: Selects the external data input.
* `1`: Selects the output of the auxiliary register.
* `2`: Selects constant 0.


* `b_mux_sel` : 2-bit signal to select the value of the B-operand for the full look-ahead adder.
* `0`: Selects the program counter submodule's data.
* `1`: Selects the output of the LIFO stack submodule.
* `2`: Selects constant 0.
* `3`: Selects the output of the auxiliary register submodule.


* `push` : 1-bit active-high signal to perform an increment of the stack pointer.
* `pop` : 1-bit active-high signal to perform a decrement of the stack pointer.
* `src_sel` : Signal to select the data at the LIFO stack submodule. A value of `1` selects the external data input. A value of `0` selects the output of the program counter submodule.
* `stack_we` : 1-bit active-high signal to write selected data from the stack multiplexer submodule into a stack RAM location.
* `stack_re` : 1-bit active-high signal to read data from a selected stack RAM location.
* `out_ce` : 1-bit active-high signal to enable the result register latch.

---

### **Hints**

1. The 5-bit `instr_in` (opcode), `cc_in`, and `instr_en` bits must be considered in the case expression to generate control signals. Considering any one of these alone to generate control signals is incorrect.
2. There will be an increment of the stack pointer during a stack write.
3. When the program counter is selected for an increment operation, `pc_mux_sel` will have a value of `1` unless explicitly stated otherwise.
4. Review the symmetry between the Global Disable and the Local Disable. While they operate at different hierarchy levels, their effect on the Program Counter's control interface (not just the data incrementer) must be identical.