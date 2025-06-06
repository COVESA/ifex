# This is a simple test framework to be able to define various types of
# unit/regression tests with a minimal amount of work.  It is favoring
# files-on-filesystem as definitions, which is a little unusual, but the result
# is flexible and space efficient.
#
# This test runner program takes one argument - the testdef directory.  It
# executes tests that are defined by files and directories _existing_ on the
# file system, in the given testdef directory.
#
# Possible files or symlinks: program, module, function
# Possible directories: inputs/, results/
#
# Directories
#
# inputs/: Contains files to be passed, one at a time, to a program or function.  This can be a symlink to another dir
# results/: Contains files with the same names as the input files plus the suffix ".out", used for comparison *if* the success condition is defined to "compare_results".
#
# Program Execution:
#
# - If the file named 'program' is a symlink, then call the linked program for each input file.
# - If 'program' is not a symlink but a file, read the program name as text from the first line in the file.
#
# This allows also adding additional fixed arguments to the program invocation:
#    myprogram arg1 arg2 ...
#
# The arguments given here will be fixed arguments = the same for each
# invocation of the program on different input files.  Note that it is not
# possible to specify a location of the input file argument -> the input file
# will always passed as the *last* argument to the program.  Adjust the program
# accordingly (or write a shellscript wrapper that changes the order of
# arguments, if needed)
#
# For all program execution, the program must return success/fail through its
# exit code (zero or non-zero), and the standard-output will be collected and
# used for comparison.
#
# Module and Function Execution:
#
# If a file named 'module' exists, it shall be a symlink to a Python file (module).
# A file named 'function' must also exists.  The name of the function is specified on the first line of this file.
# The testrunner will call this function on the imported module, passing each input file as input.
#
# Note that the test function must accept only one argument (input file name/path).  Adjust accordingly.
#
# For module/function execution, the output is expected to be a *return parameter* from the function, and standard output will not be collected.
#
#
# Success Conditions
#
# This is determined by *one* file existing with the name 'expect_success', 'expect_failure', or 'compare_results'.
#
# For the first two, the program exit code will used for programs, and for a python function test the absence of Exceptions is considered success.
#
# For 'compare_results', success means the output matches exactly the content of the corresponding file (+ ".out") in the results/ directory.

import importlib.util
import os
import subprocess
import sys
import pytest

global TESTDEF_DIR

def is_link(f):
   p = os.path.join(TESTDEF_DIR, f)
   return os.path.islink(p)

def is_file(f):
   p = os.path.join(TESTDEF_DIR, f)
   return os.path.isfile(p)

def get_program_link(f):
   p = os.path.join(TESTDEF_DIR, 'program')
   return os.readlink(p)

def get_program_args_from_file():
   p = os.path.join(TESTDEF_DIR, 'program')
   return read_file_line(p).split()  # Note expect no spaces in args

def get_module():
    p = os.path.join(TESTDEF_DIR, 'module')
    link = os.readlink(p)
    # Relative link must be considered to be starting from the testdef directory:
    if not os.path.isabs(link):
        link = os.path.join(TESTDEF_DIR, link)
    return link

def get_function_name():
    p = os.path.join(TESTDEF_DIR, 'function')
    with open(p, 'r') as f:
        return f.readline().strip()

def get_corresponding_resultfile(input_file):
    parts = os.path.split(input_file)
    fileonly = parts[1]
    inputdir = parts[0]
    # Construct resultsdir and file
    return os.path.join(inputdir, "..", "results", fileonly + ".out")

