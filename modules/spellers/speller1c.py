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
from string import maketrans
from pygame import mixer


#=============================================================================
class speller( wx.Frame ):
	def __init__(self, parent, id):

		self.winWidth, self.winHeight = wx.DisplaySize( )

		wx.Frame.__init__( self , parent , id , 'ATPlatform Speller' )
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
				    print 'Błąd w pliku parameters w linii', line
				    
				    self.timeGap = 1500
				    self.backgroundColour = 'white'
				    self.textColour = 'black'
				    self.scanningColour =  '#E7FAFD'
				    self.selectionColour = '#9EE4EF'
				    self.filmVolumeLevel = 100
				    self.musicVolumeLevel = 40
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
				    
				    self.voice = 'False'
				    self.vowelColour = 'False'
				    self.polishLettersColour = 'False'

	    self.labels = [ 'A E B C D F G H I O J K L M N P U Y R S T W Z SPECIAL_CHARACTERS UNDO SPEAK SAVE SPACJA OPEN EXIT'.split( ), '1 2 3 4 5 6 7 8 9 0 + - * / = % $ & . , ; : " ? ! @ # ( ) [ ] { } < > ~ UNDO SPEAK SAVE SPACJA OPEN EXIT'.split( ) ]
	    
	    self.colouredLabels = [ 'A', 'E', 'I', 'O', 'U', 'Y' ]

	    self.numberOfRows = [ 4, 5 ]
	    self.numberOfColumns = [ 8, 9 ]
				
	    self.flag = 'row'						
	    self.pressFlag = False

	    self.rowIteration = 0						
	    self.columnIteration = 0							
	    self.countRows = 0
	    self.countColumns = 0										

	    self.maxNumberOfRows = 2
	    self.maxNumberOfColumns = 2									
	    
	    self.numberOfPresses = 1
	    self.subSizerNumber = 0

	    if self.control != 'tracker':		    
		    self.mouseCursor = PyMouse( )
		    self.mousePosition = self.winWidth - 8, self.winHeight - 8
		    self.mouseCursor.move( *self.mousePosition )			

	    mixer.init( )
	    self.typewriterKeySound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_key.wav' )
	    self.typewriterForwardSound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_forward.wav' )
	    self.typewriterSpaceSound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_space.wav' )

	    if self.voice == 'True':
		    self.phones = glob.glob( self.pathToATPlatform + 'sounds/phone/*' )
		    self.phoneLabels = [ item[ item.rfind( '/' )+1 : item.rfind( '.' ) ] for item in self.phones ]
		    self.sounds = [ mixer.Sound( self.sound ) for self.sound in self.phones ]
	    
	    self.SetBackgroundColour( 'black' )
		
	#-------------------------------------------------------------------------
        def initializeBitmaps(self):
            
            labelFiles = [ self.pathToATPlatform + file for file in [ 'icons/speller/special_characters.png', 'icons/speller/undo.png', 'icons/speller/speak.png', 'icons/speller/save.png', 'icons/speller/open.png', 'icons/speller/exit.png', ] ]
            
            self.labelBitmaps = { }
	    
	    labelBitmapIndex = [ self.labels[ 0 ].index( self.labels[ 0 ][ -7 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -6 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -5 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -4 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -2 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -1 ] ) ]

            for labelFilesIndex, labelIndex in enumerate( labelBitmapIndex ):
		    self.labelBitmaps[ self.labels[ 0 ][ labelIndex ] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[ labelFilesIndex ], 'rb' )) )      

            self.labelBitmaps2 = { }
	    
	    labelBitmapIndex2 = [ self.labels[ 1 ].index( self.labels[ 1 ][ -6 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -5 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -4 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -2 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -1 ] ) ]

            for labelFilesIndex2, labelIndex2 in enumerate( labelBitmapIndex2 ):
		    self.labelBitmaps2[ self.labels[ 1 ][ labelIndex2 ] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[ -5: ][ labelFilesIndex2 ], 'rb' )) )

	#-------------------------------------------------------------------------	
	def createGui(self):
		
		self.mainSizer = wx.BoxSizer( wx.VERTICAL )
		self.textField = wx.TextCtrl( self, style = wx.TE_LEFT, size = ( self.winWidth, 0.2 * self.winHeight ) )
		self.textField.SetFont( wx.Font( 60, wx.SWISS, wx.NORMAL, wx.NORMAL ) )
		self.mainSizer.Add( self.textField, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3 )
		
		self.subSizers = [ ]
		
		subSizer = wx.GridBagSizer( 3, 3 )

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')

		for index_1, item in enumerate( self.labels[ 0 ][ :-7 ] ):
			b = bt.GenButton( self, -1, item, name = item, size = ( 0.985*self.winWidth / self.numberOfColumns[ 0 ], 0.745 * self.winHeight / self.numberOfRows[ 0 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )

			if item in self.colouredLabels and self.vowelColour != 'False':
				b.SetForegroundColour( self.vowelColour )
			else:
				b.SetForegroundColour( self.textColour )

			b.Bind( event, self.onPress )
			subSizer.Add( b, ( index_1 / self.numberOfColumns[ 0 ], index_1 % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

		for index_2, item in enumerate( self.labels[ 0 ][ -7 : -3 ], start = 1 ):
			b = bt.GenBitmapButton( self, -1, name = item, bitmap = self.labelBitmaps[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index_1 + index_2 ) / self.numberOfColumns[ 0 ], ( index_1 + index_2 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

		for item in ( self.labels[ 0 ][ -3 ], ):
			b = bt.GenButton( self, -1, item, name = item, size = ( 3 * 0.985*self.winWidth / self.numberOfColumns[ 0 ], 0.745 * self.winHeight / self.numberOfRows[ 0 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetForegroundColour( self.textColour )
			b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index_1 + index_2 ) / self.numberOfColumns[ 0 ], ( index_1 + index_2 + 1 ) % self.numberOfColumns[ 0 ] ), ( 1, 3 ), wx.EXPAND )

		for index_3, item in enumerate( self.labels[ 0 ][ -2: ], start = 4 ):
			b = bt.GenBitmapButton( self, -1, name = item, bitmap = self.labelBitmaps[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )
			subSizer.Add( b, ( ( index_1 + index_2 + index_3 ) / self.numberOfColumns[ 0 ], ( index_1 + index_2 + index_3 ) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

		self.subSizers.append( subSizer )		    
		self.mainSizer.Add( self.subSizers[ 0 ], proportion = 1, flag = wx.EXPAND )
		self.SetSizer( self.mainSizer )
		self.Center( )
		
		subSizer2 = wx.GridBagSizer( 3, 3 )

		for index_1, item in enumerate( self.labels[ 1 ][ :-6 ] ):
			b = bt.GenButton( self, -1, item, name = item, size = ( 0.985*self.winWidth / self.numberOfColumns[ 1 ], 0.7 * self.winHeight / self.numberOfRows[ 1 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetForegroundColour( self.textColour )
			b.Bind( event, self.onPress )
			subSizer2.Add( b, ( index_1 / self.numberOfColumns[ 1 ], index_1 % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )

		for index_2, item in enumerate( self.labels[ 1 ][ -6 : -3 ], start = 1 ):
			b = bt.GenBitmapButton( self, -1, name = item, bitmap = self.labelBitmaps2[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )
			subSizer2.Add( b, ( ( index_1 + index_2 ) / self.numberOfColumns[ 1 ], ( index_1 + index_2 ) % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )

		for item in ( self.labels[ 1 ][ -3 ], ):
			b = bt.GenButton( self, -1, item, name = item, size = ( 3 * 0.985*self.winWidth / self.numberOfColumns[ 1 ], 0.7 * self.winHeight / self.numberOfRows[ 1 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetForegroundColour( self.textColour )
			b.Bind( event, self.onPress )
			subSizer2.Add( b, ( ( index_1 + index_2 ) / self.numberOfColumns[ 1 ], ( index_1 + index_2 + 1 ) % self.numberOfColumns[ 1 ] ), ( 1, 4 ), wx.EXPAND )

		for index_3, item in enumerate( self.labels[ 1 ][ -2: ], start = 5 ):
			b = bt.GenBitmapButton( self, -1, name = item, bitmap = self.labelBitmaps2[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )
			subSizer2.Add( b, ( ( index_1 + index_2 + index_3 ) / self.numberOfColumns[ 1 ], ( index_1 + index_2 + index_3 ) % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )

		self.subSizers.append( subSizer2 )		   
		self.mainSizer.Add( self.subSizers[ 1 ], proportion = 1, flag = wx.EXPAND )
		self.mainSizer.Show( item = self.subSizers[ 1 ], show = False, recursive = True )
		self.SetSizer( self.mainSizer )
		self.Center( )

	#-------------------------------------------------------------------------
	def initializeTimer(self):
		self.stoper = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper )

		if self.control != 'tracker':
			self.stoper.Start( self.timeGap )
	
	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )
	
	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):

		if self.control != 'tracker':		    
			self.mousePosition = self.winWidth/1.85, self.winHeight/1.85	
			self.mouseCursor.move( *self.mousePosition )	

		dial = wx.MessageDialog(None, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal()
		
		if ret == wx.ID_YES:
			if __name__ == '__main__':
				self.Destroy()
			else:
				self.parent.Destroy( )
				self.Destroy( )
		else:
			event.Veto()

			if self.control != 'tracker':
				self.mousePosition = self.winWidth - 8, self.winHeight - 8
				self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------
	def onExit(self):

		if __name__ == '__main__':
			self.stoper.Stop ( )
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

		if self.control == 'tracker':
			if self.pressFlag == False:
				self.button = event.GetEventObject()
				self.button.SetBackgroundColour( self.selectionColour )
				self.pressFlag = True
				self.label = event.GetEventObject().GetName()			
				self.stoper.Start( 0.15 * self.timeGap )

				if self.label == 'SPECIAL_CHARACTERS':								

					self.subSizerNumber = 1

					self.mainSizer.Show( item = self.subSizers[ 1 ], show = True, recursive = True )
					self.mainSizer.Show( item = self.subSizers[ 0 ], show = False, recursive = True )					
					self.SetSizer( self.mainSizer )

					self.Layout( )

				elif self.label == 'UNDO':
					self.typewriterForwardSound.play( )
					self.textField.Remove( self.textField.GetLastPosition( ) - 1, self.textField.GetLastPosition( ) )

				elif self.label == 'SPEAK':								
					text = str( self.textField.GetValue( ) )

					if text == '' or text.isspace( ):
						pass

					else:
						inputTable = '~!#$&( )[]{}<>;:"\|'
						outputTable = ' ' * len( inputTable )
						translateTable = maketrans( inputTable, outputTable )
						textToSpeech = text.translate( translateTable )

						replacements = { '-' : ' minus ', '+' : ' plus ', '*' : ' razy ', '/' : ' podzielić na ', '=' : ' równa się ', '%' : ' procent ' }
						textToSpeech = reduce( lambda text, replacer: text.replace( *replacer ), replacements.iteritems( ), textToSpeech )

						time.sleep( 1 )
						os.system( 'milena_say %s' %textToSpeech )

				elif self.label == 'SAVE':
					text = str( self.textField.GetValue( ) )

					if text == '':
						pass
					else:
						f = open( 'myTextFile.txt', 'w' )
						f.write( self.textField.GetValue( ) )
						f.close( )

				elif self.label == 'SPACJA':
					self.typewriterSpaceSound.play( )
					self.textField.AppendText( ' ' )

				elif self.label == 'OPEN':
					try:
						textToLoad = open( 'myTextFile.txt' ).read( )
						self.textField.Clear( )
						self.textField.AppendText( textToLoad )

					except IOError:
						pass

				elif self.label == 'EXIT':
					if self.subSizerNumber == 0:
						self.onExit( )

					else:	
					    self.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = False, recursive = True )

					    self.subSizerNumber = 0
					    self.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = True, recursive = True )

					    self.SetSizer( self.mainSizer )
					    self.Layout( )

				else:
					self.typewriterKeySound.play( )

					self.textField.AppendText( self.label )
			else:
				pass
		else:
			self.numberOfPresses += 1

			if self.numberOfPresses == 1:

				if self.flag == 'rest':
					self.flag = 'row'
					self.rowIteration = 0

				elif self.flag == 'row':

					if self.rowIteration != self.numberOfRows[ self.subSizerNumber ]:
						buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ self.subSizerNumber ], ( self.rowIteration - 1 ) * self.numberOfColumns[ self.subSizerNumber ] + self.numberOfColumns[ self.subSizerNumber ] )
					else:
						buttonsToHighlight = range( ( self.rowIteration - 1 ) * self.numberOfColumns[ self.subSizerNumber ], ( self.rowIteration - 1 ) * self.numberOfColumns[ self.subSizerNumber ] + 6 )

					for button in buttonsToHighlight:
						item = self.subSizers[ self.subSizerNumber ].GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.selectionColour )
						b.SetFocus( )
						b.Update( )

					self.flag = 'columns' 
					self.rowIteration -= 1
					self.columnIteration = 0

				elif self.flag == 'columns' and self.rowIteration != self.numberOfRows[ self.subSizerNumber ] - 1:

					item = self.subSizers[ self.subSizerNumber ].GetItem( ( self.rowIteration ) * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration - 1 )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.selectionColour )
					b.SetFocus( )
					b.Update( )

					label = self.labels[ self.subSizerNumber ][ self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration - 1 ]

					if label == 'SPECIAL_CHARACTERS':								

						self.subSizerNumber = 1

						self.mainSizer.Show( item = self.subSizers[ 1 ], show = True, recursive = True )
						self.mainSizer.Show( item = self.subSizers[ 0 ], show = False, recursive = True )					
						self.SetSizer( self.mainSizer )

						self.Layout( )

					else:
						self.typewriterKeySound.play( )

						#self.typingSound.Play(wx.SOUND_ASYNC) doesn't work. Wonder why

						self.textField.AppendText( label )

					self.flag = 'row'
					self.rowIteration = 0
					self.columnIteration = 0
					self.countColumns = 0

				elif self.flag == 'columns' and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1:

					item = self.subSizers[ self.subSizerNumber ].GetItem( ( self.rowIteration ) * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration-1 )
					b = item.GetWindow( )
					b.SetBackgroundColour( self.selectionColour )
					b.SetFocus( )
					b.Update( )

					label = self.labels[ self.subSizerNumber ][ self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration-1 ]

					if label == 'UNDO':
						self.typewriterForwardSound.play( )
						self.textField.Remove( self.textField.GetLastPosition( ) - 1, self.textField.GetLastPosition( ) )

					elif label == 'SPEAK':								
						text = str( self.textField.GetValue( ) )

						if text == '' or text.isspace( ):
							pass

						else:
							inputTable = '~!#$&( )[]{}<>;:"\|'
							outputTable = ' ' * len( inputTable )
							translateTable = maketrans( inputTable, outputTable )
							textToSpeech = text.translate( translateTable )

							replacements = { '-' : ' minus ', '+' : ' plus ', '*' : ' razy ', '/' : ' podzielić na ', '=' : ' równa się ', '%' : ' procent ' }
							textToSpeech = reduce( lambda text, replacer: text.replace( *replacer ), replacements.iteritems( ), textToSpeech )

							time.sleep( 1 )
							os.system( 'milena_say %s' %textToSpeech )

					elif label == 'SAVE':
						text = str( self.textField.GetValue( ) )

						if text == '':
							pass
						else:
							f = open( 'myTextFile.txt', 'w' )
							f.write( self.textField.GetValue( ) )
							f.close( )

					elif label == 'SPACJA':
						self.typewriterSpaceSound.play( )
						self.textField.AppendText( ' ' )

					elif label == 'OPEN':
						try:
							textToLoad = open( 'myTextFile.txt' ).read( )
							self.textField.Clear( )
							self.textField.AppendText( textToLoad )

						except IOError:
							pass

					elif label == 'EXIT':
						if self.subSizerNumber == 0:
							self.onExit( )

						else:	
						    self.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = False, recursive = True )

						    self.subSizerNumber = 0
						    self.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = True, recursive = True )

						    self.SetSizer( self.mainSizer )
						    self.Layout( )

					self.flag = 'row'
					self.rowIteration = 0
					self.columnIteration = 0
					self.countRows = 0
					self.countColumns = 0

			else:
				event.Skip( ) #Event skip use in else statement here!			
	
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

			if self.flag == 'row':

				if self.countRows == self.maxNumberOfRows:
					self.flag = 'rest'
					self.countRows = 0

					items = self.subSizers[ self.subSizerNumber ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )

				else:
					self.rowIteration = self.rowIteration % self.numberOfRows[ self.subSizerNumber ]

					items = self.subSizers[ self.subSizerNumber ].GetChildren( )
					for item in items:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )

					if self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1:
						self.countRows += 1
						buttonsToHighlight = range( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ], self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + 6 )

					else:
						buttonsToHighlight = range( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ], self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.numberOfColumns[ self.subSizerNumber ] )

					for button in buttonsToHighlight:
						item = self.subSizers[ self.subSizerNumber ].GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
						b.Update( )

					self.rowIteration += 1

					if self.voice == 'True':
						os.system( 'milena_say %i' % ( self.rowIteration ) )

			elif self.flag == 'columns':

					if self.countColumns == self.maxNumberOfColumns:
						self.flag = 'row'

						item = self.subSizers[ self.subSizerNumber ].GetItem( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration - 1 )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )

						self.rowIteration = 0
						self.columnIteration = 0
						self.countColumns = 0

					else:
						if self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] - 1 or (self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] - 3 and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] - 4 and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1 ):
							self.countColumns += 1

						if self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] or ( self.subSizerNumber == 0 and self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] - 2 and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1 ) or ( self.subSizerNumber == 1 and self.columnIteration == self.numberOfColumns[ self.subSizerNumber ] - 3 and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1 ):
							self.columnIteration = 0

						items = self.subSizers[ self.subSizerNumber ].GetChildren( )
						for item in items:
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )
							b.Update( )

						item = self.subSizers[ self.subSizerNumber ].GetItem( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
						b.Update( )

						if self.voice == 'True':
							label = self.labels[ self.subSizerNumber ][ self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration ]

							try:
								soundIndex = self.phoneLabels.index( [ item for item in self.phoneLabels if item == label ][ 0 ] )
								sound = self.sounds[ soundIndex ]
								sound.play( )

							except IndexError:
								pass

						self.columnIteration += 1

			else:
				pass


#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = speller( parent = None, id = -1 )
	frame.Show( True )
	app.MainLoop( )
