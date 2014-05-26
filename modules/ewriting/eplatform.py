#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of EPlatform.
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

import os, sys
import wx
import wx.lib.buttons as bt
from pymouse import PyMouse

from pygame import mixer

import EGaps, EMatch

#=============================================================================
class cwiczenia(wx.Frame):
	def __init__(self, parent, id):
		
		self.winWidth, self.winHeight = wx.DisplaySize( )
		
		wx.Frame.__init__( self , parent , id , 'e-platform main menu')
                style = self.GetWindowStyle( )
		self.SetWindowStyle( style | wx.STAY_ON_TOP ) 
		self.parent = parent

		self.Maximize( True )
		self.Centre( True )
		self.MakeModal( True )
		
		self.initializeParameters( )
		self.initializeBitmaps( )
		self.createGui( )
		self.createBindings( )

		self.initializeTimer( )

	#-------------------------------------------------------------------------	
	def initializeParameters(self):

		with open( './.pathToATPlatform' ,'r' ) as textFile:
			self.pathToATPlatform = textFile.readline( )

		sys.path.append( self.pathToATPlatform )
		from reader import reader
		
		reader = reader()
		reader.readParameters()
		parameters = reader.getParameters()

		for item in parameters:
			try:
				setattr(self, item[:item.find('=')], int(item[item.find('=')+1:]))
			except ValueError:
				setattr(self, item[:item.find('=')], item[item.find('=')+1:])

		self.pressFlag = False

		self.numberOfRows = 3,
		self.numberOfColumns = 1,
		self.numberOfIteration = 0
		self.maxNumberOfIteration = 2 * self.numberOfRows[0]

		self.flaga = 0
		
		if self.control != 'tracker':
			self.mouseCursor = PyMouse( )
			self.mousePosition = self.winWidth - 8 - self.xBorder, self.winHeight - 8 - self.yBorder
			self.mouseCursor.move( *self.mousePosition )			
							
		if self.switchSound.lower( ) == 'on' or self.pressSound.lower( ) == 'on':
			mixer.init( )
			if self.switchSound.lower( ) == 'on':
				self.switchingSound = mixer.Sound( self.pathToATPlatform + '/sounds/switchSound.wav' )
			if self.pressSound.lower( ) == 'on':
				self.pressingSound = mixer.Sound( self.pathToATPlatform + '/sounds/pressSound.wav' )

                self.poczatek = True
		self.numberOfPresses = 1

	#-------------------------------------------------------------------------	
        def initializeBitmaps(self):
            
		self.functionButtonPath = [ wx.BitmapFromImage( wx.ImageFromStream( open(self.pathToATPlatform + 'icons/back.png', 'rb' ) ) ) ]

		self.functionButtonName = [ 'back' ]

	#-------------------------------------------------------------------------	
	def initializeTimer(self):

                id1 = wx.NewId( )
                wx.RegisterId( id1 )
		self.stoper = wx.Timer( self, id1 )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper,id1 )

		if self.control != 'tracker':
			self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------	
	def createGui(self):

		self.mainSizer = wx.GridBagSizer( self.xBorder, self.yBorder )

                nazwy = [ u'UZUPEŁNIJ LUKĘ',u'NAZWIJ OBRAZEK' ]
                kolory = [ 'indian red', 'yellow' ]

		b = bt.GenButton( self, -1, nazwy[ 0 ], name = nazwy[ 0 ])
		b.SetFont( wx.Font( 75, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
		b.SetBezelWidth( 3 )
		b.SetBackgroundColour( self.backgroundColour )
		b.SetForegroundColour( kolory[ 0 ] )
		b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
		self.mainSizer.Add( b, ( 0, 0 ), wx.DefaultSpan, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = self.xBorder )

		b = bt.GenButton( self, -1, nazwy[ 1 ], name = nazwy[ 1 ])
		b.SetFont( wx.Font( 75, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
		b.SetBezelWidth( 3 )
		b.SetBackgroundColour( self.backgroundColour )
		b.SetForegroundColour( kolory[ 1 ] )
		b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
		self.mainSizer.Add( b, ( 1, 0 ), wx.DefaultSpan, wx.EXPAND | wx.LEFT | wx.RIGHT, border = self.xBorder )

		b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 0 ], name = self.functionButtonName[ 0 ] )
		b.SetBackgroundColour( self.backgroundColour )
		b.SetBezelWidth( 3 )
		b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
		self.mainSizer.Add( b, ( 2, 0 ), wx.DefaultSpan, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border = self.xBorder)
		
		for number in range( self.numberOfRows[ 0 ] ):
			self.mainSizer.AddGrowableRow( number )
		for number in range( self.numberOfColumns[ 0 ] ):
			self.mainSizer.AddGrowableCol( number )

                self.SetSizer( self.mainSizer )
                self.SetBackgroundColour( 'black' )
		self.Layout( )
		self.Refresh( )
		self.Center( )
		self.MakeModal( True )
		self.flaga = 0

	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE , self.OnCloseWindow )

	#-------------------------------------------------------------------------	
	def OnCloseWindow(self, event):

		if self.control != 'tracker':
			self.mousePosition = self.winWidth/1.85, self.winHeight/1.85	
			self.mouseCursor.move( *self.mousePosition )	

		dial = wx.MessageDialog(None, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal( )
		
		if ret == wx.ID_YES:

			try:
				self.parent.parent.parent.Destroy()
				self.parent.parent.Destroy()
				self.parent.Destroy()
				self.Destroy()

			except AttributeError:
				try:
					self.parent.parent.Destroy()
					self.parent.Destroy()
					self.Destroy()

				except AttributeError:
					try:		
						self.parent.Destroy()
						self.Destroy()

					except AttributeError:
						self.Destroy()
						
		else:
			event.Veto()

			if self.control != 'tracker':
				self.mousePosition = self.winWidth - 8 - self.xBorder, self.winHeight - 8 - self.yBorder
				self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------	
	def onExit(self):
                if self.parent:
                        self.parent.MakeModal( True )
                        self.parent.Show( )
			if self.control == 'tracker':
				self.parent.stoper.Start( 0.15 * self.parent.timeGap )
			else:
				self.parent.stoper.Start( self.parent.timeGap )

                        self.MakeModal( False )
                        self.Destroy( )
                else:
                        self.MakeModal( False )
                        self.Destroy( )

	#-------------------------------------------------------------------------	
	def onPress(self, event):
		
		if self.pressSound.lower( ) == 'on':
			self.pressingSound.play( )

		if self.control == 'tracker':
			if self.pressFlag == False:
				self.button = event.GetEventObject()
				self.button.SetBackgroundColour( self.selectionColour )
				self.pressFlag = True
				self.label = event.GetEventObject().GetName().encode( 'utf-8' )
				self.stoper.Start( 0.15 * self.timeGap )

				if self.label == 'UZUPEŁNIJ LUKĘ':
					self.stoper.Stop( )
					EGaps.cwiczenia( self, id = -1 ).Show( True )
					self.MakeModal( False )
					self.Hide( )

				elif self.label == 'NAZWIJ OBRAZEK':
					self.stoper.Stop( )
					EMatch.cwiczenia( self, id = -1 ).Show( True )
					self.MakeModal( False )
					self.Hide( )

				if self.label == 'back':
					self.onExit( )

		else:
			self.numberOfPresses += 1
			self.numberOfIteration = 0

			if self.numberOfPresses == 1:
				
				items = self.mainSizer.GetChildren( )
				
				if self.flaga == 'rest':
					self.flaga = 0				
				
				else:
					if self.flaga == 0:
						b = items[ 2 ].GetWindow( )

					elif self.flaga == 1:
					       b = items[ 0 ].GetWindow( )

					elif self.flaga == 2:
						b = items[ 1 ].GetWindow( )

					b.SetBackgroundColour( self.selectionColour )
					b.SetFocus( )
					b.Update( )

					if self.flaga == 0 :
						self.onExit( )

					if self.flaga == 1 :
						self.stoper.Stop( )
						EGaps.cwiczenia( self, id = -1 ).Show( True )
						self.MakeModal( False )
						self.Hide( )

					if self.flaga == 2 :
						self.stoper.Stop( )
						EMatch.cwiczenia( self, id = -1 ).Show( True )
						self.MakeModal( False )
						self.Hide( )

			else:
				event.Skip( )

	#-------------------------------------------------------------------------	
	def timerUpdate(self, event):

		if self.control == 'tracker':
			
			if self.button.GetBackgroundColour( ) == self.backgroundColour:
				self.button.SetBackgroundColour( self.selectionColour )
				
			else:
				self.button.SetBackgroundColour( self.backgroundColour )	
		
			self.stoper.Stop( )
			self.pressFlag = False

		else:
			self.mouseCursor.move( *self.mousePosition )
			self.numberOfPresses = 0
			
			self.numberOfIteration += 1

			if self.flaga == 'rest':
				pass

			elif self.numberOfIteration > self.maxNumberOfIteration:
				for i in range( 3 ):
					item = self.mainSizer.GetItem( i )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetFocus( )

				self.flaga = 'rest'

			else:
				for i in range( 3 ):
					item = self.mainSizer.GetItem( i )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetFocus( )

				item = self.mainSizer.GetItem( self.flaga )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.scanningColour )
				b.SetFocus( )

				if self.flaga == 2:
					self.flaga = 0
				else:
					self.flaga += 1			
					
				if self.switchSound.lower( ) == 'on':
					self.switchingSound.play( )

#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = cwiczenia( parent = None, id = -1 )
	frame.Show( )
	app.MainLoop( )
