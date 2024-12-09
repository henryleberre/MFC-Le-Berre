#!/usr/bin/env python3

# References:
# + https://doi.org/10.1016/j.ijhydene.2023.03.190:  Verification of numerical method
# + https://doi.org/10.1016/j.compfluid.2013.10.014: 4.7. Multi-species reactive shock tube

import json, argparse
import cantera as ct

parser = argparse.ArgumentParser(
    prog="2D_detonation",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--mfc", type=json.loads, default='{}', metavar="DICT",
                    help="MFC's toolchain's internal state.")
parser.add_argument("--no-chem", dest='chemistry', default=True, action="store_false",
                                 help="Disable chemistry.")
parser.add_argument("--scale",   type=float,  default=1,    help="Scale.")

args = parser.parse_args()

ctfile    = 'h2o2.yaml'
sol_L     = ct.Solution(ctfile)
sol_L.DPX =   0.072,  7173, 'H2:2,O2:1,AR:7'

sol_R     = ct.Solution(ctfile)
sol_R.DPX = 0.18075, 35594, 'H2:2,O2:1,AR:7'

u_l = 0
u_r = -487.34

L  = 0.12
Nx = int(2*400 * args.scale)
Ny = int(200 * args.scale)
dx =   2*L/Nx
dy = (L/2)/Ny
dt = min(dx,dy)/abs(u_r)*0.05*0.1*0.2
Tend=230e-6

NT=int(Tend/dt)
SAVE_COUNT=100
NS=NT//SAVE_COUNT

case = {
    # Logistics ================================================================
    'run_time_info'                : 'T',
    # ==========================================================================

    # Computational Domain Parameters ==========================================
    'x_domain%beg'                 : 0,
    'x_domain%end'                 : L*2,
    'y_domain%beg'                 : 0,
    'y_domain%end'                 : L/2,
    'm'                            : Nx,
    'n'                            : Ny,
    'p'                            : 0,
    'dt'                           : float(dt),
    't_step_start'                 : 0,
    't_step_stop'                  : NT,
    't_step_save'                  : NS,
    't_step_print'                 : 10,
    'parallel_io'                  : 'T' if args.mfc.get("mpi", True) else 'F',

    # Simulation Algorithm Parameters ==========================================
    'model_eqns'                   : 2,
    'num_fluids'                   : 1,
    'num_patches'                  : 2,
    'mpp_lim'                      : 'F',
    'mixture_err'                  : 'F',
    'time_stepper'                 : 3,
    'weno_order'                   : 5,
    'weno_eps'                     : 1E-16,
    'weno_avg'                     : 'F',
    'mapped_weno'                  : 'T',
    'mp_weno'                      : 'T',
    'riemann_solver'               : 2,
    'wave_speeds'                  : 1,
    'avg_state'                    : 2,
    'bc_x%beg'                     :-3,
    'bc_x%end'                     :-3,
    'bc_y%beg'                     :-1,
    'bc_y%end'                     :-1,

    # Chemistry ================================================================
    'chemistry'                    : 'F' if not args.chemistry else 'T',
    'chem_params%diffusion'        : 'F',
    'chem_params%reactions'        : 'T',
    'cantera_file'                 : ctfile,
    # ==========================================================================

    # Formatted Database Files Structure Parameters ============================
    'format'                       : 1,
    'precision'                    : 2,
    'prim_vars_wrt'                : 'T',
    'chem_wrt_T'                   : 'T',
    # ==========================================================================
    'rho_wrt' : 'T',

    # ==========================================================================
    'patch_icpp(1)%geometry'       : 3,
    'patch_icpp(1)%x_centroid'     : L,
    'patch_icpp(1)%y_centroid'     : L/4,
    'patch_icpp(1)%length_x'       : 2*L,
    'patch_icpp(1)%length_y'       : L/2,
    'patch_icpp(1)%vel(1)'         : 0.0,
    'patch_icpp(1)%vel(2)'         : 0.0,
    'patch_icpp(1)%pres'           : sol_R.P,
    'patch_icpp(1)%alpha(1)'       : 1,
    'patch_icpp(1)%alpha_rho(1)'   : sol_R.density,
    # ==========================================================================

    # ==========================================================================
    'patch_icpp(2)%geometry'       : 7,
    'patch_icpp(2)%x_centroid'     : L/2,
    'patch_icpp(2)%y_centroid'     : L/4,
    'patch_icpp(2)%length_x'       : L,
    'patch_icpp(2)%length_y'       : L/2,
    'patch_icpp(2)%hcid'           : 666,
    'patch_icpp(2)%vel(1)'         : 0,
    'patch_icpp(2)%vel(2)'         : 0,
    'patch_icpp(2)%pres'           : sol_R.P,
    'patch_icpp(2)%alpha(1)'       : 1,
    'patch_icpp(2)%alpha_rho(1)'   : sol_R.density,
    'patch_icpp(2)%alter_patch(1)' : 'T',
    # ==========================================================================

    # ==========================================================================
    #'patch_icpp(3)%geometry'       : 21,
    #'patch_icpp(3)%x_centroid'     : 3*L/2,
    #'patch_icpp(3)%y_centroid'     : L/4,
    #'patch_icpp(3)%length_x'       : L,
    #'patch_icpp(3)%length_y'       : L/2,
    #'patch_icpp(3)%vel(1)'         : 0,
    #'patch_icpp(3)%vel(2)'         : 100,
    #'patch_icpp(3)%model_scale(1)' : 1/20.0,
    #'patch_icpp(3)%model_scale(2)' : 1/2.0,
    #'patch_icpp(3)%model_scale(3)' : 1/10.0,
    #'patch_icpp(3)%model_translate(1)' : L/2+L/1.2,
    #'patch_icpp(3)%model_translate(2)' : L/4,
    #'patch_icpp(3)%model_translate(3)' : 0,
    #'patch_icpp(3)%model_threshold' : 0.5,
    #'patch_icpp(3)%model_spc'       : 'mfc-small.stl',
    #'patch_icpp(3)%pres'           : 1000*sol_R.P,
    #'patch_icpp(3)%alpha(1)'       : 1,
    #'patch_icpp(3)%alpha_rho(1)'   : sol_R.density,
    #'patch_icpp(3)%model_filepath' : 'mfc-small.stl',
    #'patch_icpp(3)%alter_patch(1)' : 'T',
    #'patch_icpp(3)%alter_patch(2)' : 'T',
    # ==========================================================================

    'vel_wrt(1)'                   : 'T',
    'vel_wrt(2)'                   : 'T',
    'pres_wrt'                     : 'T',

    # Fluids Physical Parameters ===============================================
    'fluid_pp(1)%gamma'            : 1.0E+00/(4.4E+00-1.0E+00),
    'fluid_pp(1)%pi_inf'           : 0,
    # ==========================================================================
}

if args.chemistry:
    for i in range(len(sol_L.Y)):
        case[f'chem_wrt_Y({i + 1})']    = 'T'
        case[f'patch_icpp(1)%Y({i+1})'] = sol_L.Y[i]
        case[f'patch_icpp(2)%Y({i+1})'] = sol_L.Y[i]
        #case[f'patch_icpp(3)%Y({i+1})'] = sol_L.Y[i]

if __name__ == '__main__':
    print(json.dumps(case))
