#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of Pre-Pisak.
#
# Pre-Pisak is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pre-Pisak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pre-Pisak. If not, see <http://www.gnu.org/licenses/>.

import wxversion
wxversion.select( '2.8' )

import glob, os, time, sys, psutil
import wx, alsaaudio
import wx.lib.buttons as bt
import subprocess as sp
import shlex

from pymouse import PyMouse
from pygame import mixer
from games.atmemory import atmemory
from games.atmemory_hard import atmemory_hard
from games.atsweeper import atsweeper

#=============================================================================
class games( wx.Frame ):
	def __init__(self, parent, id):

	    self.winWidth, self.winHeight = wx.DisplaySize( )
	
            wx.Frame.__init__( self , parent , id, 'ATExercise' )
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

		self.numberOfColumns = 4,
		self.numberOfRows = 2,
		
		self.columnIteration = 0
		self.rowIteration = 0						
		self.panelIteration = 0
		self.emptyColumnIteration = 0
		self.emptyRowIteration = 0
		self.emptyPanelIteration = 0
		self.maxEmptyColumnIteration = 2									
		self.maxEmptyRowIteration = 2									
		self.maxEmptyPanelIteration = 2
		
		self.numberOfPresses = 1
		
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
		
		self.SetBackgroundColour( 'black' )

	#-------------------------------------------------------------------------	
        def initializeBitmaps(self):
		
		self.panels = { 1 : [ [], [] ] }
		self.numberOfPanels = 1
				
		self.functionButtonPath = [ wx.BitmapFromImage( wx.ImageFromStream( open(self.pathToATPlatform + 'icons/back.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open(self.pathToATPlatform + 'icons/games/memo.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream(open(self.pathToATPlatform + 'icons/games/memohard.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream(open(self.pathToATPlatform + 'icons/games/minesweeper.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream(open(self.pathToATPlatform + 'icons/games/pacman.png', 'rb' ) ) ) ]

		self.labels = [ 'memory', 'memoryhard', 'saper' , 'pacman']
		self.functionButtonName = [ 'back' ]

		if self.numberOfPanels == 1:
			self.flag = 'row'
		else:
			self.flag = 'panel'
		
	#-------------------------------------------------------------------------
	def createGui(self):

                self.subSizers = [ ]
                self.mainSizer = wx.BoxSizer( wx.VERTICAL )
                
		self.numberOfCells = self.numberOfRows[ 0 ] * self.numberOfColumns[ 0 ]

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')

                for panel in self.panels.keys( ):
			
			subSizer = wx.GridBagSizer( self.xBorder, self.yBorder )
                   
			self.subSizers.append( subSizer )
			
			index = 0

			for index in range( 4 ):
				b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ index+1 ], name = self.labels[ index ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( event, self.onPress )
				subSizer.Add( b, ( index / self.numberOfColumns[ 0 ], index % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 0 ], name = self.functionButtonName[ 0 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + 1 ) / self.numberOfColumns[ 0 ], ( index + 1 ) % self.numberOfColumns[ 0 ] ), (1, 4), wx.EXPAND )
				
			for number in range( self.numberOfRows[ 0 ] ):
				subSizer.AddGrowableRow( number )
			for number in range( self.numberOfColumns[ 0 ] ):
				subSizer.AddGrowableCol( number )
		
			self.Layout( )

			self. mainSizer.Add( subSizer, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = self.xBorder )
			
			self.SetSizer( self. mainSizer )
			self.Center( True )
                        
			if panel != 1:
				self.mainSizer.Show( item = self.subSizers[ panel - 1 ], show = False, recursive = True )
                    
			self.SetSizer( self.mainSizer )
                
	#-------------------------------------------------------------------------
	def initializeTimer(self):

		self.stoper = wx.Timer( self )
		self.Bind( wx.EVT_TIMER , self.timerUpdate , self.stoper )

		if self.control != 'tracker':
			self.stoper.Start( self.timeGap )
	
	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE , self.OnCloseWindow )

	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):
		
		if self.control != 'tracker':
			if True in [ 'debian' in item for item in os.uname( ) ]: #POSITION OF THE DIALOG WINDOW DEPENDS ON WINDOWS MANAGER NOT ON DESKTOP ENVIROMENT. THERE IS NO REASONABLE WAY TO CHECK IN PYTHON WHICH WINDOWS MANAGER IS CURRENTLY RUNNING, BESIDE IT IS POSSIBLE TO FEW WINDOWS MANAGER RUNNING AT THE SAME TIME. I DON'T SEE SOLUTION OF THIS ISSUE, EXCEPT OF CREATING OWN SIGNAL (AVR MICROCONTROLLERS).
				if os.environ.get('KDE_FULL_SESSION'):
					self.mousePosition = self.winWidth/1.7, self.winHeight/1.7
				# elif ___: #for gnome-debian
				# 	self.mousePosition = self.winWidth/6.5, self.winHeight/6.
				else:
					self.mousePosition = self.winWidth/1.8, self.winHeight/1.7
			else:
				self.mousePosition = self.winWidth/1.9, self.winHeight/1.68
			
		self.mouseCursor.move( *self.mousePosition )

		dial = wx.MessageDialog(self, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal()
		
		if ret == wx.ID_YES:
			try:
				if "smplayer" in [psutil.Process(i).name() for i in psutil.get_pid_list()]:
					os.system( 'smplayer -send-action quit' )
			except TypeError:
				if "smplayer" in [psutil.Process(i).name for i in psutil.get_pid_list()]:
					os.system( 'smplayer -send-action quit' )

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

		if __name__ == '__main__':
			self.stoper.Stop( )
			self.Destroy( )
		else:
			self.stoper.Stop( )
			self.MakeModal( False )
			self.parent.Show( True )
			if self.control == 'tracker':
				self.parent.stoper.Start( 0.15 * self.parent.timeGap )
			else:
				self.parent.stoper.Start( self.parent.timeGap )
				
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
				print label
				self.stoper.Start( 0.15 * self.timeGap )

				if self.label == 'memory':
					self.stoper.Stop( )
					atmemory.memory_GUI( self, id = -1 ).Show( True )
					self.Hide( )
				elif self.label == 'memoryhard':
					self.stoper.Stop( )
					atmemory_hard.memory_GUI( self, id = -1 ).Show( True )
					self.Hide( )
				
				elif self.label == 'saper':
					self.stoper.Stop( )
					atsweeper.sweeper_GUI( self, id = -1 ).Show( True )
					self.Hide( )
				
				elif self.label == 'pacman':
					self.stoper.Stop()
					self.Hide()
					process = sp.Call( ['python', self.pathToATPlatform + '/modules/games/pacman-large/pacman.pyw'] )
					self.Show()

				elif self.label == 'back':
					self.onExit( )

		else:
			self.numberOfPresses += 1

			if self.numberOfPresses == 1:

				if self.flag == 'rest':

					if self.numberOfPanels == 1:
						self.flag = 'row'
					else:
						self.flag = 'panel'

				elif self.flag == 'panel':
					items = self.subSizers[ self.panelIteration ].GetChildren( )			

					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )

					self.flag = 'row'

				elif self.flag == 'row':

					if self.rowIteration == self.numberOfRows[ 0 ]:
						buttonsToHighlight = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ],

					else:
						buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ], ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )

					for button in buttonsToHighlight:
						item = self.subSizers[ self.panelIteration ].GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.selectionColour )
						b.SetFocus( )

					if self.rowIteration == self.numberOfRows[ 0 ]:
						self.onExit( )

					self.flag = 'columns'

				elif self.flag == 'columns':

					self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.columnIteration - 1

					item = self.subSizers[ self.panelIteration ].GetItem( self.position )
					selectedButton = item.GetWindow( )
					selectedButton.SetBackgroundColour( self.selectionColour )
					selectedButton.SetFocus( )

					self.Update( )

					if self.position == 0:
						self.stoper.Stop( )
						atmemory.memory_GUI( self, id = -1 ).Show( True )

					elif self.position == 1:
						self.stoper.Stop( )
						atmemory_hard.memory_GUI( self, id = -1 ).Show( True )
						self.Hide( )

					elif self.position == 2:
						self.stoper.Stop( )
						atsweeper.sweeper_GUI( self, id = -1 ).Show( True )
						self.Hide( )
				
					elif self.position == 3:
						self.stoper.Stop()
						self.Hide()
						process = sp.call( ['python', self.pathToATPlatform + '/modules/games/pacman-large/pacman.pyw'] )
						self.Show()
			 			self.SetFocus()
			        		self.stoper.Start( self.timeGap )

					if self.numberOfPanels == 1:
						self.flag = 'row'
						self.panelIteration = 0
					else:
						self.flag = 'panel'
						self.panelIteration = -1

					self.rowIteration = 0
					self.columnIteration = 0

					self.emptyPanelIteration = -1
					self.emptyRowIteration = 0
					self.emptyColumnIteration = 0

					selectedButton = item.GetWindow( )
					selectedButton.SetBackgroundColour( self.backgroundColour )
					selectedButton.SetFocus( )

			else:
				pass

	#-------------------------------------------------------------------------
	def timerUpdate(self , event):

		if self.control == 'tracker':

			if self.button.GetBackgroundColour( ) == self.backgroundColour:
				self.button.SetBackgroundColour( self.selectionColour )
				
			else:
				self.button.SetBackgroundColour( self.backgroundColour )	
		
			self.stoper.Stop( )
			self.pressFlag = False

		else:
			if self.control != 'tracker':
				self.mouseCursor.move( *self.mousePosition )	

                        self.numberOfPresses = 0
            
			if self.flag == 'panel': ## flag == panel ie. switching between panels
				
				if self.emptyPanelIteration == self.maxEmptyPanelIteration:
					self.flag = 'rest'
					self.emptyPanelIteration = 0
				else:
					self.panelIteration += 1
				
					self.panelIteration = self.panelIteration % self.numberOfPanels
					
					if self.panelIteration == self.numberOfPanels - 1:
						self.emptyPanelIteration += 1

					for item in range( self.numberOfPanels ):
						if item != self.panelIteration:
							self.mainSizer.Show( item = self.subSizers[ item ], show = False, recursive = True )
							
					self.mainSizer.Show( item = self.subSizers[ self.panelIteration ], show = True, recursive = True )
					self.SetSizer( self.mainSizer )
					self.Layout( )
					
			if self.flag == 'row': #flag == row ie. switching between rows
				
				if self.emptyRowIteration == self.maxEmptyRowIteration:
					self.emptyRowIteration = 0
					self.emptyPanelIteration = 0
					
					if self.numberOfPanels == 1:
						self.flag = 'rest'
					else:
						self.flag = 'panel'

					items = self.subSizers[ self.panelIteration ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )

