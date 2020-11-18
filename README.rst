lecroyparser
============


leCroyParser.py parses binary files as written by LeCroy scopes.

leCroyParser.py is derived from the matlab program
ReadLeCroyBinaryWaveform.m, available at
<https://www.mathworks.com/matlabcentral/fileexchange/26375-readlecroybinarywaveform-m>,
Original version (c)2001 Hochschule fr Technik+Architektur Luzern
Fachstelle Elektronik 6048 Horw, Switzerland Slightly modified by Alan
Blankman, LeCroy Corporation, 2006

Further elements for the code were taken from pylecroy, written by Steve Bian

A useful resource for modifications is the LeCroy Remote Control Manual
available at
<http://cdn.teledynelecroy.com/files/manuals/dda-rcm-e10.pdf>

Lecroyparser has been tested with Python 2.7 and Python 3.6, 3.8

Installation
------------

lecroyparser is available at pip. It may be installed
with

>>> pip install lecroyparser

or with


>>> easy_install lecroyparser

Usage
-----

To import a single trace, instantiate a ScopeData object by passing it a
path, i.e.

>>> import lecroyparser
>>> path = "/home/benno/Dropbox/RESEARCH/bullet/experiments/scopeTraces/201804/C1180421_typicalShot00000.trc"
>>> data = lecroyparser.ScopeData(path)


The x and y data are stored as numpy arrays in data.x and data.y

Alternatively, to parse several channels set the optional keyword
argument parseAll to True, i.e.

>>> data = lecroyparser.ScopeData(path, parseAll = True)

This will parse all files in the specified folder with a matching
filename. I.e., if the provided path is as above, then the files

.. code-block:: console

   C2180421_typicalShot00000.trc
   C3180421_typicalShot00000.trc
   C4180421_typicalShot00000.trc


will pe parsed as well.

Next to reading files, it is possible to read a binary buffer/string directly. For this, supply the data argument instead of file:

>>> import lecroyparser
>>> path = "/home/benno/Dropbox/RESEARCH/bullet/experiments/scopeTraces/201804/C1180421_typicalShot00000.trc"
>>> contents = open(path, 'rb').read()
>>> data = lecroyparser.ScopeData(data=contents)

This is especially useful when reading data directly from oscilloscope using python-vx11 or similar software.

Additionally, it is possible to limit the number of samples in the output array, by overwriting the sparse keyword:

>>> data = lecroyparser.ScopeData(path, parseAll = True, sparse = 1000)

will limit the samples in the x and y dimensions to 1000.

Information about the file can be obtained by calling print(data)

.. code-block:: console

    >>> print(data)

    Le Croy Scope Data
    Path: /Users/benno/Dropbox/RESEARCH/bullet/experiments/scopeTraces/201804/C1180421\_typicalShot00000.trc
    Endianness: <
    Instrument: LECROYHDO4104
    Instrunemt Number: 19359
    Template Name: LECROY\_2\_3
    Channel: Channel 4
    Vertical Coupling: DC1M
    Bandwidth Limit: on
    Record Type: single\_sweep
    Processing: No Processing &gt;&gt;&gt; TimeBase: 200 ms/div
    TriggerTime: 2018-04-21 11:50:45.76



License
-------

MIT License

Copyright (c) 2018-2020 Benno Meier, Jeroen van Oorschot

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
