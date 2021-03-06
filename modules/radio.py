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

import wxversion
wxversion.select( '2.8' )

import glob, os, time
import wx, alsaaudio
import wx.lib.buttons as bt

from pymouse import PyMouse

from pilots import radioPilot


#=============================================================================
class radio( wx.Frame ):
	def __init__(self, parent, id):
	
	    self.winWidth, self.winHeight = wx.DisplaySize( )

            wx.Frame.__init__( self , parent , id, 'ATRadio' )            
            style = self.GetWindowStyle( )
            self.SetWindowStyle( style | wx.STAY_ON_TOP ) 
	    self.parent = parent
            
	    self.Maximize( True )
	    self.Centre( True )
            self.MakeModal( True )		
		
            self.initializeParameters( )

	    self.initializeBitmaps( )
            self.createGui( )								
            self.initializeTimer( )					
            self.createBindings( )						

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
					
		alsaaudio.Mixer( control = 'Master' ).setvolume( self.musicVolumeLevel, 0 )
		self.flag = 'row'

		self.numberOfRows = 4,
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

		self.mouseCursor = PyMouse( )
		self.mousePosition = self.winWidth - 8, self.winHeight - 8
               	self.mouseCursor.move( *self.mousePosition )			

		self.radioFlag = 'OFF'
		self.SetBackgroundColour( 'black' )
	    
	#-------------------------------------------------------------------------	
	def initializeBitmaps(self):

		try:
			self.path = self.pathToATPlatform + 'multimedia/radio/'
			files = os.listdir( self.path )
			files.sort( key=lambda f: os.path.getmtime( os.path.join(self.path, f) ) )

			self.existingLogos = [ ]
			for item in files:
				fileExtension = item[ item.rfind('.')+1: ]
				if fileExtension == 'png' or fileExtension == 'jpg' or fileExtension == 'jpeg':
					self.existingLogos.append( item )

			self.existingLogos = sorted( self.existingLogos, key=lambda name: int(name.split( '_', 2 )[ 0 ]) )

			self.numberOfPanels = 1 + len( self.existingLogos ) / ( ( self.numberOfRows[ 0 ]-1 )  * self.numberOfColumns[ 0 ] + 1)

			# self.newHeight = 0.4*self.winHeight / self.numberOfRows[ 0 ]

			self.panels = { }

			for number in range( self.numberOfPanels ):
				logoNames = self.existingLogos[ number * ( self.numberOfRows[ 0 ] - 1 ) * self.numberOfColumns[ 0 ] : ( number + 1 ) * ( self.numberOfRows[ 0 ] - 1 ) * self.numberOfColumns[ 0 ] ]
				logoPaths = [ self.path + name for name in logoNames ]

				logos = [ wx.ImageFromStream( open( logo, "rb" ) ) for logo in logoPaths ]
				# logos = [ logo.Rescale( logo.GetSize( )[ 0 ] * ( self.newHeight / float( logo.GetSize( )[ 1 ] ) ), self.newHeight, wx.IMAGE_QUALITY_HIGH ) for logo in logos ]
				logoBitmaps = [ wx.BitmapFromImage( logo ) for logo in logos ]

				self.panels[ number+1 ] = [ logoNames,  logoBitmaps ]

				self.radioURL = []
				with open( self.pathToATPlatform + 'documents/radio/radioURL', 'r' ) as file:
					for line in file:
						self.radioURL.append( line[:-1] )
						
		except OSError:
			self.panels = { 1 : [ [], [] ] }
			self.numberOfPanels = 1
			print "Błąd w strukturze plików."
						
		self.functionButtonPath = [ wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/volume down.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/volume up.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( self.pathToATPlatform + 'icons/show2.png', 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( '%sicons/delete.png' % self.pathToATPlatform, 'rb' ) ) ), wx.BitmapFromImage( wx.ImageFromStream( open( '%sicons/back.png' % self.pathToATPlatform, 'rb' ) ) ) ]
	
		if self.numberOfPanels == 1:
			self.flag = 'row'
		else:
			self.flag = 'panel'
	    
	#-------------------------------------------------------------------------
	def createGui(self):

                self.subSizers = [ ]
                self.mainSizer = wx.BoxSizer( wx.VERTICAL )
               
		self.numberOfCells = self.numberOfRows[ 0 ] * self.numberOfColumns[ 0 ]
                for panel in self.panels.keys( ):
			
			subSizer = wx.GridBagSizer( 4, 4 )
                   
			self.subSizers.append( subSizer )

			if self.panels != { 1 : [ [], [] ] }:
				
				index = 0
				for index, logo in enumerate( self.panels[ panel ][ 1 ] ):
					b = bt.GenBitmapButton( self, -1, name = self.panels[ panel ][ 0 ][ index ], bitmap = logo )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetBezelWidth( 3 )
					b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
					subSizer.Add( b, ( index / self.numberOfColumns[ 0 ], index % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
			else:
				index = -1

			index_2 = 0
			while index + index_2 < self.numberOfCells - 6:
				index_2 += 1
				b = bt.GenButton( self, -1 )
				b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
				b.SetBackgroundColour( self.backgroundColour )
				subSizer.Add( b, ( ( index + index_2 ) / self.numberOfColumns[ 0 ], ( index + index_2 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
			
			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 0 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 1 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 1 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 1 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 2 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 2 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 2 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 3 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 3 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 3 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 4 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 4 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

			b = bt.GenBitmapButton( self, -1, bitmap = self.functionButtonPath[ 4 ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			subSizer.Add( b, ( ( index + index_2 + 5 ) / self.numberOfColumns[ 0 ], ( index + index_2 + 5 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
				
			for number in range( self.numberOfRows[ 0 ] - 1 ):
				subSizer.AddGrowableRow( number )
			for number in range( self.numberOfColumns[ 0 ] ):
				subSizer.AddGrowableCol( number )
		
			self.Layout( )

			self. mainSizer.Add( subSizer, proportion = 1, flag = wx.EXPAND )
			
			self.SetSizer( self. mainSizer )
			self.Center( True )
                        
			if panel != 1:
				self.mainSizer.Show( item = self.subSizers[ panel - 1 ], show = False, recursive = True )
                    
			self.SetSizer( self.mainSizer )
                
	#-------------------------------------------------------------------------
	def initializeTimer(self):
		self.stoper = wx.Timer( self )
		self.Bind( wx.EVT_TIMER , self.timerUpdate , self.stoper )
		self.stoper.Start( self.timeGap )
	
	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE , self.OnCloseWindow )

	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):

		self.mousePosition = self.winWidth/1.85, self.winHeight/1.85	
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
			self.mousePosition = self.winWidth - 8, self.winHeight - 8
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
			self.parent.stoper.Start( self.parent.timeGap )
			self.Destroy( )
		
	#-------------------------------------------------------------------------
        def onPress(self, event):

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
						radioPilot.pilot( self, id = 2 ).Show( True )
						self.Hide( )

					elif self.columnIteration == 4:
						os.system( 'smplayer -send-action quit &')
						
					elif self.columnIteration == 5:
						self.onExit( )
				else:
					try:
						# print self.panelIteration
						# print self.position

						logo = self.panels[ self.panelIteration + 1 ][ 0 ][ self.position ]

						os.system('milena_say %s' % logo[ logo.find('_') + 1 : logo.rfind('.') ] )
						
						mediaIndex = self.existingLogos.index( logo )
						choice = self.radioURL[ mediaIndex ]
						# print choice

						os.system( 'smplayer -pos 0 0 %s &' % choice )
						
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

			else:
				pass
					
			# print self.panelIteration, self.rowIteration, self.columnIteration


#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = radio( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
