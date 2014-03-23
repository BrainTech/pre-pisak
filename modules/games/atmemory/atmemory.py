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
import numpy as np
import time

import memory

#=============================================================================
class memory_GUI( wx.Frame ):
	def __init__(self, parent, id):

		self.winWidth, self.winHeight = wx.DisplaySize( )
		
		wx.Frame.__init__( self , parent , id , 'memory_GUI')
                style = self.GetWindowStyle()
		self.SetWindowStyle( style | wx.STAY_ON_TOP )
		self.parent=parent

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
		
		self.options = [ 'restart', 'exit' ]
		self.winstate = False
		self.move_info = False
		
		self.revert = False
		
		self.gamesize = ( 4, 5 ) #do ustalania
		self.indexes = np.arange( 1, self.gamesize[ 0 ] * self.gamesize[ 1 ] / 2 + 1 )
		self.game = memory.Memory_game( self.gamesize )        	
		self.labels = self.game.displayfield.flatten( )      
		
		self.numberOfRows = self.gamesize[ 0 ] + 1
                self.numberOfColumns = self.gamesize[ 1 ]
		
                self.flag = 'row'						
                self.rowIteration = 0						
                self.columnIteration = 0							
                self.countRows = 0
                self.countColumns = 0										
		
                self.maxNumberOfColumns = 2									
		
                self.numberOfPresses = 1
                self.subSizerNumber = 0

		self.mouseCursor = PyMouse( )
				
		self.SetBackgroundColour( 'black' )

	#-------------------------------------------------------------------------
        def initializeBitmaps(self):
		
		self.path = self.pathToATPlatform
		
		iconFiles = [ file for file in [ self.path + 'icons/games/atmemory/restart.png', self.path + 'icons/games/atmemory/exit.png' ,self.path + 'icons/games/atmemory/empty.png' ] ]	
		iconBitmapName = [ 'restart', 'exit', 'empty' ]

		for i in self.indexes:
			i = str( i )
			file = self.path + 'multimedia/games/atmemory/' + i + '.png'
			iconFiles.append( file )
			iconBitmapName.append( i )
	
		self.iconBitmaps = { }
		
		for i in xrange( len( iconFiles ) ):
			self.iconBitmaps[ iconBitmapName[ i ] ] = wx.BitmapFromImage( wx.ImageFromStream( open( iconFiles[ i ], 'rb' ) ) )      

	#-------------------------------------------------------------------------	
	def createGui(self):
		
		self.mainSizer = wx.BoxSizer( wx.VERTICAL )		

		self.subSizer = wx.GridBagSizer( 3, 3 )
		
		for index_1, item in enumerate( self.labels ):
			if item in self.indexes:
				name = str(int(item))
				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ name ], size = ( 0.985*self.winWidth / self.numberOfColumns, 0.95 * self.winHeight / self.numberOfRows ) )#0.79
			else:
				if item == -1.0:
					name = 'empty'			
				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ name ], size = ( 0.985*self.winWidth / self.numberOfColumns, 0.95 * self.winHeight / self.numberOfRows ) )
				b.SetFont( wx.Font( 65, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )

			
			b.SetBezelWidth( 1 )
			b.SetBackgroundColour( self.backgroundColour )

			b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
			self.subSizer.Add( b, ( index_1 / self.numberOfColumns, index_1 % self.numberOfColumns ), wx.DefaultSpan, wx.EXPAND )

		for index_2, item in enumerate( self.options ):

                        if index_2==0:
				if self.winstate:
					b = bt.GenButton( self, -1, u'WYGRYWASZ!', size = ( 0.985*self.winWidth / self.numberOfColumns, 0.95 * self.winHeight / self.numberOfRows  ) )
					b.SetFont( wx.Font(27, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		
				else:
					b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'restart' ] )
				
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
				b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
		                self.subSizer.Add( b, ( ( index_1 + index_2 +1) / self.numberOfColumns, ( index_1 + index_2+1 ) % self.numberOfColumns ), (1,3), wx.EXPAND )

                        else:
				b = bt.GenBitmapButton( self, -1, bitmap = self.iconBitmaps[ 'exit' ] )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetBezelWidth( 3 )
		                b.Bind( wx.EVT_LEFT_DOWN, self.onPress )
                                self.subSizer.Add( b, ( ( index_1 + index_2+3 ) / self.numberOfColumns, ( index_1 + index_2 +3) % self.numberOfColumns), (1,2), wx.EXPAND )
                        				    		    
		self.mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND )
		self.SetSizer( self.mainSizer , deleteOld = True )
		
		self.Layout( )
		self.Refresh( )
		self.Center( )

	#-------------------------------------------------------------------------
	def updateGui(self,row,column,name):
		item = self.subSizer.GetItem( ( row ) * self.numberOfColumns + column - 1 )
		b = item.GetWindow( )
		b.SetBitmapLabel(bitmap = self.iconBitmaps[ name ], createOthers=True)
		b.Update( )		
		self.Layout()
		self.Refresh()
		self.Center()

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
				self.parent.parent.parent.parent.Destroy()
				self.parent.parent.parent.Destroy()
				self.parent.parent.Destroy()
				self.parent.Destroy()
				self.Destroy()
				
			except AttributeError:
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

	#----------------------------------------------------------------------------
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

	#----------------------------------------------------------------------------
	def onPress(self, event):

		self.numberOfPresses += 1

		if self.numberOfPresses == 1:
			#print self.game.displayfield
			if self.flag == 'rest':
				self.flag = 'row'
				self.rowIteration = 0

			elif self.flag == 'row':
				
				self.flag = 'columns' 
				self.rowIteration -= 1
				self.columnIteration = 0
			
			elif self.flag == 'columns':

				item = self.subSizer.GetItem( ( self.rowIteration ) * self.numberOfColumns + self.columnIteration - 1 )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.selectionColour )
				b.SetFocus( )
				b.Update( )

				self.labels = self.game.displayfield.flatten( )
				try:
					label = self.labels[ self.rowIteration * self.numberOfColumns + self.columnIteration - 1 ]
					#print label
				except IndexError:
					label = 'special'
									
				if label == -1.0 and not self.winstate: # checking
					#print 'checking'
					self.move_info = self.game.check_field(self.columnIteration-1, self.rowIteration)

					#print self.game.displayfield
					self.labels = self.game.displayfield.flatten( )

					self.updateGui(self.rowIteration, self.columnIteration,str(int(self.game.displayfield[self.rowIteration, self.columnIteration-1])))

					if self.move_info == 'second-miss':
						
						self.revert = True
						self.new_rowIteration, self.new_columnIteration = self.rowIteration, self.columnIteration 

					elif self.move_info == 'first':
						self.old_rowIteration, self.old_columnIteration = self.rowIteration, self.columnIteration
					else:
						if np.all(self.game.displayfield > -0.5):
							self.winstate = True
							self.createGui()

					self.flag = 'row'
					self.rowIteration = 0
					self.columnIteration = 0
					self.countColumns = 0

				elif label == 'special':
					if self.rowIteration * self.numberOfColumns + self.columnIteration - 1 == len( self.labels ): #restart
						self.winstate = False
						self.failstate = False
						self.game = memory.Memory_game( self.gamesize )        	
						self.labels = self.game.displayfield.flatten( )  
						self.createGui( )
						self.flag = 'row'
						self.rowIteration = 0
						self.columnIteration = 0
						self.countColumns = 0 

					elif self.rowIteration * self.numberOfColumns + self.columnIteration - 1 == len( self.labels ) + 1: #exit
						self.onExit( )

				else:
					event.Skip( )
		else:
			event.Skip( )	

	#-------------------------------------------------------------------------
	def initializeTimer(self):

                id1=wx.NewId( )
                wx.RegisterId( id1 )
		self.stoper = wx.Timer( self, id1 )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper, id1 )

		self.stoper.Start( self.timeGap )
	

	#-------------------------------------------------------------------------
	def timerUpdate(self, event):
		self.numberOfPresses = 0		
		if self.revert:
			self.stoper.Stop()
			time.sleep(1)
			self.stoper.Start( self.timeGap )
			self.game.revert( )
			#print self.rowIteration, self.columnIteration, self.old_rowIteration, self.old_columnIteration			
			self.updateGui(self.new_rowIteration, self.new_columnIteration,'empty')
			self.updateGui(self.old_rowIteration, self.old_columnIteration,'empty')
			
			self.revert = False
			self.flag = 'row'
			self.rowIteration = 0
			self.columnIteration = 0
			self.countColumns = 0

			
		self.mouseCursor.move( self.winWidth - 12, self.winHeight - 500 )
		

		if self.flag == 'row':

			self.rowIteration = self.rowIteration % self.numberOfRows

			items = self.subSizer.GetChildren( )
			for i, item in enumerate( items ):
                                        b = item.GetWindow( )
                                        b.SetBackgroundColour( self.backgroundColour )
                                        b.SetFocus( )
                                        b.Update( )

			if self.rowIteration == self.numberOfRows - 1:
				self.countRows += 1
				buttonsToHighlight = range( self.rowIteration * self.numberOfColumns, self.rowIteration * self.numberOfColumns  + 2 )

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

