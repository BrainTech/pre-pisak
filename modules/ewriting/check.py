#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of AT-Platform.
#
# EPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EPlatform. If not, see <http://www.gnu.org/licenses/>.


import wxversion
wxversion.select('2.8')

import os

import wx
import wx.lib.buttons as bt

from pymouse import PyMouse
from pygame import mixer
import numpy as np

#=============================================================================
class check(wx.Frame):

	def __init__(self, parent):

		self.winWidth, self.winHeight = wx.DisplaySize( )
                
		self.parent = parent
		self.initializeParameters( )
		self.createGui( )
		self.parent.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------
	def initializeParameters(self):

		with open( './.pathToATPlatform' ,'r' ) as textFile:
			self.pathToATPlatform = textFile.readline( )

		with open( self.pathToATPlatform + 'parameters', 'r' ) as parametersFile:
			for line in parametersFile:

				if line[ :line.find('=')-1 ] == 'timeGap':
					self.timeGap = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'backgroundColour':
					self.backgroundColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'textColour':
					self.textColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'scanningColour':
					self.scanningColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'selectionColour':
					self.selectionColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'filmVolume':
					self.filmVolumeLevel = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'musicVolume':
					self.musicVolumeLevel = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'control':
					self.control = line[ line.rfind('=')+2:-1 ]

				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w linii', line
					
					self.timeGap = 1500
					self.backgroundColour = 'white'
					self.textColour = 'black'
					self.scanningColour =  '#E7FAFD'
					self.selectionColour = '#9EE4EF'
					self.filmVolumeLevel = 100
					self.musicVolumeLevel = 70
					self.control = 'switch'

		with open( self.pathToATPlatform + 'spellerParameters', 'r' ) as parametersFile:
			for line in parametersFile:
				
				if line[ :line.find('=')-1 ] == 'voice':
					self.voice = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'vowelColour':
					self.vowelColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'polishLettersColour':
					self.polishLettersColour = line[ line.rfind('=')+2:-1 ]
			
				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w pliku spellerParameters w linii', line
				    
					self.voice = False
					self.vowelColour = 'red'
					self.polishLettersColour = 'blue'

                with open( self.pathToATPlatform + 'ewritingParameters', 'r' ) as parametersFile:
			for line in parametersFile:                                                                

                                if line[ :line.find('=')-1 ] == 'textSize':
					self.textSize = int( line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'maxPoints':
					self.maxPoints = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'checkTime':
                                        self.checkTime = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'colorGrat':
					self.colorGrat = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'colorNiest':
                                        self.colorNiest = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'ileLuk':
                                        self.ileLuk = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'sex':
                                        self.sex = line[ line.rfind('=')+2:-1 ]
		
				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w linii', line
					
					self.textSize = 80
					self.checkTime = 8000
					self.colorGrat = 'lime green'
					self.colorNiest = 'indian red'
					self.ileLuk = 1
					self.maxPoints = 2
					self.sex = 'D'

		mixer.init( )

	#-------------------------------------------------------------------------
	def createGui(self):
	
                self.subSizer = wx.GridSizer( 1, 1, 0, 0 )
                self.subSizer2 = wx.GridSizer( 1, 1, 0, 0 )

		if self.control != 'tracker':
			self.event = eval('wx.EVT_LEFT_DOWN')
		else:
			self.event = eval('wx.EVT_BUTTON')

                if self.parent.ownWord == self.parent.WORD:
                        self.parent.result += 1

                        if self.parent.result == self.parent.maxPoints:

                                if self.sex == 'M':
                                        text = u'BRAWO! \n \nZDOBYŁEŚ WSZYSTKIE PUNKTY. \n \nPRZYCIŚNIJ ŻEBY ODEBRAĆ NAGRODĘ.'
                                else:
                                        text = u'BRAWO! \n \nZDOBYŁAŚ WSZYSTKIE PUNKTY. \n \nPRZYCIŚNIJ ŻEBY ODEBRAĆ NAGRODĘ.'

                                kolor = 'dark slate blue'
                                self.app = False
                                self.oklaski = True
                                i = wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform+'/icons/ewriting/thumbup.png', "rb" ) ) )
                                be = bt.GenBitmapButton( self.parent, -1, bitmap = i )
                                be.SetBackgroundColour( 'white' )
                                be.Bind( self.event, self.reward )

                        else:
                                if self.sex =='M':
                                        text = u'GRATULACJE! \n \nWPISAŁEŚ POPRAWNE SŁOWO!'
                                else:
                                        text = u'GRATULACJE! \n \nWPISAŁAŚ POPRAWNE SŁOWO!'

                                kolor = self.colorGrat
                                self.app = True
                                self.oklaski = True
                                i=wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + '/icons/ewriting/thumbup.png', "rb" ) ) )
                                be = bt.GenBitmapButton( self.parent, -1, bitmap = i )
                                be.SetBackgroundColour( 'white' )
				be.Bind( self.event, self.zamknij )

                else:
                        text = u'NIESTETY. \n \nSPRÓBUJ JESZCZE RAZ!'
                        kolor = self.colorNiest
			self.parent.PicNr -= 1
			self.app = True
			self.oklaski = False

			i = wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + '/icons/ewriting/sad.png', "rb" ) ) )
                        be = bt.GenBitmapButton( self.parent, -1, bitmap = i )
                        be.SetBackgroundColour( 'white' )
			be.Bind( self.event, self.zamknij )
			
		b = bt.GenButton( self.parent, -1, text )
		b.SetFont( wx.Font(50, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		b.SetBezelWidth( 3 )
		
		if self.parent.result == self.parent.maxPoints:
			self.parent.result = 0
			b.Bind( self.event, self.reward )
		else:
			b.Bind( self.event, self.zamknij )

		b.SetBackgroundColour( 'white' )
		b.SetForegroundColour( kolor)
		b.SetFocus( )
		
		self.subSizer.Add( b, 0, wx.EXPAND )
		self.subSizer2.Add( be, 0, wx.EXPAND )
		self.parent.mainSizer.Add( self.subSizer, proportion = 7, flag = wx.EXPAND )
		self.parent.mainSizer.Add(self.subSizer2, proportion = 3, flag = wx.EXPAND )
		self.parent.SetSizer( self.parent.mainSizer )
		self.parent.Layout( )

		# if self.app:
                #         self.parent.stoper3.Start( self.checkTime )

		if self.oklaski:
                        mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/oklaski.ogg' )
                        mixer.music.play( )


                self.ileklik = 0

	#------------------------------------------------------------------------
	def reward(self, event):

                self.parent.mainSizer.Clear( deleteWindows = True )
                self.subSizer = wx.GridSizer( 1, 1, 0, 0)

                b = bt.GenButton( self.parent, -1, u'CHCESZ WYŁĄCZYĆ?\n \nPRZYCIŚNIJ.' )
		b.SetFont( wx.Font(25, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		b.SetBezelWidth( 3 )
		b.SetBackgroundColour( 'white' )
		b.Bind( self.event, self.OnExit)

		self.subSizer.Add( b, 0, wx.EXPAND )
                self.parent.mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND )
                self.parent.SetSizer( self.parent.mainSizer )
                self.parent.Layout( )

                path = self.pathToATPlatform+'multimedia/ewriting/rewards/'
                song = os.listdir( path )[ np.random.randint( 0, len( os.listdir( path ) ), 1 ) ]
                mixer.music.stop( )
                mixer.music.load( path + song )
                mixer.music.play( )
                
	#-------------------------------------------------------------------------
        def OnExit(self, event):

                self.ileklik += 1

                if self.ileklik == 1:
                        mixer.music.stop( )
                        self.parent.back( )
		else:
                        event.Skip( )

	#-------------------------------------------------------------------------
	def zamknij(self, event):

		self.parent.back( )

                if self.oklaski:
                        mixer.music.stop( )