def run_test_on_inputs(testfunction):
    p = os.path.join(TESTDEF_DIR, 'inputs')
    input_files = [os.path.join(p, f) for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    final_result = True
    for file in input_files:
        success, output, file = check_result(testfunction(file))
        print(f"Test {file}: {'Success' if success else 'Failure'}")
        if not success:
            return False, output
    return True, ""

def check_result(args):
    exit_code, output, file = args
    if is_file('expect_success'):
        return exit_code == 0, "", file
    elif is_file('expect_failure'):
        return exit_code != 0, "", file
    elif is_file('compare_results'):
        rfile = get_corresponding_resultfile(file)
        with open(rfile, 'r') as f:
            expected = f.read()
        return output.strip() == expected.strip(), output, file
    return False, output, file

def read_file(file):
    with open(file, 'r') as f:
        return f.read()

def read_file_line(file):
    with open(file, 'r') as f:
        return f.readline().strip()

def run_tests(test_root_dir):
    #defs = ['program', 'module', 'function', 'inputs/', 'results/', 'expect_success', 'expect_failure', 'compare_results']

    # args: program path and input_file path
    def run_executable(program : str, input_file : str):
        result = subprocess.run([program, input_file], capture_output=True, text=True)
        return result.returncode, result.stdout, input_file

    # args: Array of program name/path + fixed arguments that must be passed before the input-file argument
    # and then the input_file argument
    def run_executable2(program_args : [str], input_file : str):
        # Run program and "fixed" arguments (in program_args array) and add variable input_file as the last argument
        result = subprocess.run(program_args + [input_file], capture_output=True, text=True)
        return result.returncode, result.stdout, input_file

    # input: Reference to callable (python function), then the input_file
    def run_py_function(function : callable, input_file : str):
        try:
            output = function(input_file)
            exit_code = 0
        except Exception as e:
            print(f"EXCEPTION during {function=}")
            output = str(e)
            print(f"{output=}")
            exit_code = 1

        return exit_code, output, input_file


        # Fail if we are unable?
        #return -1, "NOTRUN", "NOFILE"
        raise Exception()

    # Symlink -> points to the program to run
    if is_link('program'):
        program = get_program_link()
        print("Tested program is: {program}")
        testfunction = lambda file : run_executable(program, file)

    # A text file -> it will contain the name/path of the program to run
    # ... followed by any "fixed" arguments to pass before the input file
    # (Input file must always be the last argument -> adjust program or make a wrapper script accordingly)
    elif is_file('program'):
        program_args = get_program_args_from_file()
        print("Tested program is: {program_args} <input_file>")
        testfunction = lambda file : run_executable2(program_args, file)

    # If module exists, it shall be a symlink to the python module file
    # ... then the 'function' is expected to have the name of the function to call on that module
    elif is_link('module') and is_file('function'):
        # Follow symlink to get path to module
        module_path = get_module()
        # Name only, and drop the .py extension
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        # Import this module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the function name from the file function
        fname = get_function_name()
        function = getattr(module, fname)
        print(f"Tested function is: {fname} from module {module_path}")

        # Set up test to call the python function on each input file
        testfunction = lambda file: run_py_function(function, file)

    else:
        raise Exception(f"Malformed test definition in {test_root_dir=}")

    # testfunction set up above -> run it.
    result, output = run_test_on_inputs(testfunction)

    return result


def define_testdef_dir(d):
    global TESTDEF_DIR
    if os.path.isabs(d):
        TESTDEF_DIR = d
    else:
        TESTDEF_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), d)


# Wrapper to be picked up by pytest - loops over *all* testdefs
tdroot = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdefs")
tddirs = [d for d in os.listdir(tdroot) if os.path.isdir(os.path.join(tdroot, d))]
@pytest.mark.parametrize('d', tddirs)
def test_generic_runner(d):
    # This function takes d as name-only because it looks better in pytest output
    # Therefore, here convert to abspath actual dir again:
    tdroot = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdefs")
    tddir = os.path.abspath(os.path.join(tdroot, d))
    define_testdef_dir(tddir) # Yeah, ugly global var remains here, refactor someday...
    assert(run_tests(tddir))


# Invoked interactive or by shell script - expects *one* testdef dir as argument!
if __name__ == "__main__":
    global TESTDEF_DIR

    define_testdef_dir(sys.argv[1])

    if not run_tests(TESTDEF_DIR):
        sys.exit(1)
