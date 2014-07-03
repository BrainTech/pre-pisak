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

import wx, glob, os, alsaaudio, time, sys
import wx.lib.buttons as bt
import subprocess as sp

from pymouse import PyMouse
from pygame import mixer

import suspend

#=============================================================================
class pilot(wx.Frame):
	def __init__(self, parent, id):

	    self.winWidth, self.winHeight = wx.DisplaySize( )
	    
            self.initializeParameters( )				
            wx.Frame.__init__( self , parent , id, 'musicPilot', size = ( self.width, self.height ), pos = ( self.winWidth - self.width - self.xBorder*(self.numberOfColumns[0]-2), self.winHeight - self.height - self.xBorder*(self.numberOfRows[0]-6) ) )
            self.SetBackgroundColour( 'black' )
	    
            style = self.GetWindowStyle( )
            self.SetWindowStyle( style | wx.STAY_ON_TOP )
	    self.parent = parent
            
	    self.MakeModal( True )		
	    
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
                        
            self.flag = 'row'
	    self.pressFlag = False
            self.pressedStopFlag = False
	    
            self.rowIteration = 0						
            self.colIteration = 0

            self.numberOfColumns = 2,
            self.numberOfRows = 7,

	    self.numberOfEmptyIteration = 0
            self.countRows = 0
            self.countColumns = 0
            self.countMaxRows = 2									
            self.countMaxColumns = 2									
	    self.countMaxEmptyIteration = 3
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
            	    
	    self.width = self.numberOfColumns[0] * 120
	    self.height = self.numberOfRows[0] * 100

	#-------------------------------------------------------------------------	
        def initializeBitmaps(self):

            buttonPaths = glob.glob( self.pathToATPlatform + 'icons/pilots/musicPilot/*' ) #labelFiles
            
            self.buttons = { }

            for buttonPath in buttonPaths:

                buttonBitmap = wx.BitmapFromImage( wx.ImageFromStream( open(buttonPath, "rb") ) )

                buttonLabel = buttonPath[ buttonPath.rfind( '/' )+1 : buttonPath.rfind('.') ]
                try:
                    buttonPosition = int( buttonLabel.split( '_' )[ 0 ] )
                    buttonName = buttonLabel[ buttonLabel.find( '_' )+1: ]
                    self.buttons[ buttonPosition ] = [ buttonName, buttonBitmap ]
                    
                except ValueError:
                    print 'Symbol %s ma nieprawidłową nazwę.' % ( buttonLabel )
                    pass

	#-------------------------------------------------------------------------
	def createGui(self):

		self.mainSizer = wx.BoxSizer( wx.VERTICAL )

		self.subSizer = wx.GridBagSizer( self.xBorder, self.yBorder )

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')
		
		for key, value in self.buttons.items( ):
			if key == 1 or key == 2 or key == 3 or key == 4:
				b = bt.GenBitmapButton( self, -1, name = value[ 0 ], bitmap = value[ 1 ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( event, self.onPress )
				
				self.subSizer.Add( b, ( ( key - 1 ) / self.numberOfColumns[ 0 ], ( key - 1 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			elif key == 5:
				b = bt.GenBitmapButton( self, -1, name = value[ 0 ], bitmap = value[ 1 ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( event, self.onPress )

				self.subSizer.Add( b, ( ( key - 1 ) / self.numberOfColumns[ 0 ], ( key - 1 ) % self.numberOfColumns[ 0 ] ), ( 1, 2 ), wx.EXPAND )
			
			else:
				b = bt.GenBitmapButton( self, -1, name = value[ 0 ], bitmap = value[ 1 ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( event, self.onPress )
				
				self.subSizer.Add( b, ( ( key ) / self.numberOfColumns[ 0 ], ( key ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
			
                for number in range( self.numberOfRows[ 0 ] ):
                    self.subSizer.AddGrowableRow( number )
                for number in range( self.numberOfColumns[ 0 ] ):
                    self.subSizer.AddGrowableCol( number )
		
		self. mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND | wx.RIGHT | wx. LEFT | wx.TOP | wx.BOTTOM, border = self.xBorder )
		self.SetSizer( self. mainSizer )
                    
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
			if os.environ.get('KDE_FULL_SESSION'):
				self.mousePosition = self.winWidth/1.05, self.winHeight/1.6
			elif True in [ 'debian' in item for item in os.uname( ) ]:				
				self.mousePosition = self.winWidth/6.5, self.winHeight/6.
			else:
				self.mousePosition = self.winWidth/1.12, self.winHeight/1.6
			
		self.mouseCursor.move( *self.mousePosition )

		dial = wx.MessageDialog(self, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal()
		
		if ret == wx.ID_YES:
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
				self.stoper.Start( 0.15 * self.timeGap )

				if self.label == 'volume down':
					try:
						recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
						alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume - 15, 0 )
						time.sleep( 1.5 )

					except alsaaudio.ALSAAudioError:
						self.button.SetBackgroundColour( 'red' )
						self.button.SetFocus( )

						self.Update( )
						time.sleep( 1.5 )

				elif self.label == 'volume up':
					try:
						recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
						alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume + 15, 0 )
						time.sleep( 1.5 )

					except alsaaudio.ALSAAudioError:
						self.button.SetBackgroundColour( 'red' )
						self.button.SetFocus( )
							
						self.Update( )
						time.sleep( 1.5 )

				elif self.label == 'play pause':
					if self.pressedStopFlag == True:
						os.system( 'smplayer -send-action play' ) 
						self.pressedStopFlag = False
						
					else:
						os.system( 'smplayer -send-action pause' )
						
				elif self.label == 'stop':
					os.system( 'smplayer -send-action stop && smplayer -send-action stop %% smplayer -send-action fullcreen' )
					self.pressedStopFlag = True
					
				elif self.label == 'fast backward':
					os.system( 'smplayer -send-action pl_prev' )
					
				elif self.label == 'fast forward':
					os.system( 'smplayer -send-action pl_next' )
					
				elif self.label == 'backward':
					os.system( 'smplayer -send-action rewind1' )
					
				elif self.label == 'forward':
					os.system( 'smplayer -send-action forward1' )
					
				elif self.label == 'repeat':
					os.system( 'smplayer -send-action repeat' )
					
				elif self.label == 'playlist repeat':
					os.system( 'smplayer -send-action pl_repeat' )
					
				elif self.label == 'cancel':
					os.system( 'smplayer -send-action quit' )
					self.onExit( )
					
				elif self.label == 'back':
					self.onExit( )
				
				elif self.label == 'playlist':
					os.system( 'smplayer -send-action show_playlist' )

		else:
			self.numberOfPresses += 1
			self.numberOfEmptyIteration = 0

			if self.numberOfPresses == 1:

				if self.flag == 'row':

					if self.rowIteration == 1 or self.rowIteration == 2:
						buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ], ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )
						for button in buttonsToHighlight:
							item = self.subSizer.GetItem( button )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.selectionColour )
							b.SetFocus( )
						self.flag = 'columns'
						self.colIteration = 0                                

					elif self.rowIteration == 3:
						buttonsToHighlight = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ],
						for button in buttonsToHighlight:
							item = self.subSizer.GetItem( button )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.selectionColour )
							b.SetFocus( )

						self.rowIteration = 0
						os.system( 'smplayer -send-action show_playlist' )

					else:
						buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] - 1, ( self.rowIteration - 1) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] - 1 )
						for button in buttonsToHighlight:
							item = self.subSizer.GetItem( button )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.selectionColour )
							b.SetFocus( )
						self.flag = 'columns'
						self.colIteration = 0                                

				elif self.flag == 'columns':

					if self.rowIteration == 1 or self.rowIteration == 2:
						self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration

					else:
						self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration - 1

					item = self.subSizer.GetItem( self.position - 1 )
					selectedButton = item.GetWindow( )
					selectedButton.SetBackgroundColour( self.selectionColour )
					selectedButton.SetFocus( )

					self.Update( )

					if self.buttons[ self.position ][ 0 ] == 'volume down':
						try:
							recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
							alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume - 15, 0 )
							time.sleep( 1.5 )

						except alsaaudio.ALSAAudioError:
							selectedButton.SetBackgroundColour( 'red' )
							selectedButton.SetFocus( )

							self.Update( )
							time.sleep( 1.5 )

					elif self.buttons[ self.position ][ 0 ] == 'volume up':
						try:
							recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
							alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume + 15, 0 )
							time.sleep( 1.5 )

						except alsaaudio.ALSAAudioError:
							selectedButton.SetBackgroundColour( 'red' )
							selectedButton.SetFocus( )

							self.Update( )
							time.sleep( 1.5 )

					elif self.buttons[ self.position ][ 0 ] == 'play pause':
						if self.pressedStopFlag == True:
							os.system( 'smplayer -send-action play' ) 
							self.pressedStopFlag = False

						else:
							os.system( 'smplayer -send-action pause' )

					elif self.buttons[ self.position ][ 0 ] == 'stop':
						os.system( 'smplayer -send-action stop && smplayer -send-action stop %% smplayer -send-action fullcreen' )
						self.pressedStopFlag = True

					elif self.buttons[ self.position ][ 0 ] == 'fast backward':
						os.system( 'smplayer -send-action pl_prev' )

					elif self.buttons[ self.position ][ 0 ] == 'fast forward':
						os.system( 'smplayer -send-action pl_next' )

					elif self.buttons[ self.position ][ 0 ] == 'backward':
						os.system( 'smplayer -send-action rewind1' )

					elif self.buttons[ self.position ][ 0 ] == 'forward':
						os.system( 'smplayer -send-action forward1' )

					elif self.buttons[ self.position ][ 0 ] == 'repeat':
						os.system( 'smplayer -send-action repeat' )

					elif self.buttons[ self.position ][ 0 ] == 'playlist repeat':
						os.system( 'smplayer -send-action pl_repeat' )

					elif self.buttons[ self.position ][ 0 ] == 'cancel':
						os.system( 'smplayer -send-action quit' )
						self.onExit( )

					elif self.buttons[ self.position ][ 0 ] == 'back':
						self.onExit( )

					selectedButton.SetBackgroundColour( self.backgroundColour ) # depend on abilites comment or not
					self.flag = 'row'
					self.rowIteration = 0
					self.colIteration = 0
					self.countRows = 0
					self.countColumns = 0

			else:
				pass

			# print self.numberOfPresses

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
			if self.control != 'tracker':
				self.mouseCursor.move( *self.mousePosition )	

			self.numberOfPresses = 0

			if self.numberOfEmptyIteration < 3*0.9999999999:

				if self.switchSound.lower( ) == 'on':
					self.switchingSound.play( )

				if self.flag == 'row': #flag == row ie. switching between rows

						self.numberOfEmptyIteration += 1. / self.numberOfRows[ 0 ]

						self.rowIteration = self.rowIteration % self.numberOfRows[ 0 ]

						items = self.subSizer.GetChildren( )
						for item in items:
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )

						if self.rowIteration == 0 or self.rowIteration == 1:
							scope = range( self.rowIteration * self.numberOfColumns[ 0 ], self.rowIteration * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )

						elif self.rowIteration == 2:
							scope = self.rowIteration * self.numberOfColumns[ 0 ], 

						else:
							scope = range( self.rowIteration * self.numberOfColumns[ 0 ] - 1, self.rowIteration * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] - 1 )
						for i in scope:
							item = self.subSizer.GetItem( i )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.scanningColour )
							b.SetFocus( )

						self.rowIteration += 1

				elif self.flag == 'columns': #flag = columns ie. switching between cells in the particular row

					if self.countColumns == self.countMaxColumns:
						self.flag = 'row'
						self.rowIteration = 0
						self.colIteration = 0
						self.countColumns = 0
						self.countRows = 0

						items = self.subSizer.GetChildren( )
						for item in items:
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )

					else:
						self.colIteration = self.colIteration % self.numberOfColumns[ 0 ]

						if self.colIteration == self.numberOfColumns[ 0 ] - 1:
							self.countColumns += 1

						items = self.subSizer.GetChildren( )
						for item in items:
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )

						if self.rowIteration == 1 or self.rowIteration == 2:
							item = self.subSizer.GetItem( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration )

						else:
							item = self.subSizer.GetItem( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration - 1 )				
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )

						self.colIteration += 1

			else:
			    self.stoper.Stop( )
			    suspend.suspend( self, id = 2 ).Show( True )
			    self.Hide( )

			    items = self.subSizer.GetChildren( )			
			    for item in items:
				    b = item.GetWindow( )
				    b.SetBackgroundColour( self.backgroundColour )
				    b.SetFocus( )

			    self.numberOfEmptyIteration = 0
			    self.countColumns = 0
			    self.countRows = 0
			    self.colIteration = 0
			    self.rowIteration = 0
			    self.countColumns = 0
			    self.countRows = 0
			    self.numberOfPresses = 1

			# print self.rowIteration, self.colIteration

#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = pilot( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