################################################################################################################################################
					
				new_numberOfColumns = self.numberOfColumns
				if self.rowIteration == self.numberOfRows - 1:
					new_numberOfColumns = 2
					self.maxNumberOfColumns = 4

################################################################################################################################################

				if self.countColumns == self.maxNumberOfColumns:
					self.flag = 'row'

					item = self.subSizer.GetItem( self.rowIteration * self.numberOfColumns + self.columnIteration - 1 )
                                        
					b = item.GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )

					self.rowIteration = 0
					self.columnIteration = 0
					self.countColumns = 0

				else:

					if self.columnIteration == new_numberOfColumns - 1 or (self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns - 3 and self.rowIteration == self.numberOfRows - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns - 4 and self.rowIteration == self.numberOfRows - 1 ):
						self.countColumns += 1

					if self.columnIteration == new_numberOfColumns or ( self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns - 2 and self.rowIteration == self.numberOfRows - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns - 3 and self.rowIteration == self.numberOfRows - 1 ):
						self.columnIteration = 0

					items = self.subSizer.GetChildren( )

					for i, item in enumerate( items ):
                                       
                                                        b = item.GetWindow( )
                                                        b.SetBackgroundColour( self.backgroundColour )
                                                        b.SetFocus( )
                                                        b.Update( )

                                        item = self.subSizer.GetItem( self.rowIteration * self.numberOfColumns + self.columnIteration)
                                        b = item.GetWindow( )
                                        b.SetBackgroundColour( self.scanningColour )
                                        b.SetFocus( )
                                        b.Update( )

					self.maxNumberOfColumns			
					self.columnIteration += 1


#=============================================================================
if __name__ == '__main__':
	app = wx.PySimpleApp( )
	frame = memory_GUI( parent = None, id = -1 )
	frame.Show( )
	app.MainLoop( )

