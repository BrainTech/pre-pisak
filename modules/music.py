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

import glob, os, sys, time #modules of the Python standard library 
import wx, alsaaudio
import wx.lib.buttons as bt

from pymouse import PyMouse
from pygame import mixer

from pilots import musicPilot


#=============================================================================
class music( wx.Frame ):
	def __init__(self, parent, id):
	
	    self.winWidth, self.winHeight = wx.DisplaySize( )

            wx.Frame.__init__( self , parent , id, 'music' )
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
		
		alsaaudio.Mixer( control = 'Master' ).setvolume( self.musicVolumeLevel, 0 )

		self.pressFlag = False

		self.numberOfRows = 3,
		self.numberOfColumns = 5,
		
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
		
		try:
			self.path = self.pathToATPlatform + 'multimedia/music/'
			directories = [ directory for directory in os.listdir( self.path ) if os.path.isdir( os.path.join( self.path, directory )) ]
			    #directories.sort( key=lambda directory: os.path.getmtime( os.path.join(self.path, directory) ) )

			directories = sorted( directories, key = lambda x: int( x.split( "_" )[ 0 ] ) )

			self.existingLogos, self.existingMedia = [ ], [ ]

			for item in directories:
				if 'playlist.m3u' in os.listdir( self.path + item ):

					self.existingMedia.append( self.path + item + '/playlist.m3u' )
					self.existingLogos.append( self.path + item + '/cover.jpg' )

				else:
					ositem = item.replace( ' ', '\ ' ).replace( '(', '\(').replace( ')', '\)' ).replace( '&', '\&')
					os.system( 'ls -d -1 %s/*.mp3 > %s/playlist.m3u' % ( self.path.replace( ' ', '\ ' ) + ositem , self.path.replace( ' ', '\ ' ) + ositem ) )

					self.existingMedia.append( self.path + item + '/playlist.m3u' )
					self.existingLogos.append( self.path + item + '/cover.jpg' )

			self.numberOfPanels = 1 + len( self.existingMedia ) / ( ( self.numberOfRows[ 0 ]-1 ) * self.numberOfColumns[ 0 ] + 1 )

			self.newHeight = 0.9 * self.winHeight / self.numberOfRows[ 0 ]

			self.panels = { }

			for number in range( self.numberOfPanels ):
				logoNames = self.existingLogos[ number * ( self.numberOfRows[ 0 ] - 1 ) * self.numberOfColumns[ 0 ] : ( number + 1 ) * ( self.numberOfRows[ 0 ] - 1 ) * self.numberOfColumns[ 0 ] ]

				logos = [ wx.ImageFromStream( open( logo, "rb" ) ) for logo in logoNames ]
				logos = [ logo.Rescale( logo.GetSize( )[ 0 ] * ( self.newHeight / float( logo.GetSize( )[ 1 ] ) ), self.newHeight, wx.IMAGE_QUALITY_HIGH ) for logo in logos ]
				logoBitmaps = [ wx.BitmapFromImage( logo ) for logo in logos ]

				self.panels[ number+1 ] = [ logoNames,  logoBitmaps ]
				
		except OSError:
			self.panels = { 1 : [ [], [] ] }
			self.numberOfPanels = 1
			print "Błąd w strukturze plików."

		self.functionButtonPath = [ wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/volume down.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/volume up.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/show.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/delete.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/back.png', 'rb' ) ) ) ]

		self.functionButtonName = [ 'volume_down', 'volume_up', 'show', 'delete', 'back' ]

		if self.numberOfPanels == 1:
			self.flag = 'row'
		else:
			self.flag = 'panel'

		# print self.existingMedia
		# print self.existingLogos
		
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

			if self.panels != { 1 : [ [], [] ] }:
			
				index = 0
				for index, logo in enumerate( self.panels[ panel ][ 1 ] ):
					b = bt.GenBitmapButton( self, -1, name = self.panels[ panel ][ 0 ][ index ], bitmap = logo )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetBezelWidth( 3 )
					b.Bind( event, self.onPress )
					subSizer.Add( b, ( index / self.numberOfColumns[ 0 ], index % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
			else:
				index = -1

			index_2 = 0
			while index + index_2 < self.numberOfCells - (self.numberOfColumns[0]+1):
				index_2 += 1
				b = bt.GenButton( self, -1, name = 'empty' )
				b.Bind( event, self.onPress )
				b.SetBackgroundColour( self.backgroundColour )
				subSizer.Add( b, ( ( index + index_2 ) / self.numberOfColumns[ 0 ], ( index + index_2 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
			
			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 0 ], name = self.functionButtonName[ 0 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 1 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 1 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 1 ], name = self.functionButtonName[ 1 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 2 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 2 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 2 ], name = self.functionButtonName[ 2 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 3 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 3 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 3 ], name = self.functionButtonName[ 3 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 4 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 4 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 4 ], name = self.functionButtonName[ 4 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 5 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 5 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
				
			for number in range( self.numberOfRows[ 0 ] ):
				subSizer.AddGrowableRow( number )
			for number in range( self.numberOfColumns[ 0 ] ):
				subSizer.AddGrowableCol( number )

			self.Layout( )

			self. mainSizer.Add( subSizer, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = self.xBorder)
			
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
			if os.environ.get('KDE_FULL_SESSION'):
				self.mousePosition = self.winWidth/1.7, self.winHeight/1.7
			elif True in [ 'debian' in item for item in os.uname( ) ]:				
				self.mousePosition = self.winWidth/6.5, self.winHeight/6.
			else:
				self.mousePosition = self.winWidth/1.9, self.winHeight/1.68
			
		self.mouseCursor.move( *self.mousePosition )

		dial = wx.MessageDialog(None, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal()
		
		if ret == wx.ID_YES:
			os.system( 'smplayer -send-action quit' )

			if __name__ == '__main__':
				self.Destroy()
			else:
				self.parent.Destroy( )
				self.Destroy( )
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
			if self.control != 'tracker':			
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
				
				if self.label == 'volume_down':
					try:
						recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
						alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume - 15, 0 )

					except alsaaudio.ALSAAudioError:
						self.button.SetBackgroundColour( 'red' )
						self.button.SetFocus( )

						self.Update( )

				elif self.label == 'volume_up':
					try:
						recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
						alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume + 15, 0 )

					except alsaaudio.ALSAAudioError:
						self.button.SetBackgroundColour( 'red' )
						self.button.SetFocus( )

						self.Update( )

				elif self.label == 'show':
					self.stoper.Stop( )
					musicPilot.pilot( self, id = 2 ).Show( True )
					self.Hide( )

				elif self.label == 'delete':
					os.system( 'smplayer -send-action quit &' )

				elif self.label == 'back':
					self.onExit( )

				elif self.label == 'empty':
					self.button.SetBackgroundColour( 'red' )
					self.button.SetFocus( )

					self.Update( )
					# time.sleep( 1.5 )

				else:
					try:
						choicePath = self.label[:self.label.rfind('/')] + '/playlist.m3u'
						# print choicePath
						os.system( 'smplayer -pos 0 0 %s &' % choicePath.replace( ' ', '\ ' ) )

					except IndexError:
						self.button.SetBackgroundColour( 'red' )
						self.button.SetFocus( )

						self.Update( )
						time.sleep( 1.5 )

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

					buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ], ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )

					for button in buttonsToHighlight:
						item = self.subSizers[ self.panelIteration ].GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.selectionColour )
						b.SetFocus( )

					self.flag = 'columns'

				elif self.flag == 'columns':

					self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.columnIteration - 1

					item = self.subSizers[ self.panelIteration ].GetItem( self.position )
					selectedButton = item.GetWindow( )
					selectedButton.SetBackgroundColour( self.selectionColour )
					selectedButton.SetFocus( )

					self.Update( )

					if self.rowIteration == self.numberOfRows[ 0 ]:

						if self.columnIteration == 1:
							try:
								recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
								alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume - 15, 0 )
								time.sleep( 1.5 )

							except alsaaudio.ALSAAudioError:
								selectedButton.SetBackgroundColour( 'red' )
								selectedButton.SetFocus( )

								self.Update( )
								time.sleep( 1.5 )

						elif self.columnIteration == 2:
							try:
								recentVolume = alsaaudio.Mixer( control = 'Master' ).getvolume( )[ 0 ] 
								alsaaudio.Mixer( control = 'Master' ).setvolume( recentVolume + 15, 0 )
								time.sleep( 1.5 )

							except alsaaudio.ALSAAudioError:
								selectedButton.SetBackgroundColour( 'red' )
								selectedButton.SetFocus( )

								self.Update( )
								time.sleep( 1.5 )

						elif self.columnIteration == 3:
							self.stoper.Stop( )
							musicPilot.pilot( self, id = 2 ).Show( True )
							self.Hide( )

						elif self.columnIteration == 4:
							os.system( 'smplayer -send-action quit &')

						elif self.columnIteration == 5:
							self.onExit( )
					else:
						try:

							logo = self.panels[ self.panelIteration + 1 ][ 0 ][ self.position ]

							videoIndex = self.existingLogos.index( logo )
							choice = self.existingMedia[ videoIndex ]
							os.system( 'smplayer -pos 0 0 %s &' % choice.replace( ' ', r'\ ' ).replace( '&', r'\&' ).replace( '#', r'\#' ).replace( '(', r'\(' ).replace( ')', r'\)' ) )

						except IndexError:                                
							selectedButton.SetBackgroundColour( 'red' )
							selectedButton.SetFocus( )

							self.Update( )
							time.sleep( 1.5 )

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

			# print self.numberOfPresses

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
					
					if self.columnIteration == self.numberOfColumns[ 0 ]-1:
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

		# print self.panelIteration, self.rowIteration, self.columnIteration


#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = music( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
