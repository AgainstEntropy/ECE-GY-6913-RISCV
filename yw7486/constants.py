from easydict import EasyDict

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
BYTE = 8
WORD_LEN = SYS_BIT // BYTE
UPPER_BOUND = 2 ** (SYS_BIT - 1) - 1
BIAS = 2 ** SYS_BIT

STAGES = EasyDict(
    IF  = 0,
    ID  = 1,
    EX  = 2,
    MEM = 3,
    WB  = 4,
)

INSTR_TYPES = EasyDict(
    R      = 0,
    I      = 1,
    J      = 2,
    B      = 3,
    LOAD_I = 4,
    S      = 5,
    HALT   = 6,
)

ENDIAN_TYPES = EasyDict(
    BIG   = 0,
    SMALL = 1,
)