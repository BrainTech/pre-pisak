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

import wx, glob, os
import wx.lib.buttons as bt

from pymouse import PyMouse


#=============================================================================
class pilot( wx.Frame ):
	def __init__(self, parent, id):

	    self.winWidth, self.winHeight = wx.DisplaySize( )
	    
            wx.Frame.__init__( self , parent , id, 'bookPilot', size = ( 220, 267 ), pos = ( self.winWidth - 224, self.winHeight - 267 ) )
	    
            style = self.GetWindowStyle( )
            self.SetWindowStyle( style | wx.STAY_ON_TOP )
	    self.parent = parent
            
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
                        
            self.flag = 'row'
	    
            self.rowIteration = 0						
            self.colIteration = 0

            self.numberOfColumns = 2,
            self.numberOfRows = 4,

	    self.numberOfEmptyIteration = 0
            self.countRows = 0
            self.countColumns = 0
            self.countMaxRows = 2									
            self.countMaxColumns = 2									
            self.numberOfPresses = 1

            self.mouseCursor = PyMouse( )
	    self.mousePosition = self.winWidth - 8, self.winHeight - 8
            self.mouseCursor.move( *self.mousePosition )	

            self.SetBackgroundColour( 'black' )
	    
	#-------------------------------------------------------------------------	
        def initializeBitmaps(self):

            radioLogoPaths = glob.glob( self.pathToATPlatform + 'icons/pilots/bookPilot/*' ) #labelFiles
            
            self.radios = { }

            for radioLogoPath in radioLogoPaths:

                radioLogoBitmap = wx.BitmapFromImage( wx.ImageFromStream( open(radioLogoPath, "rb") ) )

                radioLabel = radioLogoPath[ radioLogoPath.rfind( '/' )+1 : radioLogoPath.rfind( '.' ) ]
                try:
                    radioPosition = int( radioLabel.split( '_' )[ 0 ] )
                    radioName = radioLabel[ radioLabel.find( '_' )+1: ]
                    self.radios[ radioPosition ] = [ radioName, radioLogoBitmap ]
                    
                except ValueError:
                    print 'Symbol %s ma nieprawidłową nazwę.' % ( radioLabel )
                    pass

	#-------------------------------------------------------------------------
	def createGui(self):

		self.mainSizer = wx.BoxSizer( wx.VERTICAL )

		self.subSizer = wx.GridBagSizer( 4, 4 )
		
		for key, value in self.radios.items( ):
			if key == 1 or key == 2 or key == 3 or key == 4 or key == 5 or key == 6:
				b = bt.GenBitmapButton( self, -1, name = value[ 0 ], bitmap = value[ 1 ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
				
				self.subSizer.Add( b, ( ( key - 1 ) / self.numberOfColumns[ 0 ], ( key - 1 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )			
			elif key == 7:
				b = bt.GenBitmapButton( self, -1, name = value[ 0 ], bitmap = value[ 1 ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( wx.EVT_LEFT_DOWN, self.onPress )

				self.subSizer.Add( b, ( ( key - 1 ) / self.numberOfColumns[ 0 ], ( key - 1 ) % self.numberOfColumns[ 0 ] ), ( 1, 2 ), wx.EXPAND )

                for number in range( self.numberOfRows[ 0 ] ):
                    self.subSizer.AddGrowableRow( number )
                for number in range( self.numberOfColumns[ 0 ] ):
                    self.subSizer.AddGrowableCol( number )
		
		self. mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND )
		self.SetSizer( self. mainSizer )
                    
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
			os.system( 'wmctrl -c Przeglądarka\ książek' )
			os.system( 'wmctrl -c E-book\ Viewer' )

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
		self.numberOfEmptyIteration = 0
		
                if self.numberOfPresses == 1:
			
			if self.flag == 'row':

				if self.rowIteration == self.numberOfRows[ 0 ]:
					buttonsToHighlight = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ],

				else:
					buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ], ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )
			
				for button in buttonsToHighlight:
					item = self.subSizer.GetItem( button )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.selectionColour )
					b.SetFocus( )
					
				if self.rowIteration == self.numberOfRows[ 0 ]:
					os.system( 'wmctrl -c Przeglądarka\ książek' )
					os.system( 'wmctrl -c E-book\ Viewer' )
					if __name__ == '__main__':
						self.stoper.Stop( )
						self.Destroy( )
					else:
						self.stoper.Stop( )
						self.parent.stoper.Stop( )
						self.MakeModal( False )
						self.parent.MakeModal( False )
						self.parent.parent.Show( True )
						self.parent.parent.stoper.Start( self.parent.parent.timeGap )
						self.parent.Destroy( )
						self.Destroy( )
						
				self.flag = 'columns'
				self.colIteration = 0                                
				
			elif self.flag == 'columns':
                            
				self.position = ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration
	
				item = self.subSizer.GetItem( self.position - 1 )
				selectedButton = item.GetWindow( )
				selectedButton.SetBackgroundColour( self.selectionColour )
				selectedButton.SetFocus( )
                                
                                self.Update( )

				if self.radios[ self.position ][ 0 ] == 'previous page':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Page_Up' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Page_Up' )

				elif self.radios[ self.position ][ 0 ] == 'next page':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Page_Down' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Page_Down' )

				elif self.radios[ self.position ][ 0 ] == 'previous section':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Page_Up' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Page_Up' )
					
				elif self.radios[ self.position ][ 0 ] == 'next section':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Page_Down' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Page_Down' )
                                
				elif self.radios[ self.position ][ 0 ] == 'begin document':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Home' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+Home' )

				elif self.radios[ self.position ][ 0 ] == 'end document':
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+End' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Ctrl+End' )
					
                                selectedButton.SetBackgroundColour( self.backgroundColour )
				self.flag = 'row'
                                self.panelIteration = 0
				self.rowIteration = 0
				self.colIteration = 0
				self.countColumns = 0
				self.countRows = 0
				
		else: 
			pass

		# print self.numberOfPresses


	#-------------------------------------------------------------------------
	def timerUpdate(self, event):
				
               	self.mouseCursor.move( *self.mousePosition )
		
                self.numberOfPresses = 0
		
		if self.numberOfEmptyIteration < 2:
			if self.flag == 'row': #flag == row ie. switching between rows
				
					self.numberOfEmptyIteration += 1. / self.numberOfRows[ 0 ]        

					self.rowIteration = self.rowIteration % self.numberOfRows[ 0 ]

					items = self.subSizer.GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )

					if self.rowIteration == self.numberOfRows[ 0 ] - 1:
						scope = self.rowIteration * self.numberOfColumns[ 0 ],
					else:
						scope = range( self.rowIteration * self.numberOfColumns[ 0 ], self.rowIteration * self.numberOfColumns[ 0 ] + self.numberOfColumns[ 0 ] )

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
					self.numberOfPresses = 1

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

					item = self.subSizer.GetItem( ( self.rowIteration - 1 ) * self.numberOfColumns[ 0 ] + self.colIteration )
						
					b = item.GetWindow( )
					b.SetBackgroundColour( self.scanningColour )
					b.SetFocus( )
					
					self.colIteration += 1

		else:
                        self.onExit( )

		# print self.rowIteration, self.colIteration

#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = pilot( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
