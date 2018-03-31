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

For help, just run ``python ./rtSimReadDeposit.py -h``

Example usage
``python ./rtSimReadDeposit.py -i /path/to/fast5/files -o /path/to/destination -s 100``

The above example will simulate at 100x the speed of the actual
experimet.

It is also very common that you will want to simulate the experiment
multiple times for the same samples. As the building of the index list
is the longest part of the process, the first the time the above example
is run, it will save a file called ``file_order.p`` into the destination
directory. This is a python pickle file and is effectively a list sorted
in order of first file to be deposited to the last. Each element in the
list is a tuple ``(time, filepath)`` with time being the number of
seconds after the initial file that the file was produced.

So to speed things up, if you have the pickle file already you can
simulate the experiment from the example above again by running
``python ./rtSimReadDeposit.py -p /path/to/pickle/file -o /path/to/destination -s 100``

Any files that cause an ``IOError``, such as corrupt files (which do
happen), will be written to a text file with the file path and
associated error message.

If you want to generate the pickle file and not start the copying of
files you just run the command without the ``-o`` and ``-s`` flags.

To load the pickle file into Python for some other use you can use the
following example:

.. code:: python

    def get_pickle(file_):
        with open(file_, 'rb') as fp:
            return pickle.load(fp)
    xs = get_pickle(pickle_file) # list is now stored in xs

**NB:** this program is still under very active development so make sure
you ``pull`` from the clone regularly to keep up-to-date and *PLEASE*
raise any issues that you come across.

Big disclaimer
~~~~~~~~~~~~~~

For anyone who has worked with ``fast5`` file structure before I am sure
I don’t have to explain to you how volatile this structure is! In other
words: **in now way do I guarentee this will work on all fast5 files.**
I have tested it out with a few different versions of files produced by
MinKnow (should work with any MinKnow version from arounf post-R9
chemistry), but trying to test *all* would be wasting time I could be
putting towards something enjoyable. If it doesn’t work for your files
feel free to fork this and tweak it to suite your needs. Or send me some
sample ``fast5`` files and if I have time I will add in some support for
it…..maybe….



* Free software: MIT license
* Documentation: https://taeper.readthedocs.io.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
