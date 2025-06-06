import os
import sys
import io

from models.protobuf.protobuf_lark import get_ast_from_proto_file

def find_files(dir_, suffix='.proto'):
    matching_files = []
    for root, dirs, files in os.walk(dir_):
        for file in files:
            if file.endswith(suffix):
                matching_files.append(os.path.join(root, file))
    return matching_files


def run_program_on_all_files(program, paths):
    error_files = []
    outputs = {}

    for f in paths:
        try:
            result = subprocess.run([program, f], capture_output=True, text=True)
            outputs[f] = result.stdout
            if result.returncode != 0:
                error_files.append(f)
        except Exception as e:
            error_files.append(f)
            outputs[f] = str(e)

    return error_files, outputs


def run_function_on_files(func, paths):
    error_files = []
    outputs = {}

    new_stdout = io.StringIO()
    new_stderr = io.StringIO()

    for f in paths:
        try:
            # Capture printouts
            sys.stderr = new_stderr
            sys.stdout = new_stdout
            
            output = func(f)
            captured_output = sys.stdout.getvalue()
            # Store captured output
            s =  "============================== STDERR ===============================\n" + new_stderr.getvalue() + "\n"
            s += "============================== STDOUT ===============================\n" + new_stdout.getvalue() + "\n"
            s += "============================== RETURNED ===============================\n" + str(output) + "\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            outputs[f] = s

            # Temporarily restore original stdout
            # and print progress indicator
            sys.stdout = sys.__stdout__
            print(".", end="", flush=True)
            sys.stdout = new_stdout

        except Exception as e:
            error_files.append(f)
            s =  "============================== STDERR ===============================\n" + new_stderr.getvalue() + "\n"
            s += "============================== STDOUT ===============================\n" + new_stdout.getvalue() + "\n"
            s += "============================== EXCEPTION ===============================\n" + str(e) + "\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            outputs[f] = s


    # Restore stdout
    sys.stdout = sys.__stdout__

    return error_files, outputs


def test_protobuf_parsing():
    testpath = os.path.dirname(os.path.realpath(__file__))
    unit_test_files_dir = os.path.join(testpath, "protobuf/unit_test_files")

    paths = find_files(unit_test_files_dir, ".proto")

    (failed_files, outputs) = run_function_on_files(get_ast_from_proto_file, paths)

    # Lower the amount of printouts under pytest - we primarily need pass/fail
    if "PYTEST_CURRENT_TEST" in os.environ:
        if len(failed_files) != 0:
            print("\nOne *or more* unit-test files (.proto) failed parsing.  Here is the output for the FIRST one only:")
            print(f"File {failed_files[0]} failed with:")
            print(outputs[failed_files[0]])

        # Determine pytest pass/fail
        # For interactive use, don't fail/abort on the assert however
        assert(len(failed_files) == 0)

    # For interactive use however - provide all failures clearly
    else:
        for f in failed_files:
            print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print(f":::FILE::: {f} failed with:")
            print(outputs[f])
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("Not pytest - Skipping assert")



if __name__ == "__main__":
    test_protobuf_parsing()

