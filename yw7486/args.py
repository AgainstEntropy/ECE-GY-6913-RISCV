from pathlib import Path

from tap import Tap

from constants import NETID


class Args(Tap):
    debug: bool = False
    iodir: Path = "./input/"
    output_dir: Path = None


def get_args():
    args = Args().parse_args()

    args.iodir = args.iodir.resolve()
    print("IO Directory:", args.iodir)

    args.output_dir =  args.output_dir or (f"./output_{NETID}_debug/" if args.debug \
        else f"../output_{NETID}/")
    args.output_dir = Path(args.output_dir).resolve()
    print("Output Directory:", args.output_dir)

    return args
