H5Plot
======

H5Plot is a PyQt5-based viewer for HDF5 data served through `dataserver`.
It lets you browse files, groups, and datasets, inspect attributes, and open
rank-1 traces, rank-2 images, and parametric plots in a dockable plotting area.

Dependencies
------------

Core:

* PyQt5
* numpy
* pyqtgraph
* objectsharer
* dataserver

Demo scripts also use:

* scipy

Quick Start
-----------

Start a dataserver first, then launch the plot window.

```python
from dataserver import run_dataserver
run_dataserver()
```

In another shell:

```python
from H5Plot import run_plotwindow
run_plotwindow()
```

You can also run the window module directly:

```bash
python H5Plot/window.py
```

If you want to talk to an already running plot window from another process:

```python
from H5Plot import plotwindow_client
win = plotwindow_client()
```

This returns the shared `plotwin` interface exposed through `objectsharer`.

Working with data
-----------------

Create or load files through `dataserver`, then add datasets as usual:

```python
from dataserver import get_file

f = get_file('test.h5')
f['dataset'] = [1, 3, 2, 4]
```

If you want a fresh group for each run, use `timestamp_group=True`:

```python
f = get_file('test.h5', timestamp_group=True)
f['dataset'] = [1, 3, 2, 4]
```

The plot window will show:

* rank-1 datasets as line plots
* rank-2 datasets as images
* parametric datasets when the dataset has `parametric=True`

It also supports:

* attribute editing
* show/hide of individual items or whole subtrees
* renaming and deleting items
* multiplots and pairwise parametric plots
* limiting how many plots remain visible at once

Demos
-----

The `demos/` directory contains small examples for the current workflow:

* `simple.py` creates a nested file with one line plot and one image
* `updating.py` shows replacing datasets over time
* `accumulate.py` shows appending to datasets incrementally
* `attrs.py` shows setting plotting attributes like `x0`, `xscale`, `xlabel`, and `ylabel`
* `parametric.py` shows a parametric dataset built from 2D points
* `plot_only.py` shows creating a plot window client and pushing a standalone plot into it

