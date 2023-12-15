from copy import deepcopy

from arg_utils import Args, get_args
from core import FiveStageCore, SingleStageCore
from mem import DataMem, InsMem


def process_testcase(TC_args: Args):

    imem = InsMem("Imem", TC_args.iodir)
    dmem_ss = DataMem("SS", TC_args.iodir, TC_args.output_dir)
    dmem_fs = DataMem("FS", TC_args.iodir, TC_args.output_dir)

    ssCore = SingleStageCore(TC_args.output_dir, imem, dmem_ss)
    fsCore = FiveStageCore(TC_args.output_dir, imem, dmem_fs)

    while True:
        if not ssCore.halted:
            ssCore.step()

        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            fsCore.myRF.outputRF(fsCore.cycle)  # dump RF
            fsCore.printState(fsCore.nextState, fsCore.cycle)
            fsCore.cycle += 1
            break

    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()

    # dump SS and FS performance.
    ssCore.monitor.writePerformance(mode='w')
    fsCore.monitor.writePerformance(mode='a')


if __name__ == "__main__":
    args = get_args()

    # for testcase_folder in os.listdir(args.iodir):
    for testcase_folder in args.iodir.glob('*'):
        print(f"Processing {testcase_folder} ...")
        testcase_args = deepcopy(args)
        testcase_args.iodir = testcase_folder
        testcase_args.output_dir = args.output_dir / testcase_folder.name

        testcase_args.output_dir.mkdir(parents=True, exist_ok=True)

        process_testcase(testcase_args)

    else:
        print("Done!")
        