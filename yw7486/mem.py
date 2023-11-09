from pathlib import Path

from constants import BYTE_LEN, DMEM_FILE, DMEM_RESULT_FILE, IMEM_FILE, WORD_LEN
from misc import signed_int_to_binary_str


class InsMem(object):
    def __init__(self, name: str, ioDir: Path):
        self.id = name

        with open(ioDir / IMEM_FILE) as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress: int):
        # read instruction memory
        # return 32 bit hex val
        return "".join(self.IMem[ReadAddress: ReadAddress + WORD_LEN])  # read in 4 lines and cocnat them into a 32-bit binary string


class DataMem(object):
    def __init__(self, name: str, ioDir: Path, outDir: Path):
        self.id = name
        self.ioDir = ioDir
        self.outDir = outDir
        with open(ioDir / DMEM_FILE) as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def readDataMem(self, ReadAddress: int):
        # read data memory
        binary_str = "".join(self.DMem[ReadAddress: ReadAddress + WORD_LEN])
        return binary_str

    def writeDataMem(self, Address: int, WriteData: int):
        # write data into byte addressable memory
        binary_str = signed_int_to_binary_str(WriteData)
        for i in range(WORD_LEN):
            self.DMem[Address + i] = binary_str[BYTE_LEN*i: BYTE_LEN*(i+1)]

    def outputDataMem(self):
        resPath = self.outDir / f"{self.id}_{DMEM_RESULT_FILE}"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

