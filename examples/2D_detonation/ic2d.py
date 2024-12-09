import mfc.viz
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(
    prog="ic2d.py",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--scale", type=float, default=1, help="Scale.")
args = parser.parse_args()

case     = mfc.viz.Case("examples/1D_reactive_shocktube")
num_eqns = 15
num_dims = 2

def incrange(a: int, b: int):
    return range(a, b+1)

with open("examples/2D_detonation/ic_decl.f90", "w") as f:
    f.write("integer :: i_offset\n")
    for var_wrt in tqdm(incrange(1, num_eqns+num_dims-1), desc="Loading and Generating Arrays"):
        var_init = var_wrt if var_wrt < 3 else var_wrt - 1
        case.load_variable(f"{var_init}", f"prim.{var_init}")

        nx = len(case.get_data()[0][str(var_init)])

        if var_wrt != 3:
            elems = [str(x) for x in case.get_data()[14694][str(var_init)]]
        else:
            elems = [0.0] * nx

        f.write(f"real(kind(0d0)) :: var{var_wrt}(0:{nx - 1}) = [ &\n")
        for i, element in enumerate(elems):
            if i == len(elems) - 1:
                f.write(f"{element} &\n")
            else:
                f.write(f"{element}, &\n")
        f.write("]\n")

with open("examples/2D_detonation/ic_def.f90", "w") as f:
    f.write("case (666)\n")
    f.write(f"    i_offset = int(x_cc(0)/0.12d0*{nx - 1})\n")
    for var_wrt in tqdm(range(1, num_eqns+num_dims-1), desc="Loading Conserved Variables"):
        f.write(f"    q_prim_vf({var_wrt})%sf(i, j, 0) = var{var_wrt}(min(i_offset+i, {nx - 1}))\n")
