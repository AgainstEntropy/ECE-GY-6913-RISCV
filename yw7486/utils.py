import os
from functools import partial
from pathlib import Path

from tap import Tap

from constants import NETID

binary_str_to_int = partial(int, base=2)

class Args(Tap):
    debug: bool = False

    iodir: str = "./input/"

    output_dir: str = None


def get_args():
    args = Args().parse_args()

    args.iodir = Path(os.path.abspath(args.iodir))
    print("IO Directory:", args.iodir)

    args.output_dir =  f"./output_{NETID}_debug/" if args.debug \
        else f"../output_{NETID}/"
    args.output_dir = Path(os.path.abspath(args.output_dir))
    print("Output Directory:", args.output_dir)

    return args
