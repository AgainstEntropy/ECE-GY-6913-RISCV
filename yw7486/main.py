import argparse
import os
from pathlib import Path

from .constants import MemSize, \
    IMEM_FILE, DMEM_FILE, RF_FILE, \
    SS_STATERESULT_FILE, FS_STATERESULT_FILE

# memory size, in reality, the memory size should be 2^32,
# but for this lab, for the space resaon, we keep it as this large number,
# but the memory is still 32-bit addressable.


class InsMem(object):
    def __init__(self, name: str, ioDir: Path):
        self.id = name

        with open(ioDir / IMEM_FILE) as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress: int):
        # read instruction memory
        # return 32 bit hex val
        return "".join(self.IMem[ReadAddress : ReadAddress + 4])


class DataMem(object):
    def __init__(self, name: str, ioDir: Path):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir / DMEM_FILE) as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def readInstr(self, ReadAddress: int):
        # read data memory
        # return 32 bit hex val
        pass

    def writeDataMem(self, Address: int, WriteData):
        # write data into byte addressable memory
        pass

    def outputDataMem(self):
        resPath = self.ioDir / f"{self.id}_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])


class RegisterFile(object):
    def __init__(self, ioDir: Path):
        self.outputFile = ioDir / RF_FILE
        self.Registers = [0x0 for i in range(32)]

    def readRF(self, Reg_addr: int):
        # Fill in
        pass

    def writeRF(self, Reg_addr: int, Wrt_reg_data):
        # Fill in
        pass

    def outputRF(self, cycle: int):
        op = ["-" * 70 + "\n", f"State of RF after executing cycle: {cycle}\n"]
        op.extend([f"{val}\n" for val in self.Registers])
        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": False, "Instr": 0}
        self.EX = {
            "nop": False,
            "Read_data1": 0,
            "Read_data2": 0,
            "Imm": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "is_I_type": False,
            "rd_mem": 0,
            "wrt_mem": 0,
            "alu_op": 0,
            "wrt_enable": 0,
        }
        self.MEM = {
            "nop": False,
            "ALUresult": 0,
            "Store_data": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "rd_mem": 0,
            "wrt_mem": 0,
            "wrt_enable": 0,
        }
        self.WB = {
            "nop": False,
            "Wrt_data": 0,
            "Rs": 0,
            "Rt": 0,
            "Wrt_reg_addr": 0,
            "wrt_enable": 0,
        }


class Core(object):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        self.myRF = RegisterFile(ioDir)
        self.cycle: int = 0
        self.halted: bool = False
        self.ioDir: Path = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem: InsMem = imem
        self.ext_dmem: DataMem = dmem

    @staticmethod
    def parse_instruction(instruction: str):
        # TODO: implement this
        raise NotImplementedError
        return parsed_instruction


class SingleStageCore(Core):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        super(SingleStageCore, self).__init__(ioDir / "SS_", imem, dmem)
        self.opFilePath = ioDir / SS_STATERESULT_FILE

    def step(self):
        # Your implementation

        self.halted = True
        if self.state.IF["nop"]:
            self.halted = True

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = (
            self.nextState
        )  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state: State, cycle: int):
        printstate = [
            "-" * 70 + "\n",
            "State after executing cycle: " + str(cycle) + "\n",
        ]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


class FiveStageCore(Core):
    def __init__(self, ioDir: Path, imem: InsMem, dmem: DataMem):
        super(FiveStageCore, self).__init__(ioDir / "FS_", imem, dmem)
        self.opFilePath = ioDir / FS_STATERESULT_FILE

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------

        # --------------------- MEM stage --------------------

        # --------------------- EX stage ---------------------

        # --------------------- ID stage ---------------------

        # --------------------- IF stage ---------------------

        self.halted = True
        if (
            self.state.IF["nop"]
            and self.state.ID["nop"]
            and self.state.EX["nop"]
            and self.state.MEM["nop"]
            and self.state.WB["nop"]
        ):
            self.halted = True

        self.myRF.outputRF(self.cycle)  # dump RF
        self.printState(
            self.nextState, self.cycle
        )  # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = (
            self.nextState
        )  # The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state: State, cycle: int):
        printstate = [
            "-" * 70 + "\n",
            "State after executing cycle: " + str(cycle) + "\n",
        ]
        printstate.extend(
            ["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()]
        )
        printstate.extend(
            ["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()]
        )
        printstate.extend(
            ["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()]
        )
        printstate.extend(
            ["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()]
        )
        printstate.extend(
            ["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()]
        )

        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


if __name__ == "__main__":
    # parse arguments for input file location
    parser = argparse.ArgumentParser(description="RV32I processor")
    parser.add_argument(
        "--iodir", default="", type=str, help="Directory containing the input files."
    )
    args = parser.parse_args()

    ioDir = Path(os.path.abspath(args.iodir))
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while True:
        if not ssCore.halted:
            ssCore.step()

        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break

    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()
