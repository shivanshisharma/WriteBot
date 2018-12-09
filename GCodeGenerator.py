#!/usr/bin/python

"""
    engrave-lines.py G-Code Engraving Generator for command-line usage
    (C) ArcEye <2012>  <arceye at mgware dot co dot uk>
    syntax  ---   see helpfile below
    
    Allows the generation of multiple lines of engraved text in one go
    Will take each string arguement, apply X and Y offset generating code until last line done
    
  
    based upon code from engrave-11.py
    Copyright (C) <2008>  <Lawrence Glaister> <ve7it at shaw dot ca>
                     based on work by John Thornton  -- GUI framwork from arcbuddy.py
                     Ben Lipkowitz  (fenn)-- cxf2cnc.py v0.5 font parsing code

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    Rev v2 21.06.2012 ArcEye
"""
# change this if you want to use another font
from Tkinter import *
from math import *
import os
import re
import sys
import string
import getopt
import math

String =   ""
SafeZ =    2
XStart =   0
XLineOffset =   0
XIndentList = ""
YStart = 0
YLineOffset = 0
Depth =    0.1
XScale =   1
YScale =   1
CSpaceP =  25
WSpaceP=   100
Angle =    0
Mirror = 0
Flip = 0
stringlist = []

#=======================================================================
class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%s" % (self.stroke_list)

    def get_xmax(self):
        try: return max([s.xmax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymax(self):
        try: return max([s.ymax for s in self.stroke_list[:]])
        except ValueError: return 0



#=======================================================================
class Line:

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)

    def __repr__(self):
        return ("Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend))

#=======================================================================
class GCodeGenerator:
    
    def generateGCode(self, text, fontName):
        #erase old gcode as needed
        gcode = []      
        oldx = oldy = -99990.0      
                     
        gcode.append( 'G0 Z%.4f~' %(SafeZ))
        font = self.parse(fontName)

        font_line_height = max(font[key].get_ymax() for key in font)
        font_word_space =  max(font[key].get_xmax() for key in font) * (WSpaceP/100.0)
        font_char_space = font_word_space * (CSpaceP /100.0)

        xoffset = 0                 # distance along raw string in font units
        # calc a plot scale so we can show about first 15 chars of string
        # in the preview window
        PlotScale = 15 * font['A'].get_xmax() * XScale / 150

        for char in text:
            if char == ' ':
                xoffset += font_word_space
                continue
            try:
                first_stroke = True
                for stroke in font[char].stroke_list:
    #               gcode.append("(%f,%f to %f,%f)" %(stroke.xstart,stroke.ystart,stroke.xend,stroke.yend ))
                    dx = oldx - stroke.xstart
                    dy = oldy - stroke.ystart
                    dist = sqrt(dx*dx + dy*dy)

                    x1 = stroke.xstart + xoffset
                    y1 = stroke.ystart
                    if Mirror == 1:
                        x1 = -x1
                    if Flip == 1:
                        y1 = -y1

                    # check and see if we need to move to a new discontinuous start point
                    if (dist > 0.001) or first_stroke:
                        first_stroke = False
                        #lift engraver, rapid to start of stroke, drop tool
                        gcode.append("G0 Z%.4f~" %(SafeZ))
                        gcode.append(self.getGCode(0, x1, y1, XStart, YStart))
                        gcode.append("G1 Z%.4f~" %(Depth))

                    x2 = stroke.xend + xoffset
                    y2 = stroke.yend
                    if Mirror == 1:
                        x2 = -x2
                    if Flip == 1:
                        y2 = -y2
                    gcode.append(self.getGCode(1, x2, y2, XStart, YStart))
                    oldx, oldy = stroke.xend, stroke.yend

                # move over for next character
                char_width = font[char].get_xmax()
                xoffset += font_char_space + char_width

            except KeyError:
               print("(warning: character '0x%02X' not found in font defn)" % ord(char))

        gcode.append("G0 Z%.4f~" %(SafeZ))     # final engraver up
        return gcode
    
    def parse(self, fontName):
        font = {}
        key = None
        num_cmds = 0
        line_num = 0
        fileContents = []
        with open("fonts/%s.cxf" %(fontName)) as file:
            fileContents = file.readlines()
        for text in fileContents:
            #format for a typical letter (lowercase r):
            ##comment, with a blank line after it
            #
            #[r] 3
            #L 0,0,0,6
            #L 0,6,2,6
            #A 2,5,1,0,90
            #
            line_num += 1
            end_char = re.match('^$', text) #blank line
            if end_char and key: #save the character to our dictionary
                font[key] = Character(key)
                font[key].stroke_list = stroke_list
                font[key].xmax = xmax
                if (num_cmds != cmds_read):
                    print ("(warning: discrepancy in number of commands %s, line %s, %s != %s )" % (fontfile, line_num, num_cmds, cmds_read))

            new_cmd = re.match('^\[(.*)\]\s(\d+)', text)
            if new_cmd: #new character
                key = new_cmd.group(1)
                num_cmds = int(new_cmd.group(2)) #for debug
                cmds_read = 0
                stroke_list = []
                xmax, ymax = 0, 0

            line_cmd = re.match('^L (.*)', text)
            if line_cmd:
                cmds_read += 1
                coords = line_cmd.group(1)
                coords = [float(n) for n in coords.split(',')]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])

            arc_cmd = re.match('^A (.*)', text)
            if arc_cmd:
                cmds_read += 1
                coords = arc_cmd.group(1)
                coords = [float(n) for n in coords.split(',')]
                xcenter, ycenter, radius, start_angle, end_angle = coords
                # since font defn has arcs as ccw, we need some font foo
                if ( end_angle < start_angle ):
                    start_angle -= 360.0
                # approximate arc with line seg every 20 degrees
                segs = int((end_angle - start_angle) / 20) + 1
                angleincr = (end_angle - start_angle)/segs
                xstart = cos(start_angle * pi/180) * radius + xcenter
                ystart = sin(start_angle * pi/180) * radius + ycenter
                angle = start_angle
                for i in range(segs):
                    angle += angleincr
                    xend = cos(angle * pi/180) * radius + xcenter
                    yend = sin(angle * pi/180) * radius + ycenter
                    coords = [xstart,ystart,xend,yend]
                    stroke_list += [Line(coords)]
                    xmax = max(xmax, coords[0], coords[2])
                    ymax = max(ymax, coords[1], coords[3])
                    xstart = xend
                    ystart = yend
        return font
    
    def getGCode(self, z, x, y, xStart, yStart):
        xScale = 0.4000
        yScale = 0.5000
        angle = 0.0000
        rotatedX = 0.0000
        rotatedY = 0.0000
        
        scaledX = x*xScale
        scaledY = y*yScale
        distanceOfXYFromZero = math.sqrt(((scaledX*scaledX) + (scaledY*scaledY)))
        if x != 0:
            directionToXY = math.atan(scaledY/scaledX)
            rotatedX = distanceOfXYFromZero * (math.cos((directionToXY + angle)))
            rotatedY = distanceOfXYFromZero * (math.sin((directionToXY + angle)))
        
        if z < 0.5:
            return "G00 X%.4f Y%.4f~" %((rotatedX + xStart), (rotatedY + yStart))
        else:
            return "G01 X%.4f Y%.4f~" %((rotatedX + xStart), (rotatedY + yStart))
