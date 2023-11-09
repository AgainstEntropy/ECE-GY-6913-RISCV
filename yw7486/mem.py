from pathlib import Path

from constants import DMEM_FILE, DMEM_RESULT_FILE, IMEM_FILE
from args import Args


class InsMem(object):
    def __init__(self, name: str, ioDir: Path):
        self.id = name

        with open(ioDir / IMEM_FILE) as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress: int):
        # read instruction memory
        # return 32 bit hex val
        return "".join(self.IMem[ReadAddress: ReadAddress + 4])  # read in 4 lines and cocnat them into a 32-bit binary string


class DataMem(object):
    def __init__(self, name: str, ioDir: Path, outDir: Path):
        self.id = name
        self.ioDir = ioDir
        self.outDir = outDir
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
        resPath = self.outDir / f"{self.id}_{DMEM_RESULT_FILE}"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

