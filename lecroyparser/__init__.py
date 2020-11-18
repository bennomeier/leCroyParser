""" leCroyParser.py
(c) Benno Meier, 2018 published under an MIT license.

leCroyParser.py is derived from the matlab programme ReadLeCroyBinaryWaveform.m,
which is available at Matlab Central.
a useful resource for modifications is the LeCroy Remote Control Manual
available at http://cdn.teledynelecroy.com/files/manuals/dda-rcm-e10.pdf
------------------------------------------------------
Original version (c)2001 Hochschule fr Technik+Architektur Luzern
Fachstelle Elektronik
6048 Horw, Switzerland
Slightly modified by Alan Blankman, LeCroy Corporation, 2006

Further elements for the code were taken from pylecroy, written by Steve Bian

lecroyparser defines the ScopeData object.
Tested in Python 2.7 and Python 3.6

Updated 2020 Jeroen van Oorschot, Eindhoven University of Technology
"""

import sys
import numpy as np
import glob


class ScopeData(object):
    def __init__(self, path=None, data=None, parseAll=False, sparse=-1):
        """Import Scopedata as stored under path.

        If parseAll is set to true, search for all files 
        in the folder commencing with C1...Cx and store the y data in a list.

        If a positive value is provided for sparse, then only #sparse elements will 
        be stored in x and y. These will be sampled evenly from all data points in
        the source file. This can speed up data processing and plotting."""

        if path:
            if data:
                raise Exception('Both data and path supplied. Choose either one.')

            self.path = path

            if parseAll:
                basePath = "/".join(path.split("/")[:-1])
                core_filename = path.split("/")[-1][2:]

                files = sorted(list(glob.iglob(basePath + "/C*" + core_filename)))

                self.y = []
                for f in files:
                    x, y = self.parseFile(f, sparse=sparse)
                    self.x = x
                    self.y.append(y)

            else:
                x, y = self.parseFile(path, sparse=sparse)
                self.x = x
                self.y = y
        elif data:
            if path:
                raise Exception('Both data and path supplied. Choose either one.')
            if parseAll:
                raise Exception('parseAll option is not available using data input')

            assert type(data) == bytes, 'Please supply data as bytes'
            self.path = 'None - from bytes data'  # not reading from a path
            self.x, self.y = self.parseData(data, sparse)

    def parseFile(self, path, sparse=-1):
        self.file = open(path, mode='rb')

        fileContent = self.file.read()

        self.file.close()
        del self.file
        return self.parseData(data=fileContent, sparse=sparse)

    def parseData(self, data, sparse):
        self.data = data

        self.endianness = "<"

        waveSourceList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Unknown"]
        verticalCouplingList = ["DC50", "GND", "DC1M", "GND", "AC1M"]
        bandwidthLimitList = ["off", "on"]
        recordTypeList = ["single_sweep", "interleaved", "histogram", "graph",
                          "filter_coefficient", "complex", "extrema", "sequence_obsolete",
                          "centered_RIS", "peak_detect"]
        processingList = ["No Processing", "FIR Filter", "interpolated", "sparsed",
                          "autoscaled", "no_resulst", "rolling", "cumulative"]

        # convert the first 50 bytes to a string to find position of substring WAVEDESC
        self.posWAVEDESC = self.data[:50].decode("ascii", "replace").index("WAVEDESC")

        self.commOrder = self.parseInt16(34)  # big endian (>) if 0, else little
        self.endianness = [">", "<"][self.commOrder]

        self.templateName = self.parseString(16)
        self.commType = self.parseInt16(32)  # encodes whether data is stored as 8 or 16bit

        self.waveDescriptor = self.parseInt32(36)
        self.userText = self.parseInt32(40)
        self.trigTimeArray = self.parseInt32(48)
        self.waveArray1 = self.parseInt32(60)

        self.instrumentName = self.parseString(76)
        self.instrumentNumber = self.parseInt32(92)

        self.traceLabel = "NOT PARSED"
        self.waveArrayCount = self.parseInt32(116)

        self.verticalGain = self.parseFloat(156)
        self.verticalOffset = self.parseFloat(160)

        self.nominalBits = self.parseInt16(172)

        self.horizInterval = self.parseFloat(176)
        self.horizOffset = self.parseDouble(180)

        self.vertUnit = "NOT PARSED"
        self.horUnit = "NOT PARSED"

        self.triggerTime = self.parseTimeStamp(296)
        self.recordType = recordTypeList[self.parseInt16(316)]
        self.processingDone = processingList[self.parseInt16(318)]
        self.timeBase = self.parseTimeBase(324)
        self.verticalCoupling = verticalCouplingList[self.parseInt16(326)]
        self.bandwidthLimit = bandwidthLimitList[self.parseInt16(334)]
        self.waveSource = waveSourceList[self.parseInt16(344)]

        start = self.posWAVEDESC + self.waveDescriptor + self.userText + self.trigTimeArray
        if self.commType == 0:  # data is stored in 8bit integers
            y = np.frombuffer(self.data[start:start + self.waveArray1], dtype=np.dtype((self.endianness + "i1", self.waveArray1)), count=1)[0]
        else:  # 16 bit integers
            length = self.waveArray1 // 2
            y = np.frombuffer(self.data[start:start + self.waveArray1], dtype=np.dtype((self.endianness + "i2", length)), count=1)[0]

        # now scale the ADC values
        y = self.verticalGain * np.array(y) - self.verticalOffset

        x = np.linspace(0, self.waveArrayCount * self.horizInterval,
                        num=self.waveArrayCount) + self.horizOffset

        if sparse > 0:
            indices = int(len(x) / sparse) * np.arange(sparse)

            x = x[indices]
            y = y[indices]

        return x, y

    def unpack(self, pos, formatSpecifier, length):
        """ a wrapper that reads binary data
        in a given position in the file, with correct endianness, and returns the parsed
        data as a tuple, according to the format specifier. """
        start = pos + self.posWAVEDESC
        x = np.frombuffer(self.data[start:start + length], self.endianness + formatSpecifier, count=1)[0]
        return x

    def parseString(self, pos, length=16):
        s = self.unpack(pos, "S{}".format(length), length)
        if sys.version_info > (3, 0):
            s = s.decode('ascii')
        return s

    def parseInt16(self, pos):
        return self.unpack(pos, "u2", 2)

    def parseWord(self, pos):
        return self.unpack(pos, "i2", 2)

    def parseInt32(self, pos):
        return self.unpack(pos, "i4", 4)

    def parseFloat(self, pos):
        return self.unpack(pos, "f4", 4)

    def parseDouble(self, pos):
        return self.unpack(pos, "f8", 8)

    def parseByte(self, pos):
        return self.unpack(pos, "u1", 1)

    def parseTimeStamp(self, pos):
        second = self.parseDouble(pos)
        minute = self.parseByte(pos + 8)
        hour = self.parseByte(pos + 9)
        day = self.parseByte(pos + 10)
        month = self.parseByte(pos + 11)
        year = self.parseWord(pos + 12)

        return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:.2f}".format(year, month, day,
                                                              hour, minute, second)

    def parseTimeBase(self, pos):
        """ time base is an integer, and encodes timing information as follows:
        0 : 1 ps  / div
        1:  2 ps / div
        2:  5 ps/div, up to 47 = 5 ks / div. 100 for external clock"""

        timeBaseNumber = self.parseInt16(pos)

        if timeBaseNumber < 48:
            unit = "pnum k"[int(timeBaseNumber / 9)]
            value = [1, 2, 5, 10, 20, 50, 100, 200, 500][timeBaseNumber % 9]
            return "{} ".format(value) + unit.strip() + "s/div"
        elif timeBaseNumber == 100:
            return "EXTERNAL"

    def __repr__(self):
        string = "Le Croy Scope Data\n"
        string += "Path: " + self.path + "\n"
        string += "Endianness: " + self.endianness + "\n"
        string += "Instrument: " + self.instrumentName + "\n"
        string += "Instrument Number: " + str(self.instrumentNumber) + "\n"
        string += "Template Name: " + self.templateName + "\n"
        string += "Channel: " + self.waveSource + "\n"
        string += "WaveArrayCount: " + str(self.waveArrayCount) + "\n"
        string += "Vertical Coupling: " + self.verticalCoupling + "\n"
        string += "Bandwidth Limit: " + self.bandwidthLimit + "\n"
        string += "Record Type: " + self.recordType + "\n"
        string += "Processing: " + self.processingDone + "\n"
        string += "TimeBase: " + self.timeBase + "\n"
        string += "TriggerTime: " + self.triggerTime + "\n"

        return string


if __name__ == "__main__":
    data = ScopeData(path, parseAll=True)
