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

import wx
import wx.lib.buttons as bt
from pymouse import PyMouse

import pygame
import minesweeper

#=============================================================================
class sweeper_GUI( wx.Frame ):
	def __init__(self, parent, id):
		
		self.winWidth, self.winHeight = wx.DisplaySize( )
		
		wx.Frame.__init__( self, parent, id, 'sweeper_GUI' )
                style = self.GetWindowStyle( )
		self.SetWindowStyle( style | wx.STAY_ON_TOP )
		self.parent = parent

		self.Maximize( True )
		
		self.initializeParameters( )
		self.initializeBitmaps( )
		self.createGui( )
		self.createBindings( )
		self.initializeTimer( )

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
                
		self.colorlegend = {'0':'#E5D9D9', '1': '#5545EA', '2': '#B229B7', '3': '#13CE1A', '4':'#CE1355', '5': '#F9F504', '6':'#FF7504', '7':'#FF0404', '8':'#000000'}

		self.options = ['mode', 'restart', 'exit']
		self.selection_mode = 'mines'	
		self.winstate = False
		self.failstate = False
		self.first_move = True

		self.gamesize = ( 5, 10 ) #do ustalania
		self.numberOfRows = self.gamesize[ 0 ] + 1
                self.numberOfColumns = self.gamesize[ 1 ]

		self.numberOfMines = 4
		
		if self.numberOfColumns < 3 or self.numberOfColumns * (self.numberOfRows-1) < self.numberOfMines:
			print '\nZbyt mała liczba komórek lub kolumn. \nKomórek musi być więcej niż min, a minimalna liczba kolumn to 3. \n'
			exit( )

		self.game = minesweeper.Minesweeper_game( self.gamesize, self.numberOfMines )        	
		self.labels = self.game.displayfield.flatten( )      

                self.flag = 'row'						
                self.rowIteration = self.numberOfRows - 1					
                self.columnIteration = 0							
                self.countRows = 0
                self.countColumns = 0										

		self.maxNumberOfRows = 3
                self.maxNumberOfColumns = 2									
	    
                self.numberOfPresses = 1
                self.subSizerNumber = 0
		self.mouseCursor = PyMouse( )

		self.mouseCursor = PyMouse( )
		self.mousePosition = self.winWidth - 8, self.winHeight - 8
               	self.mouseCursor.move( *self.mousePosition )			


		self.SetBackgroundColour( 'black' )

	#-------------------------------------------------------------------------
        def initializeBitmaps(self):
		
		self.path=self.pathToATPlatform + 'icons/games/ATsweeper/'
		iconFiles = [ file for file in [ self.path + 'mine_mini.png', self.path + 'mines.png', self.path + 'flag.png', self.path + 'flag_mini.png', self.path + 'flag_crossed_mini.png', self.path + 'restart.png', self.path + 'exit.png', self.path + 'win.png', self.path + 'lose.png' ] ]
    
		iconBitmapName = [ 'mine', 'mines', 'flag', 'flag_mini', 'flag_crossed_mini', 'restart', 'exit', 'win', 'lose' ]
		
		self.iconBitmaps = { }

		for i in xrange( len( iconFiles ) ):
			self.iconBitmaps[ iconBitmapName[i] ] = wx.BitmapFromImage( wx.ImageFromStream( open( iconFiles[i], 'rb' )))      

	#-------------------------------------------------------------------------	
	def createGui(self):
		
		self.mainSizer = wx.BoxSizer( wx.VERTICAL )

		if self.winstate:
			self.res = bt.GenButton( self, -1, u'WSZYSTKIE MINY OZNAKOWANE. WYGRYWASZ!', size = ( self.winWidth, 0.1 * ( self.winHeight-20 ) ) )
		elif self.failstate:
			self.res = bt.GenButton( self, -1, u'KABOOM!', size = ( self.winWidth, 0.1 * ( self.winHeight-20 ) ) )
		else:
                	self.res = bt.GenButton( self, -1, u'FLAGI / MINY:   ' + str( self.game.numberOfFlags ) + ' / ' + str( self.game.numberOfMines ), size = ( self.winWidth, 0.1 * ( self.winHeight-20 ) ) )

		self.border = 1
		self.res.SetFont( wx.Font(27, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
				
		self.margine = 3

		self.subSizer = wx.GridBagSizer( self.margine, self.margine )

		for index_1, item in enumerate( self.labels ):

			if item == -2.0:

				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'mine' ], size = ( ( self.winWidth - self.margine/1.8 * (self.numberOfColumns) ) / float( self.numberOfColumns ), ( 0.7 * ( self.winHeight-20 ) - self.margine * (self.numberOfRows - 1) ) / float( self.numberOfRows - 1 ) ) )

			elif item == -3.0:

				b = bt.GenBitmapButton( self, -1, bitmap=self.iconBitmaps[ 'flag_mini' ],size = ( ( self.winWidth - self.margine/1.8 * (self.numberOfColumns) ) / float( self.numberOfColumns ), ( 0.7 * ( self.winHeight-20 ) - self.margine * (self.numberOfRows - 1) ) / float( self.numberOfRows - 1 ) ) )

			elif item == -4.0:

				b = bt.GenBitmapButton( self, -1, bitmap=self.iconBitmaps[ 'flag_crossed_mini' ],size = ( ( self.winWidth - self.margine/1.8 * (self.numberOfColumns) ) / float( self.numberOfColumns ), ( 0.7 * ( self.winHeight-20 ) - self.margine * (self.numberOfRows - 1) ) / float( self.numberOfRows - 1 ) ) )

			else:

				if item == -1.0:
					item = ' '			

				else:
					item = str( int( item ) )

				b = bt.GenButton( self, -1, item, name = item, size = ( ( self.winWidth - self.margine/1.8 * ( self.numberOfColumns ) ) / float( self.numberOfColumns ), ( 0.7 * ( self.winHeight-20 ) - self.margine * ( self.numberOfRows - 1 ) ) / float( self.numberOfRows - 1 ) ) )
				b.SetFont( wx.Font( 65, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			
			b.SetBezelWidth( 1 )
			b.SetBackgroundColour( self.backgroundColour )
			
			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			self.subSizer.Add( b, ( index_1 / self.numberOfColumns + 1, index_1 % self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND )
			
			if item in self.colorlegend.keys( ):
				b.SetForegroundColour( self.colorlegend[ item ] )
			else:
				b.SetForegroundColour( self.textColour )
				
		for index_2, item in enumerate( self.options ):
			
                        if index_2 == 0:
				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ self.selection_mode ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
		                b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
                                self.subSizer.Add( b, ( 0, 0 ), ( 1, self.numberOfColumns / 3 ), wx.EXPAND )

                        elif index_2 == 1:
				if not self.winstate and not self.failstate:
					b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'restart' ] )
				elif self.winstate:
					b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'win' ] )
				elif self.failstate:
					b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'lose' ] )

				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
		                b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
                                self.subSizer.Add( b, ( 0, self.numberOfColumns / 3 ), ( 1, self.numberOfColumns / 3 + self.numberOfColumns % 3 ), wx.EXPAND )

                        else:
				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'exit' ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
		                b.Bind( wx.EVT_LEFT_DOWN, self.onPress )

				if self.numberOfColumns % 3 == 2: #just numerical problem

					self.subSizer.Add( b, ( 0, 2 * self.numberOfColumns / 3 + self.numberOfColumns % 3 - 1 ), ( 1, self.numberOfColumns / 3 ), wx.EXPAND )
				else:
					self.subSizer.Add( b, ( 0, 2 * self.numberOfColumns / 3 + self.numberOfColumns % 3), ( 1, self.numberOfColumns / 3 ), wx.EXPAND )
                        
		self.mainSizer.Add( self.res, flag = wx.EXPAND | wx.TOP , border = 1 )				    
		self.mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND )

		self.SetSizer( self.mainSizer , deleteOld = True )
		
		self.Layout( )
		self.Refresh( )
		self.Center( )

	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE , self.OnCloseWindow )

	#-------------------------------------------------------------------------	
	def OnCloseWindow(self, event):

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
			event.Veto( )
			self.mousePosition = self.winWidth - 8, self.winHeight - 8
			self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------
	def onExit( self ):

		if __name__ == '__main__':
			self.stoper.Stop( )
			self.Destroy( )
		else:
			self.stoper.Stop( )
			self.MakeModal( False )
			self.parent.Show( True )
			self.parent.stoper.Start( self.parent.timeGap )
			self.Destroy( )

	#----------------------------------------------------------------------------
	def onPress(self, event):

		self.numberOfPresses += 1

		if self.numberOfPresses == 1:
			
			if self.flag == 'rest':

				self.flag = 'row'
				self.rowIteration = self.numberOfRows - 1
				self.countRows = 0

			elif self.flag == 'row':
				
				self.flag = 'columns' 
				self.rowIteration -= 1
				self.columnIteration = 0
				self.countRows = 0

			elif self.flag == 'columns':
				
				item = self.subSizer.GetItem( ( self.rowIteration ) * self.numberOfColumns + self.columnIteration - 1 )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.selectionColour )
				b.SetFocus( )
				b.Update( )
				try:
					label = self.labels[ self.rowIteration * self.numberOfColumns + self.columnIteration - 1 ]
				except IndexError:
					label = 'special'
									
				if (label == -1.0 or label == -3.0) and not self.failstate and not self.winstate: # checking for mines, updating buttons

					if self.selection_mode == 'mines':
						self.failstate = self.game.check_for_mines(self.columnIteration-1, self.rowIteration)
						while self.failstate and self.first_move:
							self.game = minesweeper.Minesweeper_game(self.gamesize, self.numberOfMines)
							self.failstate = self.game.check_for_mines(self.columnIteration-1, self.rowIteration)
						self.first_move = False
        	
						self.labels = self.game.displayfield.flatten( ) 
					else:
						self.winstate = self.game.flag_field( self.columnIteration - 1, self.rowIteration )

					self.labels = self.game.displayfield.flatten()
					self.mainSizer.Clear()
					self.createGui()
					self.flag = 'row'
					self.rowIteration = self.numberOfRows -1
					self.columnIteration = 0
					self.countColumns = 0

				elif label == 'special':
					if self.rowIteration * self.numberOfColumns + self.columnIteration - 1 == len(self.labels):
						if self.selection_mode == 'mines':						
							self.selection_mode = 'flag'
						else:
							self.selection_mode = 'mines'
						self.createGui()
						self.flag = 'row'
						self.rowIteration = self.numberOfRows -1
						self.columnIteration = 0
						self.countColumns = 0

					elif self.rowIteration * self.numberOfColumns + self.columnIteration - 1 == len(self.labels)+1: #restart
						self.selection_mode = 'mines'	
						self.winstate = False
						self.failstate = False
						self.firstmove = True
						self.game = minesweeper.Minesweeper_game(self.gamesize, self.numberOfMines)        	
						self.labels = self.game.displayfield.flatten()  
						self.createGui()
						self.flag = 'row'
						self.rowIteration = self.numberOfRows -1 
						self.columnIteration = 0
						self.countColumns = 0 

					elif self.rowIteration * self.numberOfColumns + self.columnIteration - 1 == len(self.labels)+2:
						self.onExit( )
				

				else:
					self.flag = 'row'
					self.rowIteration = self.numberOfRows -1
					self.columnIteration = 0
					self.countColumns = 0 
					event.Skip( )

		else:
			event.Skip( )	

	#-------------------------------------------------------------------------
	def initializeTimer(self):

                id1 = wx.NewId( )
                wx.RegisterId( id1 )
		self.stoper = wx.Timer( self, id1 )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper, id1 )

		self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------
	def timerUpdate(self, event):

		self.mouseCursor.move( *self.mousePosition )
		
		self.numberOfPresses = 0		

		if self.flag == 'rest':
			pass

		elif self.countRows < self.maxNumberOfRows:

			if self.flag == 'row':

				self.rowIteration = self.rowIteration % self.numberOfRows

				items = self.subSizer.GetChildren( )
				for i,item in enumerate(items):
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )

				if self.rowIteration == self.numberOfRows - 2:
					self.countRows += 1
				
				if self.rowIteration == self.numberOfRows - 1:

					buttonsToHighlight = range( self.rowIteration * self.numberOfColumns, self.rowIteration * self.numberOfColumns + 3 )

				else:
					buttonsToHighlight = range( self.rowIteration * self.numberOfColumns, self.rowIteration * self.numberOfColumns + self.numberOfColumns )

				for i, button in enumerate( buttonsToHighlight ):

						item = self.subSizer.GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
						b.Update( )

				self.rowIteration += 1

			elif self.flag == 'columns':

					if self.countColumns == self.maxNumberOfColumns:
						self.flag = 'row'

						item = self.subSizer.GetItem( self.rowIteration * self.numberOfColumns + self.columnIteration - 1 )

						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )

						self.rowIteration = self.numberOfRows-1
						self.columnIteration = 0
						self.countColumns = 0

					else:

	################################################################################################################################################

						new_numberOfColumns = self.numberOfColumns

						if self.rowIteration == self.numberOfRows - 1:
							new_numberOfColumns = 3

	################################################################################################################################################

						if self.columnIteration == new_numberOfColumns - 1 or (self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns - 3 and self.rowIteration == self.numberOfRows - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns - 4 and self.rowIteration == self.numberOfRows - 1 ):
							self.countColumns += 1

						if self.columnIteration == new_numberOfColumns or ( self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns - 2 and self.rowIteration == self.numberOfRows - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns - 3 and self.rowIteration == self.numberOfRows - 1 ):
							self.columnIteration = 0

						items = self.subSizer.GetChildren( )
						for i,item in enumerate(items):

								b = item.GetWindow( )
								b.SetBackgroundColour( self.backgroundColour )
								b.SetFocus( )
								b.Update( )

						item = self.subSizer.GetItem( self.rowIteration * self.numberOfColumns + self.columnIteration )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
						b.Update( )

						self.columnIteration += 1

		elif self.countRows == self.maxNumberOfRows:

			self.flag = 'rest'
			self.countRows += 1

			items = self.subSizer.GetChildren( )
			
			for item in items:
				b = item.GetWindow( )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetFocus( )


#=============================================================================
if __name__ == '__main__':
	app = wx.PySimpleApp( )
	frame = sweeper_GUI( parent = None, id = -1 )
	frame.Show( )
	app.MainLoop( )