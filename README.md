# ECE-GY-6913-RISCV

[project page](https://against-entropy.notion.site/RISC-V-simulator-3364c353830c4286928c2343b99e3a6f)

## Create Environment

    conda env create -n risc-v -f requirements.txt

    conda activate risc-v

### Run with default arguments

    python ./[netid]/main.py

This will automatically create an output folder called `output_[netid]`.

> One can modify the netid in [constants.py](yw7486/constants.py).

### Debug mode

When `debug` is activated, the output folder will be renamed as `output_[netid]_debug`.

    python ./yw7486/main.py --debug
