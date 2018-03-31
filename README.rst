======
taeper
======
Simulate repeating a nanopore experiment.

.. image:: https://img.shields.io/pypi/v/taeper.svg
        :target: https://pypi.python.org/pypi/taeper

.. image:: https://img.shields.io/travis/mbhall88/taeper.svg
        :target: https://travis-ci.org/mbhall88/taeper

.. image:: https://readthedocs.org/projects/taeper/badge/?version=latest
        :target: https://taeper.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


This tool is designed for anyone developing tools and applications for
real-time analysis of Oxford Nanopore sequencing data. The use is quite
simple. Given a directory of ``fast5`` files, ``A``, and a destination
directory, ``B``, this tool will copy the files from ``A`` to ``B`` in
the same order and timing as they were deposited into the reads folder
during the actual experiment. It will also maintain the current directory structure.

I know what you’re thinking: “But who wants to hang around for 30 hours
waiting for a simulation to finish?” Luckily there is an optional
scaling factor that will speed up the process (``--scale``).

Installation
=============
This is a **python3 only** package.

To install, simply run

.. code-block:: bash

    pip3 install taeper
    taeper --help

Usage
======

``taeper`` is designed to simulate the order and timing of fast5 files that
were produced in a minION run. You give it an input directory and it will gather
the names of all the fast5 files under that directory (including sub-directories).
It gathers information about the time when each read finished sequencing and
creates a sorted index of all the files. In this index the first file was the first
one sequenced and so on. Attached to each file path is a delay time, ``t`` in seconds.
This specifies that that read completed sequencing ``t`` seconds after the one
before it. In this way ``taeper`` can rerun what the experiment looked like in
terms of the depositing of fast5 files. It then moves those files into a specified
output directory and will recreate any subdirectory structures (e.g pass or fail
folders).

.. code-block:: bash

    taeper --input_dir path/to/reads --output some/place

This will copy all fast5 files in ``path/to/reads`` to ``some/place`` in the
exact same timing as they were produced.

In reality though you probably dont want to wait the full length of time that
would take. In that case you can use the scale option.

.. code-block:: bash

    taeper --input_dir path/to/reads --output some/place --scale 100

This will rerun the experiment 100 times faster.

Indexing is the longest step of the process and therefore, by default, an index
file of the file order with the time delays is stored in a file called ``taeper_index.npy``.
Keep in mind that the file paths in the index are relative to the working directory
it was generated in.

If you would just like to index but not copy you can do

.. code-block:: bash

    taeper --input_dir path/to/reads --dump_index experiment_index.npy

You just omit the output directory. ``--dump_index`` also allows you to specify a
name other than the default for the index.

If you already have an index file and you would like to rerun the experiment then
you can provide that index and skip to the copying

.. code-block:: bash

    taeper --input_dir path/to/reads --output some/place --index experiment_index.npy --scale 100

**Full usage**

.. code-block:: bash

    taeper --help
    usage: taeper [-h] -i INPUT_DIR [--index INDEX] [-o OUTPUT] [--scale SCALE]
              [-d DUMP_INDEX] [--no_index] [--log_level {0,1,2,3,4,5}]
              [--no_progress_bar]

    Simulate the real-time depositing of Nanopore reads into a given folder,
    conserving the order they were processed during sequencing. If pass and fail
    folders do not exist in output_dir they will be created if detected in the
    file path for the fast5 file.

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT_DIR, --input_dir INPUT_DIR
                            Directory where files are located.
      --index INDEX         Provide a prebuilt index file to skip indexing. Be
                            aware that paths within an index file are relative to
                            the current working directory when they were built.
      -o OUTPUT, --output OUTPUT
                            Directory to copy the files to. If not specified, will
                            generate the index file only.
      --scale SCALE         Amount to scale the timing by. i.e scale of 10 will
                            deposit the reads 10x fatser than they were generated.
                            (Default = 1.0)
      -d DUMP_INDEX, --dump_index DUMP_INDEX
                            Path to save index as. Default is 'taeper_index.npy'
                            in current working directory. Note: Paths in the index
                            are relative to the current working directory.
      --no_index            Dont write the index list to file. This will mean it
                            needs regenerating for this dataset on each run.
      --log_level {0,1,2,3,4,5}
                            Level of logging. 0 is none, 5 is for debugging.
                            Default is 4 which will report info, warnings, errors,
                            and critical information.
      --no_progress_bar     Do not display progress bar.


Disclaimer
~~~~~~~~~~~~~~

The ``fast5`` file structure has changed a bit over time and as such not all
files will work. Although, I have tested this program with most recent forms and
it works fine. A logging warning will show up on the console if ``taeper`` is
unable to read a file or determine it's finish time.

-----------

* Free software: MIT license
* Documentation: https://taeper.readthedocs.io.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
