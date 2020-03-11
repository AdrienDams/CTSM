"""

CTSM only test to do the CN-matrix spinup procedure

This is a CLM specific test:
Verifies that spinup works correctly
this test is only valid for CLM compsets

Step 0: Run a cold-start with matrix spinup off
Step 1: Run a fast-mode spinup
Step 2: Run a 2-loop fast-mode spinup
Step 3: Run a slow-mode spinup
Step 4: matrix Spinup off
"""
import shutil, glob, os, sys

if __name__ == '__main__':
   CIMEROOT = os.environ.get("CIMEROOT")
   if CIMEROOT is None:
      CIMEROOT = "../../cime";

   sys.path.append(os.path.join( CIMEROOT, "scripts", "lib"))
   sys.path.append(os.path.join( CIMEROOT, "scripts" ) )

from CIME.XML.standard_module_setup import *
from CIME.SystemTests.system_tests_common import SystemTestsCommon
from CIME.SystemTests.test_utils import user_nl_utils


logger = logging.getLogger(__name__)

class SSPMATRIXCN(SystemTestsCommon):

    # Class data
    nyr_forcing = 2
    # Get different integer multiples of the number of forcing years
    full   = nyr_forcing
    twice  = 2 * nyr_forcing
    thrice = 3 * nyr_forcing
    # Define the settings that will be used for each step
    steps  = ["0",       "1",      "2",      "3",      "4"      ]
    desc   = ["cold",    "fast",   "trans",  "slow",   "normal" ]
    runtyp = ["startup", "branch", "branch", "branch", "branch" ]
    spin   = [False,     True,     True,     True,     False    ]
    stop_n = [5,         thrice,   twice,    thrice,   thrice   ]
    cold   = [True,      False,    False,    False,    False    ]
    iloop  = [-999,      -999,     2,        -999,     -999     ]
    sasu   = [-999,      1,        1,        full,     -999     ]

    def __init__(self, case=None):
        """
        initialize an object interface to the SSPMATRIXCN system test
        """
        expect ( len(self.steps) == len(self.sasu),   "length of steps must be the same as sasu" )
        expect ( len(self.steps) == len(self.spin),   "length of steps must be the same as spin" )
        expect ( len(self.steps) == len(self.desc),   "length of steps must be the same as desc" )
        expect ( len(self.steps) == len(self.cold),   "length of steps must be the same as cold" )
        expect ( len(self.steps) == len(self.runtyp), "length of steps must be the same as runtyp" )
        expect ( len(self.steps) == len(self.iloop),  "length of steps must be the same as iloop" )
        expect ( len(self.steps) == len(self.stop_n), "length of steps must be the same as stop_n" )

        if __name__ != '__main__':
           SystemTestsCommon.__init__(self, case)
           ystart = self._case.get_value("DATM_CLMNCEP_YR_START")
           yend   = self._case.get_value("DATM_CLMNCEP_YR_END")
        else:
           ystart = 2000
           yend   = 2001

        expect( yend-ystart+1 == self.nyr_forcing, "Number of years run over MUST correspond to nyr_forcing" )

    def check_n( self, n):
        "Check if n is within range"
        expect( ( (n >= 0) and (n < self.n_steps()) ), "Step number is out of range = " + str(n) )

    def __logger__(self, n=0):
        "Log info on this step"

        self.check_n( n )
        logger.info("Step {}: {}: doing a {} run for {} years".format( self.steps[n], self.runtyp[n], self.desc[n], self.stop_n[n] )  )
        if ( n+1 < self.n_steps() ):
           logger.info("  writing restarts at end of run")
           logger.info("  short term archiving is on ")

    def n_steps(self):
        "Total number of steps"

        return( len(self.steps) )

    def total_years(self):
        "Total number of years needed to do the full spinup"

        ysum = 0
        for nyr in self.stop_n:
           ysum = ysum + nyr

        return( ysum )

    def append_user_nl(self, caseroot, n=0):
        "Append needed settings to the user_nl files"

        self.check_n( n )
        # For all set output to yearly
        contents_to_append = "hist_nhtfrq = -8760"
        contents_to_append = contents_to_append + ", hist_mfilt = "+str(self.nyr_forcing)
        # For all but last step turn extra matrix output to off
        if ( n < 4 ):
           contents_to_append = contents_to_append + ", is_outmatrix = .False."
        # For matrix spinup steps, set the matrix spinup and other variables associated with it
        if ( self.spin[n] ):
            contents_to_append = contents_to_append + ", nyr_forcing = "+str(self.nyr_forcing)
            contents_to_append = contents_to_append + ", isspinup = .True."
            contents_to_append = contents_to_append + ", nyr_sasu = " + str(self.sasu[n])
            if ( self.iloop[n] != -999 ):
               contents_to_append = contents_to_append + ", iloop_avg = " + str(self.iloop[n])

        # Always append to the end
        user_nl_utils.append_to_user_nl_files(caseroot = caseroot,
                                              component = "clm",
                                              contents = contents_to_append)

    def run_phase(self):
        "Run phase"

        caseroot = self._case.get_value("CASEROOT")
        orig_case = self._case
        orig_casevar = self._case.get_value("CASE")


        # Get a clone of each step except the last one
        b4last = self.n_steps() - 1
        for n in range(b4last):
           #
           # Clone the main case, and get it setup for the next step
           #
           clone_path =  "{}.step{}".format(caseroot,self.steps[n])
           if os.path.exists(clone_path):
               shutil.rmtree(clone_path)
           if ( n > 0 ): 
             del clone
           self._set_active_case(orig_case)
           clone = self._case.create_clone(clone_path, keepexe=True)
           os.chdir(clone_path)
           self._set_active_case(clone)

           self.__logger__(n)

           with clone:
              clone.set_value("RUN_TYPE", self.runtyp[n] )
              clone.set_value("STOP_N", self.stop_n[n] )
              if ( self.cold[n] ):
                 clone.set_value("CLM_FORCE_COLDSTART", "on" )
              else:
                 clone.set_value("CLM_FORCE_COLDSTART", "off" )

              if ( self.spin[n] ):
                 clone.set_value("CLM_ACCELERATED_SPINUP", "on" )
              else:
                 clone.set_value("CLM_ACCELERATED_SPINUP", "off" )

              self.append_user_nl( clone_path, n )

           dout_sr = clone.get_value("DOUT_S_ROOT")

           self._skip_pnl = False
           #
           # Start up from the previous case
           #
           rundir = clone.get_value("RUNDIR")
           with clone:
              if ( n > 0 ):
                 clone.set_value("GET_REFCASE", False)
                 expect( "refcase" in locals(), "refcase was NOT previously set" )
                 clone.set_value("RUN_REFCASE", refcase )
                 expect( "refdate" in locals(), "refdate was NOT previously set" )
                 clone.set_value("RUN_STARTDATE", refdate )
                 clone.set_value("RUN_REFDATE", refdate )
                 for item in glob.glob("{}/*{}*".format(rest_path, refdate)):
                     linkfile = os.path.join(rundir, os.path.basename(item))
                     if os.path.exists(linkfile):
                         os.remove( linkfile )
                     os.symlink(item, linkfile )
   
                 for item in glob.glob("{}/*rpointer*".format(rest_path)):
                     shutil.copy(item, rundir)
   
           #
           # Run the case (Archiving on)
           #
           self._case.flush()
           self.run_indv(suffix="step{}".format(self.steps[n]), st_archive=True)

           #
           # Get the reference case from this step for the next step
           #
           refcase = clone.get_value("CASE")
           refdate = run_cmd_no_fail(r'ls -1dt {}/rest/*-00000* | head -1 | sed "s/-00000.*//" | sed "s/^.*rest\///"'.format(dout_sr))
           refsec = "00000"
           rest_path = os.path.join(dout_sr, "rest", "{}-{}".format(refdate, refsec))

        #
        # Last step in original case
        #
        n = self.n_steps() - 1
        #
        # Setup the case to run from the previous clone step
        #
        os.chdir(caseroot)
        self._set_active_case(orig_case)
        self.__logger__(n)
        self._case.set_value("DOUT_S", False)
        self._case.set_value("RUN_TYPE", self.runtyp[n] )
        self._case.set_value("STOP_N", self.stop_n[n] )
        rundir = self._case.get_value("RUNDIR")
        self._case.set_value("GET_REFCASE", False)
        expect( "refcase" in locals(), "refcase was NOT previously set" )
        self._case.set_value("RUN_REFCASE", refcase)
        expect( "refdate" in locals(), "refdate was NOT previously set" )
        self._case.set_value("RUN_REFDATE", refdate)
        self._case.set_value("RUN_STARTDATE", refdate )
        for item in glob.glob("{}/*{}*".format(rest_path, refdate)):
            linkfile = os.path.join(rundir, os.path.basename(item))
            if os.path.exists(linkfile):
               os.remove( linkfile )
            os.symlink(item, linkfile )

        for item in glob.glob("{}/*rpointer*".format(rest_path)):
            shutil.copy(item, rundir)

        self.append_user_nl( clone_path, n )
        #
        # Don't need to set COLDSTART or ACCEL_SPINUP
        #

        #
        # Run the case (short term archiving is off)
        #
        self._case.flush()
        self.run_indv( suffix="step{}".format(self.steps[n]), st_archive=False )

