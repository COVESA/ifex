This directory contains tests to be run by pytest

To run them, it should be possible to run pytest in the project root:
```bash
$ pytest -v
```

The gen_test.py file will run a few basic tests and it will also run
generation tests defined in subdirectories with the following name patterns
through individual tests:
```
test.<something>
exception.test.<something>
```

In each of these directories, three files are expected:

```
input.yml
template
result
```

(Actually, in the exception case, the result is actually not needed since
 it is supposed to fail before comparing the result)

The code will read `input.yml` and generate output using `template`, and then
compare it to `result`.

Directories named `test.<something>` are required to successfully generate
something that is identical to `result`

Directories named `exception.test.<something>` are expected to throw an
exception during parsing.  In other words a failure during parsing means a
successful test, and otherwise the test fails. (Future change: possibly
support exceptions during generation stage also).


