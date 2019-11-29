# -------------------------------------------------------------------------
# set the input namelist options for clm's build-namelist
# -------------------------------------------------------------------------
# - tuning parameters and initial conditions should be optimized for what CLM model version and 
#   what meteorlogical forcing combination? valid values are:
#   clm5_0_cam6.0, clm5_0_GSWP3v1, clm5_0_CRUv7, clm4_5_CRUv7, clm4_5_GSWP3v1, clm4_5_cam6.0
# - only support startup or continue runs for now

clm_phys          = "clm5_0"
start_type        = "default"
start_ymd         = "20000101"
startfile_type    = "finidat"
ignore            = "-ignore_ic_year"
configuration     = "clm"
structure         = "standard"
ccsm_co2_ppmv     =  str(367.0)
clm_co2_type      = "constant"
clm_bldnml_opts   = "-bgc sp"
use_case          = "2000_control"
lnd_tuning_mode   = "clm5_0_GSWP3v1"
spinup            = "off"
gridmask          = "gx3v7"
lnd_grid          = "4x5" 
lnd_domain_file   = "domain.lnd.fv4x5_gx3v7.091218.nc"
lnd_domain_path   = "/glade/p/cesmdata/cseg/inputdata/share/domains"
din_loc_root      = "/glade/p/cesmdata/cseg/inputdata"
clm_namelist_opts = ""
