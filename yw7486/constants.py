from enum import Enum, auto

# memory size, in reality, the memory size should be 2^32,
# but for this lab, for the space resaon, we keep it as this large number,
# but the memory is still 32-bit addressable.
MemSize = 1000

NETID = "yw7486"

IMEM_FILE = "imem.txt"
DMEM_FILE = "dmem.txt"
DMEM_RESULT_FILE = "DMEMResult.txt"
RF_FILE = "RFresult.txt"
PERFORMANCE_FILE = "PerformanceMetrics.txt"

SS_STATE_RESULT_FILE = "StateResult_SS.txt"
FS_STATE_RESULT_FILE = "StateResult_FS.txt"

SYS_BIT = 32
BYTE_LEN = 8
WORD_LEN = SYS_BIT // BYTE_LEN
UPPER_BOUND = 2 ** (SYS_BIT - 1) - 1
BIAS = 2 ** SYS_BIT

class STAGES(Enum):
    IF  = auto()
    ID  = auto()
    EX  = auto()
    MEM = auto()
    WB  = auto()

class INSTR_TYPES(Enum):
    R      = auto()
    I      = auto()
    J      = auto()
    B      = auto()
    LOAD_I = auto()
    S      = auto()
    HALT   = auto()

class ENDIAN_TYPES(Enum):
    BIG   = auto()
    SMALL = auto()