#####################################################################################################################################

					if self.numberOfPanels > 1:
						if self.panelIteration == self.numberOfPanels:
							self.panelIteration = self.numberOfPanels - 1
						else:
							self.panelIteration -= 1

######################################################################################################################################			

				else:
					self.rowIteration = self.rowIteration % self.numberOfRows[ 0 ]
                                
					items = self.subSizers[ self.panelIteration ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
				
					if self.rowIteration == self.numberOfRows[ 0 ] - 1:
						self.emptyRowIteration += 1
				
						scope = self.rowIteration * self.numberOfColumns[ 0 ],
					else:
						scope = range( self.rowIteration * self.numberOfColumns[ 0 ], self.rowIteration * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )
					for i in scope:
						item = self.subSizers[ self.panelIteration ].GetItem( i )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
					self.rowIteration += 1
                        
			elif self.flag == 'columns': #flag = columns ie. switching between cells in the particular row

				if self.emptyColumnIteration == self.maxEmptyColumnIteration:
					self.flag = 'row'
					self.rowIteration = 0
					self.columnIteration = 0
					self.emptyColumnIteration = 0
					self.emptyRowIteration = 0
					
					items = self.subSizers[ self.panelIteration ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )

				else:
					self.columnIteration = self.columnIteration % self.numberOfColumns[ 0 ]
					
					if self.columnIteration == self.numberOfColumns[ 0 ] - 1:
						self.emptyColumnIteration += 1

					items = self.subSizers[ self.panelIteration ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )

					item = self.subSizers[ self.panelIteration ].GetItem( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.columnIteration )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.scanningColour )
					b.SetFocus( )

					self.columnIteration += 1

			if self.flag != 'rest':
				if self.switchSound.lower( ) == 'on':
					self.switchingSound.play( )

			else:
				pass


#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = games( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
