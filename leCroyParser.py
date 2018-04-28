# leCroyParser.py
# (c) Benno Meier, 2018
# and published under an MIT license.
#
# leCroyParser.py is derived from the matlab programme ReadLeCroyBinaryWaveform.m,
# which is available at Matlab Central.
# a useful resource for modifications is the LeCroy Remote Control Manual
# available at http://cdn.teledynelecroy.com/files/manuals/dda-rcm-e10.pdf
#------------------------------------------------------
# Original version (c)2001 Hochschule fr Technik+Architektur Luzern
# Fachstelle Elektronik
# 6048 Horw, Switzerland
# Slightly modified by Alan Blankman, LeCroy Corporation, 2006

import struct
import numpy as np
import glob

path = "/Users/benno/Dropbox/RESEARCH/bullet/experiments/scopeTraces/201804/C1180421_typicalShot00000.trc"

class ScopeData(object):
    def __init__(self, path, parseAll = False):
        """Import Scopedata as stored under path.

        If parseAll is set to true, search for all files 
        in the folder commencing with C1...Cx and store the y data in a list."""
        self.path = path

        if parseAll:
            basePath = "/".join(path.split("/")[:-1])
            core_filename = path.split("/")[-1][2:]

            files = sorted(list( glob.iglob(basePath + "/C*" + core_filename)))

            self.y = []
            for f in files:
                x, y = self.parseFile(f)
                self.x = x
                self.y.append(y)
                
        else:
            x, y = self.parseFile(path)
            self.x = x
            self.y = y

        
    def parseFile(self, path):
        self.file = open(path, mode='rb')
        self.endianness = "<"
        
        fileContent = self.file.read()

        waveSourceList = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Unknown"]
        verticalCouplingList = ["DC50", "GND", "DC1M", "GND", "AC1M"]
        bandwidthLimitList = ["off", "on"]
        recordTypeList = ["single_sweep", "interleaved", "histogram", "graph",
                          "filter_coefficient", "complex", "extrema", "sequence_obsolete",
                          "centered_RIS", "peak_detect"]
        processingList = ["No Processing", "FIR Filter", "interpolated", "sparsed",
                          "autoscaled", "no_resulst", "rolling", "cumulative"]
        
        #convert the first 50 bytes to a string to find position of substring WAVEDESC
        self.posWAVEDESC = fileContent[:50].decode("ascii").index("WAVEDESC")

        self.commOrder = self.parseInt16(34) #big endian (>) if 0, else little
        self.endianness = [">", "<"][self.commOrder]
        
        self.templateName = self.parseString(16)
        self.commType = self.parseInt16(32) # encodes whether data is stored as 8 or 16bit


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
        

        self.file.seek(self.posWAVEDESC + self.waveDescriptor + self.userText
                       + self.trigTimeArray)

        if self.commType == 0: #data is stored in 8bit integers
            y = struct.unpack("b"*(self.waveArray1/2),
                                   self.file.read(self.waveArray1))
        else: #16 bit integers
            y = struct.unpack("h"*(self.waveArray1/2),
                                   self.file.read(self.waveArray1))

        #now scale the ADC values
        y = self.verticalGain*np.array(y) - self.verticalOffset
        
        x = np.linspace(0, self.waveArrayCount*self.horizInterval,
                             num = self.waveArrayCount) + self.horizOffset
        
        self.file.close()
        return x, y

        
    def unpack(self, pos, formatSpecifier, length):
        """ a wrapper that reads binary data
        in a given position in the file, with correct endianness, and returns the parsed
        data as a tuple, according to the format specifier. """
        self.file.seek(pos + self.posWAVEDESC)
        return struct.unpack(self.endianness + formatSpecifier, self.file.read(length))
    
        
    def parseString(self, pos):
        return "".join(self.unpack(pos, 'c'*16, 16))

    def parseInt16(self, pos):
        return self.unpack(pos, "h", 2)[0]

    def parseInt32(self, pos):
        return self.unpack(pos, "i", 4)[0]

    def parseFloat(self, pos):
        return self.unpack(pos, "f", 4)[0]

    def parseDouble(self, pos):
        return self.unpack(pos, "d", 8)[0]

    def parseTimeStamp(self, pos):
        [second, minute, hour, day, month, year] = self.unpack(pos, "dbbbbh", 14)

        return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:.2f}".format(year, month, day,
                                                              hour, minute, second)

    def parseTimeBase(self, pos):
        """ time base is an integer, and encodes timing information as follows:
        0 : 1 ps  / div
        1:  2 ps / div
        2:  5 ps/div, up to 47 = 5 ks / div. 100 for external clock"""

        timeBaseNumber = self.parseInt16(pos)

        if timeBaseNumber < 48:
            unit = "pnum k"[timeBaseNumber/9]
            value = [1, 2, 5, 10, 20, 50, 100, 200, 500][timeBaseNumber % 9]
            return "{} ".format(value) + unit.strip() + "s/div"
        elif timeBaseNumber == 100:
            return "EXTERNAL"
           
    def __repr__(self):
        string = "Le Croy Scope Data\n"
        string += "Path: " + self.path + "\n"
        string += "Endianness: " + self.endianness + "\n"
        string += "Instrument: " + self.instrumentName + "\n"
        string += "Instrunemt Number: " + str(self.instrumentNumber) + "\n"
        string += "Template Name: " + self.templateName + "\n"
        string += "Channel: " + self.waveSource + "\n"
        string += "Vertical Coupling: " + self.verticalCoupling + "\n"
        string += "Bandwidth Limit: " + self.bandwidthLimit + "\n"
        string += "Record Type: " + self.recordType + "\n"
        string += "Processing: " + self.processingDone + "\n"
        string += "TimeBase: " + self.timeBase + "\n"
        string += "TriggerTime: " + self.triggerTime + "\n"
        
        return string





if __name__ == "__main__":
    data = ScopeData(path, parseAll = True)

