import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

# ============================================================
# Helper to check outputs against expected values
# ============================================================

async def check_outputs(dut, exp, label=""):
    await Timer(1, units="ns")
    for signal, expected_val in exp.items():
        actual_val = int(getattr(dut, signal).value)
        assert actual_val == expected_val, (
            f"{label}: {signal} expected {expected_val}, got {actual_val}"
        )

async def run_instr(dut, instr, cc, en, expected, label):
    dut.id.value = 0b010
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en
    await Timer(2, units="ns")
    await check_outputs(dut, expected, label)

# ============================================================
# Expected Output Dictionaries
# ============================================================

EXP_INVALID_ID = dict(
    rst=0, out_ce=0, rsel=0, rce=0, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=2,
    oen=0, pc_mux_sel=0, inc=0,
    src_sel=0, push=0, stack_we=0
)

EXP_DEFAULT = EXP_INVALID_ID.copy()

EXP_INSTR_DISABLE = dict(
    rst=0, out_ce=0, rsel=0, rce=0, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=2,
    oen=1, pc_mux_sel=0, inc=0,
    src_sel=0, push=0, stack_we=0
)

EXP_FETCH_PC = dict(
    rst=0, out_ce=1, rsel=1, rce=1, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=0,
    oen=1, pc_mux_sel=1, inc=1,
    src_sel=0, push=0, stack_we=0
)

EXP_FETCH_R_D = dict(
    rst=0, out_ce=1, rsel=1, rce=1, cen=1,
    stack_re=0, pop=0,
    a_mux_sel=0, b_mux_sel=3,
    oen=1, pc_mux_sel=1, inc=1,
    src_sel=0, push=0, stack_we=0
)

EXP_LOAD_R = dict(
    rst=0, out_ce=0, rsel=0, rce=1, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=0,
    oen=1, pc_mux_sel=1, inc=1,
    src_sel=0, push=0, stack_we=0
)

EXP_PUSH_PC = dict(
    rst=0, out_ce=0, rsel=0, rce=1, cen=0,
    stack_re=0, pop=0,
    a_mux_sel=2, b_mux_sel=0,
    oen=1, pc_mux_sel=1, inc=1,
    src_sel=0, push=1, stack_we=1
)

# ============================================================
# Standard Directed Tests
# ============================================================

@cocotb.test()
async def test_instruction_disable(dut):
    await run_instr(dut, 0b01000, 1, 1, EXP_INSTR_DISABLE, "0100011")

@cocotb.test()
async def test_fetch_pc_to_r(dut):
    await run_instr(dut, 0b01000, 0, 0, EXP_FETCH_PC, "01000x0")

@cocotb.test()
async def test_fetch_r_plus_d(dut):
    await run_instr(dut, 0b01001, 0, 0, EXP_FETCH_R_D, "01001x0")

@cocotb.test()
async def test_load_r(dut):
    await run_instr(dut, 0b01010, 0, 0, EXP_LOAD_R, "01010x0")

@cocotb.test()
async def test_push_pc(dut):
    await run_instr(dut, 0b01011, 0, 0, EXP_PUSH_PC, "01011x0")

# ============================================================
# Exhaustive / Invalid Logic Tests
# ============================================================

@cocotb.test()
async def test_invalid_id_exhaustive(dut):
    """
    Exhaustively checks all ID values.
    If ID != 010, outputs must match EXP_INVALID_ID regardless of other inputs.
    """
    dut.instr_in.value = 0b11111 # Set noise on inputs
    dut.cc_in.value = 1
    dut.instr_en.value = 1
    
    for id_val in range(8):
        if id_val == 0b010: 
            continue # Skip the valid ID
            
        dut.id.value = id_val
        await Timer(1, units="ns")
        await check_outputs(dut, EXP_INVALID_ID, f"Invalid ID check for {bin(id_val)}")


@cocotb.test()
async def test_invalid_instruction_space(dut):
    """
    Exhaustively iterates through all 128 combinations of {instr_in, cc, en}.
    Identifies the 9 valid cases defined in RTL.
    Asserts that ALL other 119 cases result in EXP_DEFAULT.
    """
    dut.id.value = 0b010 # Enable the decoder
    
    # Iterate all possible inputs: instr(32) * cc(2) * en(2) = 128 cases
    for i in range(32):
        for c in range(2):
            for e in range(2):
                
                # Logic to determine if this specific combination is VALID in RTL
                is_valid = False
                
                # 1. Instruction Disable: 01000, cc=1, en=1
                if i == 0b01000 and c == 1 and e == 1: is_valid = True
                
                # 2. Fetch PC: 01000, cc=X, en=0
                elif i == 0b01000 and e == 0: is_valid = True
                
                # 3. Fetch R+D: 01001, cc=X, en=0
                elif i == 0b01001 and e == 0: is_valid = True
                
                # 4. Load R: 01010, cc=X, en=0
                elif i == 0b01010 and e == 0: is_valid = True
                
                # 5. Push PC: 01011, cc=X, en=0
                elif i == 0b01011 and e == 0: is_valid = True
                
                # If it's not a valid operation, it MUST be a default/invalid case
                if not is_valid:
                    dut.instr_in.value = i
                    dut.cc_in.value = c
                    dut.instr_en.value = e
                    await Timer(1, units="ns")
                    await check_outputs(dut, EXP_DEFAULT, f"Invalid Instr Check: instr={bin(i)} cc={c} en={e}")


# ============================================================
# Invariant Tests (Stability Checks)
# ============================================================

@cocotb.test()
async def invariant_instr_disable_exact(dut):
    dut.id.value = 0b010
    dut.instr_in.value = 0b01000
    dut.cc_in.value = 1
    dut.instr_en.value = 1

    await Timer(1, units="ns")
    ref = {k: int(getattr(dut, k).value) for k in EXP_INSTR_DISABLE}

    for _ in range(5):
        await Timer(1, units="ns")
        snap = {k: int(getattr(dut, k).value) for k in EXP_INSTR_DISABLE}
        assert snap == ref, "Instruction-disable opcode unstable"

async def invariant_cc_independent(dut, instr, exp):
    dut.id.value = 0b010
    dut.instr_en.value = 0
    dut.instr_in.value = instr

    ref = None
    for cc in (0, 1):
        dut.cc_in.value = cc
        await Timer(1, units="ns")
        snap = {k: int(getattr(dut, k).value) for k in exp}
        if ref is None:
            ref = snap
        else:
            assert snap == ref, f"CC dependence detected instr={instr:05b}"

@cocotb.test()
async def invariant_fetch_pc_cc(dut):
    await invariant_cc_independent(dut, 0b01000, EXP_FETCH_PC)

@cocotb.test()
async def invariant_fetch_r_d_cc(dut):
    await invariant_cc_independent(dut, 0b01001, EXP_FETCH_R_D)

@cocotb.test()
async def invariant_load_r_cc(dut):
    await invariant_cc_independent(dut, 0b01010, EXP_LOAD_R)

@cocotb.test()
async def invariant_push_pc_cc(dut):
    await invariant_cc_independent(dut, 0b01011, EXP_PUSH_PC)


# ------------------------------------------------------------
# Runner wrapper
# ------------------------------------------------------------
def test_instruction_decoder_2_hidden_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    sources = [proj_path / "sources/instruction_decoder_2.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="instruction_decoder_2",
        always=True,
    )
    runner.test(hdl_toplevel="instruction_decoder_2", test_module="test_instruction_decoder_2_hidden")