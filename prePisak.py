#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Pre-Pisak is an interactive platform for people with severe expressive, communication disorders.
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

import wx, os, sys, alsaaudio, psutil
import wx.lib.buttons as bt
import subprocess as sp

from pymouse import PyMouse
from pygame import mixer

from modules import speller, audiobook, music, movie, radio 
from modules import exercise

#=============================================================================
class main_menu( wx.Frame ):
	def __init__(self, parent, id):

		self.winWidth, self.winHeight = wx.DisplaySize( )

		wx.Frame.__init__( self , parent , id, 'ATPlatform MainMenu' )
		style = self.GetWindowStyle( )
		self.SetWindowStyle( style | wx.STAY_ON_TOP )

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

		cmd = 'pwd'
		p = sp.Popen( cmd, shell = True, stdin = sp.PIPE, stdout = sp.PIPE, stderr = sp.STDOUT, close_fds = True )
		self.path = p.stdout.read( )[ :-1 ] + '/'
		
		files = [ '.pathToATPlatform', './modules/.pathToATPlatform', './modules/pilots/.pathToATPlatform', './modules/others/.pathToATPlatform', 'modules/ewriting/.pathToATPlatform', 'modules/games/atmemory/.pathToATPlatform', 'modules/games/atsweeper/.pathToATPlatform' ]

		for item in files:
			with open(item, 'w') as textFile:
				textFile.write( self.path ) 

				sys.path.append( self.path )

		from reader import reader
		
		reader = reader()
		reader.readParameters()
		parameters = reader.getParameters()

		for item in parameters:
			try:
				setattr(self, item[:item.find('=')], int(item[item.find('=')+1:]))
			except ValueError:
				setattr(self, item[:item.find('=')], item[item.find('=')+1:])

		self.labels = 'SPELLER EXERCISES AUDIOBOOKS MUSIC MOVIES RADIO'.split( )

		self.flag = 'row'
		self.pressFlag = False

		self.numberOfRows = [2]
		self.numberOfColumns = [3]
		self.maxRows = [ 3 * item for item in self.numberOfRows ]
		self.maxColumns = [ 2 * item for item in self.numberOfColumns ]

		self.rowIteration = 0
		self.colIteration = 0
		self.countRows = 0
		self.countColumns = 0

		self.numberOfPresses = 1
		self.mouseCursor = PyMouse( )
		
		if self.control != 'tracker':
			self.mouseCursor = PyMouse( )
			self.mousePosition = self.winWidth - 4 - self.xBorder, self.winHeight - 4 - self.yBorder
			self.mouseCursor.move( *self.mousePosition )
							
		if self.switchSound.lower( ) == 'on' or self.pressSound.lower( ) == 'on':
			mixer.init( )
			if self.switchSound.lower( ) == 'on':
				self.switchingSound = mixer.Sound( self.path + '/sounds/switchSound.wav' )
			if self.pressSound.lower( ) == 'on':
				self.pressingSound = mixer.Sound( self.path + '/sounds/pressSound.wav' )

		self.SetBackgroundColour( 'black' )

		alsaaudio.Mixer( control = 'Master' ).setvolume( self.musicVolumeLevel, 0 )

	#-------------------------------------------------------------------------	
        def initializeBitmaps(self):
            
	    labelFiles = [ self.path + item for item in [ 'icons/modules/speller.png', 'icons/modules/exercises.png', 'icons/modules/audiobooks.png', 'icons/modules/music.png', 'icons/modules/movies.png', 'icons/modules/radio.png', ] ]

            self.labelbitmaps = { }
	    for index in xrange( len(self.labels) ):
		    self.labelbitmaps[ self.labels[index] ] = wx.BitmapFromImage( wx.ImageFromStream( open(labelFiles[index], "rb") ) )

	#-------------------------------------------------------------------------
	def createGui(self):
		self.vbox = wx.BoxSizer( wx.VERTICAL )
                self.sizer = wx.GridSizer( self.numberOfRows[ 0 ], self.numberOfColumns[ 0 ], self.xBorder, self.yBorder )

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')
			
		for i in self.labels:
			b = bt.GenBitmapButton( self , -1, bitmap = self.labelbitmaps[ i ], name = i )
           		b.SetBackgroundColour( self.backgroundColour )
			b.Bind( event, self.onPress )
			self.sizer.Add( b, 0, wx.EXPAND )
		self.vbox.Add( self.sizer, proportion=1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=self.xBorder )
		self.SetSizer( self.vbox )

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
	def OnCloseWindow(self , event):
		
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
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP )

		ret = dial.ShowModal( )
		
		if ret == wx.ID_YES:
			try:
				if "smplayer" in [psutil.Process(i).name() for i in psutil.get_pid_list()]:
					os.system( 'smplayer -send-action quit' )
			except TypeError:
				if "smplayer" in [psutil.Process(i).name for i in psutil.get_pid_list()]:
					os.system( 'smplayer -send-action quit' )
					
			self.Destroy( )
		else:
			event.Veto( )

			if self.control != 'tracker':
					self.mousePosition = self.winWidth - 4 - self.xBorder, self.winHeight - 4 - self.yBorder
					self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------
	def onPress( self, event ):
		
		if self.pressSound.lower( ) == 'on':
			self.pressingSound.play( )

		if self.control == 'tracker':
                    if self.pressFlag == False:
			    self.button = event.GetEventObject( )
			    self.button.SetBackgroundColour( self.selectionColour )
			    self.pressFlag = True
			    self.label = event.GetEventObject( ).GetName( ).encode( 'utf-8' )
			    self.stoper.Start( 0.15 * self.timeGap )
			    
		    if self.label == 'SPELLER':
			    speller.speller( parent = self, id = -1 ).Show( True )
			    self.Hide( )

		    elif self.label == 'EXERCISES':
			    exercise.exercise( self, id = -1 ).Show( True )
			    self.Hide( )

		    elif self.label == 'AUDIOBOOKS':
			    audiobook.audiobook( parent = self, id = -1 ).Show( True )
			    self.Hide( )

		    elif self.label == 'MUSIC':
			    music.music( self, id = -1 ).Show( True )
			    self.Hide( )

		    elif self.label == 'MOVIES':
			    movie.movie( self, id = -1 ).Show( True )
			    self.Hide( )

		    elif self.label == 'RADIO':
			    radio.radio( parent = self, id = -1 ).Show( True )
			    self.Hide( )
			    
		else:	
			self.numberOfPresses += 1
			self.countRows = 0

			if self.numberOfPresses == 1:

			    if self.flag == 'rest':
				    self.flag = 'row'
				    self.rowIteration = 0
				    self.colIteration = 0 
				    self.countRows = 0

			    elif self.flag == 'row':

				    buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ], ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )
				    for button in buttonsToHighlight:
					    item = self.sizer.GetItem( button )
					    b = item.GetWindow( )
					    b.SetBackgroundColour( self.selectionColour )
					    b.SetFocus( )

				    self.flag = 'columns'
				    self.colIteration = 0

			    elif self.flag == 'columns':

				    self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration - 1

				    item = self.sizer.GetItem( self.position )
				    selectedButton = item.GetWindow( )
				    selectedButton.SetBackgroundColour( self.selectionColour )
				    selectedButton.SetFocus( )
				    self.Update( )
				    
				    label = self.labels[ self.position ]			    
				    
				    if label == 'SPELLER':
					    self.stoper.Stop( )
					    speller.speller( parent = self, id = -1 ).Show( True )
					    self.Hide( )

				    elif label == 'EXERCISES':
					    self.stoper.Stop( )
					    exercise.exercise( self, id = -1 ).Show( True )
					    self.Hide( )

				    elif label == 'AUDIOBOOKS':
					    self.stoper.Stop( )
					    audiobook.audiobook( parent = self, id = -1 ).Show( True )
					    self.Hide( )

				    elif label == 'MUSIC':
					    self.stoper.Stop( )
					    music.music( self, id = -1 ).Show( True )
					    self.Hide( )

				    elif label == 'MOVIES':
					    self.stoper.Stop( )
					    movie.movie( self, id = -1 ).Show( True )
					    self.Hide( )

				    elif label == 'RADIO':
					    self.stoper.Stop( )
					    radio.radio( parent = self, id = -1 ).Show( True )
					    self.Hide( )

				    self.flag = 'row'
				    self.rowIteration = 0
				    self.colIteration = 0
				    self.countColumns = 0
				    self.countRows = 0

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

			if self.flag == 'rest':
				pass

			elif self.countRows < self.maxRows[ 0 ]:

				if self.flag == 'row':

					self.rowIteration = self.rowIteration % self.numberOfRows[ 0 ]

					items = self.sizer.GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )

					buttonsToHighlight = range( self.rowIteration * self.numberOfColumns[ 0 ], self.rowIteration * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )
					for button in buttonsToHighlight:
						item = self.sizer.GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )

					self.rowIteration += 1
					self.countRows += 1

				elif self.flag == 'columns':
					if self.countColumns == self.maxColumns[ 0 ]:
						self.flag = 'row'
						self.rowIteration = 0
						self.colIteration = 0
						self.countColumns = 0
						self.countRows = 0
					else:

						self.colIteration = self.colIteration % self.numberOfColumns[ 0 ]					

						items = self.sizer.GetChildren( )
						for item in items:
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )

						item = self.sizer.GetItem( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )

						self.colIteration += 1
						self.countColumns += 1
				
				if self.switchSound.lower( ) == 'on':
					self.switchingSound.play( )

			elif self.countRows == self.maxRows[ 0 ]:
				self.flag = 'rest'
				self.countRows += 1

				items = self.sizer.GetChildren( )

				for item in items:
					b = item.GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetFocus( )

			else:
				pass

			# print self.rowIteration, self.colIteration


#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = main_menu( parent = None, id = -1 )
	frame.Show( True )
	app.MainLoop( )
