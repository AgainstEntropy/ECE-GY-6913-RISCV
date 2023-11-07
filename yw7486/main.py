import os
from copy import deepcopy

from core import FiveStageCore, SingleStageCore
from mem import DataMem, InsMem
from utils import Args, get_args


def process_testcase(TC_args: Args):

    imem = InsMem("Imem", TC_args.iodir)
    dmem_ss = DataMem("SS", TC_args.iodir, TC_args.output_dir)
    # dmem_fs = DataMem("FS", testcase_args)

    ssCore = SingleStageCore(TC_args.output_dir, imem, dmem_ss)
    # fsCore = FiveStageCore(testcase_args, imem, dmem_fs)

    while True:
        if not ssCore.halted:
            ssCore.step()

        # if not fsCore.halted:
        #     fsCore.step()

        if ssCore.halted: # and fsCore.halted:
            break

    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    # dmem_fs.outputDataMem()



if __name__ == "__main__":
    args = get_args()

    for testcase in os.listdir(args.iodir):
        print(testcase)
        testcase_args = deepcopy(args)
        testcase_args.iodir = args.iodir / testcase
        testcase_args.output_dir = args.output_dir / testcase

        testcase_args.output_dir.mkdir(parents=True, exist_ok=True)

        process_testcase(testcase_args)