#
# Unit testing for above
#
import unittest
from CIME.case import Case
from CIME.utils import _LessThanFilter
from argparse  import RawTextHelpFormatter

class test_ssp_matrixcn(unittest.TestCase):

   def setUp( self ):
     self.ssp = SSPMATRIXCN()

   def test_logger( self ):
     # Test the logger
     stream_handler = logging.StreamHandler(sys.stdout)
     logger.addHandler(stream_handler)
     logger.level = logging.DEBUG
     logger.info( "nyr_forcing = {}".format(self.ssp.nyr_forcing) )
     for n in range(self.ssp.n_steps()):
       self.ssp.__logger__(n)
       if ( self.ssp.spin[n] ):
          logger.info( "  isspinup = .true." )
          logger.info( "  nyr_sasu = {}".format(self.ssp.sasu[n]) )
          if ( self.ssp.iloop[n] != -999 ):
             logger.info( "  iloop_avg = {}".format(self.ssp.iloop[n]) )

     logger.info( "Total number of years {}".format( self.ssp.total_years() ) )
     logger.removeHandler(stream_handler)

   def test_n_steps( self ):
       self.assertTrue( self.ssp.n_steps() == 5)

   def test_valid_n( self ):
       for n in range(self.ssp.n_steps()):
          self.ssp.check_n(n)
    
   def test_negative_n( self ):
       self.assertRaises(SystemExit, self.ssp.check_n, -1 )

   def test_n_too_big( self ):
       self.assertRaises(SystemExit, self.ssp.check_n, self.ssp.n_steps()  )

   def test_append_user_nl_step2( self ):
       ufile = "user_nl_clm"
       if not os.path.exists(ufile):
         os.mknod(ufile)
       else:
         expect( 0, ufile+" file already exists, not overwritting it" )

       self.ssp.append_user_nl( caseroot=".", n=2)
       print( ufile+" for step 2" )
       log = open(ufile, "r").read()
       print( log )
       os.remove(ufile)


if __name__ == '__main__':
     unittest.main()


