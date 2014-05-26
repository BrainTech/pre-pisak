#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of AT-Platform.
#
# AT-Platform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AT-Platform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AT-Platform. If not, see <http://www.gnu.org/licenses/>.

class reader():
    def __init__(self):
        self.parameters = []

    #-------------------------------------------------------------------------    
    def readParameters(self):
        with open( './.pathToATPlatform' ,'r' ) as textFile:
            pathToATPlatform = textFile.readline( )

        with open( pathToATPlatform + 'parameters', 'r' ) as parametersFile:
            for line in parametersFile:
                self.parameters.append( "".join( line.split() ) )
    
    #-------------------------------------------------------------------------
    def getParameters(self):
        return self.parameters

		
