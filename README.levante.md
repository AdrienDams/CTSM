# How to build and run CTSM on Levante?

1. Initialisation
2. Create a case
3. Build the model
4. Submit the case

## 1. Initialisation

The model code currently running on Levante is in `/work/aa0049/a271098/CTSM` and https://github.com/AdrienDams/CTSM/tree/levante.

The current CTSM version is `ctsm5.1.dev086-3-gec6bb36a9` and will be updated reguraly.

1.1. Copy the folder `/home/a/a271098/.cime` into your home directory:
```
cp /home/a/a271098/.cime ~
```
- Change your account name on line 504 of `config_batch.xml` and line 9 of `config_machines.xml`.
- Change your scratch directory on line 13 of `config_machines.xml` (currently `/scratch/a/$USER`).

1.2. Load these modules
```
module load git openjdk python3 intel-oneapi-mpi/2021.5.0-intel-2021.5.0 esmf/8.2.0-intel-2021.5.0 gcc slk netcdf-c/4.8.1-openmpi-4.1.2-intel-2021.5.0 netcdf-fortran/4.5.3-openmpi-4.1.2-intel-2021.5.0 intel-oneapi-mkl/2022.0.1-gcc-11.2.0
```

1.3. Do these additionnals tags
```
export CIME_MACHINE=levante
MKLROOT="/sw/spack-levante/intel-oneapi-mkl-2022.0.1-ttdktf/mkl/2022.0.1"
```

1.4. Add to your `~/.condarc` (or create file)
```
channels:
  - conda-forge
auto_activate_base: false
```

## 2. Create a case

The resolutions that have been tested on Levante are: `f19_g17`. The compsets that have been tested on Levante are: `I2000Clm50Sp` `I2000Clm50BgcCrop` `I2000Clm50Fates`.

2.1. Create your case (example here is with the resolution `f19_g17` and the compset `I2000Clm50Sp`)
```
/work/aa0049/a271098/CTSM/cime/scripts/create_newcase --case I2000CLM50_001 --mach levante --res f19_g17 --compset I2000Clm50Sp --run-unsupported
```

## 3. Build the model

3.1. Setup your case
```
./case.setup
```

3.2. Build your case
```
./case.build
```

## 4. Submit the case
```
./case.submit
```

Thanks for Heidrun Matthes, Irina Fast, and the DKRZ support team to help me install CTSM on Levante.

If you need help or want to do a regional simulation or use ERA5 for forcings, contact adamseau@awi.de.
