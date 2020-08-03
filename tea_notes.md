# Notes on tea language refactor ideas

0) Fork and get the tests running. "make test".  Disable any tests that don't work.  Make sure the examples work.
1) Comment out all "globals" which are not needed. Verify that tests that worked still work.  Make sure the examples still work.
2) In api.py create a "TeaRunner" class to contain all globals.

```
class TeaRunner:
  vars_objs = None # include all "globals" in the container.
  ...

    
```
3) Add a *single* global 
```
default_runner = TeaRunner()
```

4) Remove all used globals 
```Python

# @sets global dataset_path and dataaset_obj (of type Dataset)
def data(file, key=None, runner=None):
    #global dataset_path, dataset_obj, dataset_id
    global default_runner
    if runner is None:
        runner = default_runner

    # Require that the path to the data must be a string or a Path object
    assert isinstance(file, (str, Path, pd.DataFrame))
    runner.dataset_path = file
    runner.dataset_id = key

```
5) Make sure the tests still run.  Make sure the examples still run.

6) Do something similar for "solver.py" (steps 2..5 using a SolverContainer class and default_solver global)

7) Add an ability to view a Q/Q plot for normality https://en.wikipedia.org/wiki/Q%E2%80%93Q_plot

