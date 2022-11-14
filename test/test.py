import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, Timer


async def init(dut):
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.rst.value = 1
    await ClockCycles(dut.clk, 10)
    dut.rst.value = 0

    await RisingEdge(dut.clk)


def rand_lit():
    return random.randint(0, 0b011111)


def rand_lit_gen(n=20):
    for LIT in range(n):
        yield rand_lit()


@cocotb.test()
async def test_instr_literal(dut):
    await init(dut)

    for LIT in rand_lit_gen():
        dut.instr.value = LIT
        await ClockCycles(dut.clk, 2)
        assert (
            int(dut.io_out.value) == LIT
        ), f"literal failed with {LIT} != {int(dut.io_out.value)}"


@cocotb.test()
async def test_add(dut):
    await init(dut)

    for ADD_LIT in range(3):
        for LIT in rand_lit_gen():
            dut.instr.value = LIT
            await ClockCycles(dut.clk, 2)  # R <- LIT
            assert int(dut.io_out.value) == LIT
            dut.instr.value = 0b1100_00 | ADD_LIT
            await ClockCycles(dut.clk, 2)  # R <- R + ADD_LIT
            assert (
                int(dut.io_out.value) == (LIT + ADD_LIT) % 32
            ), f"add failed with {LIT} + {ADD_LIT} != {int(dut.io_out.value)}"

    # test incrementing by one repeatedly
    await FallingEdge(dut.clk)
    dut.instr.value = 0b1100_00 | 0b01
    n = int(dut.io_out.value)
    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 100)
    assert (
        int(dut.io_out.value) == n + 100 % 32
    ), f"add100: {n} -/-> {int(dut.io_out.value)}"

    # test incrementing by zero repeatedly
    await FallingEdge(dut.clk)
    dut.instr.value = 0b1100_00 | 0b00
    n = int(dut.io_out.value)
    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 100)
    assert int(dut.io_out.value) == n, f"add0: {n} != {int(dut.io_out.value)}"


@cocotb.test()
async def test_sub(dut):
    await init(dut)

    for SUB_LIT in range(3):
        for LIT in rand_lit_gen():
            dut.instr.value = LIT
            await ClockCycles(dut.clk, 2)  # R <- LIT
            assert int(dut.io_out.value) == LIT
            dut.instr.value = 0b1101_00 | SUB_LIT
            await ClockCycles(dut.clk, 2)  # R <- R + SUB_LIT
            assert (
                int(dut.io_out.value) == (LIT - SUB_LIT) % 32
            ), f"sub failed with {LIT} - {SUB_LIT} != {int(dut.io_out.value)}"

    # test decrementing by one repeatedly
    await FallingEdge(dut.clk)
    dut.instr.value = 0b1101_00 | 0b01
    n = int(dut.io_out.value)
    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 100)
    assert (
        int(dut.io_out.value) == (n - 100) % 32
    ), f"sub100: {n} -/-> {int(dut.io_out.value)}"

    # test decrementing by zero repeatedly
    await FallingEdge(dut.clk)
    dut.instr.value = 0b1101_00 | 0b00
    n = int(dut.io_out.value)
    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 100)
    assert int(dut.io_out.value) == n, f"sub0: {n} -/-> {int(dut.io_out.value)}"
