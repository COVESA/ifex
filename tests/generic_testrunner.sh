#!/bin/bash

# Execute generic_testrunner on each def found under testdefs/

# Normalize current working directory
cd "$(dirname "$0")"

echo "Sourcing venv/bin/activate, if it exists"
[ -x ../venv/bin/activate ] && . ../venv/bin/activate

/bin/ls testdefs | while read x ; do
   if [ -d "testdefs/$x" ] ; then
      echo '================================================================================'
      echo "Testdef $x:" 
      echo '================================================================================'
      python generic_testrunner.py "testdefs/$x"
      echo
   fi
done
