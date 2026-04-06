"""Build and export the Devais PCB design using tscircuit."""

import os
import subprocess
import sys

PCB_DIR = os.path.join(os.path.dirname(__file__), "pcb")
CIRCUIT_FILE = "index.circuit.tsx"


def run_tsci(*args: str) -> int:
    result = subprocess.run(
        ["tsci", *args],
        cwd=PCB_DIR,
    )
    return result.returncode


def build():
    sys.exit(run_tsci("build"))


def export():
    rc = run_tsci("build")
    if rc != 0:
        print("Build failed, skipping exports", file=sys.stderr)
        sys.exit(rc)

    for fmt, output in [
        ("pcb-svg", None),
        ("schematic-svg", None),
        ("assembly-svg", None),
        ("readable-netlist", None),
    ]:
        args = ["export", CIRCUIT_FILE, "-f", fmt]
        if output:
            args.extend(["-o", output])
        run_tsci(*args)

    print("\nExported to hardware/pcb/:")
    print("  index.circuit-pcb.svg        PCB layout")
    print("  index.circuit-schematic.svg  Schematic")
    print("  index.circuit-assembly.svg   Assembly drawing")
    print("  index.circuit.readable-netlist  Netlist")
