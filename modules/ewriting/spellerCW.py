#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of AT-Platform.
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
wxversion.select( '2.8' )

import glob, os, time
import wx
import wx.lib.buttons as bt

from pymouse import PyMouse
from pygame import mixer
import subprocess as sp
import shlex

import numpy as np

#=============================================================================
class speller( wx.Frame ):

	def __init__(self, parent):

                self.winWidth, self.winHeight = wx.DisplaySize( )

		self.parent = parent

		self.initializeParameters( )
		self.initializeBitmaps( )
		self.createGui( )

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
					print 'Błąd w linii', line
					
					self.timeGap = 1500
					self.backgroundColour = 'white'
					self.textColour = 'black'
					self.scanningColour =  '#E7FAFD'
					self.selectionColour = '#9EE4EF'
					self.filmVolumeLevel = 100
					self.musicVolumeLevel = 70
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
				    
					self.voice = False
					self.vowelColour = 'red'
					self.polishLettersColour = 'blue'

                with open( self.pathToATPlatform + 'ewritingParameters', 'r' ) as parametersFile:
			for line in parametersFile:                                                                

                                if line[ :line.find('=')-1 ] == 'textSize':
					self.textSize = int( line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'maxPoints':
					self.maxPoints = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'checkTime':
                                        self.checkTime = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'colorGrat':
					self.colorGrat = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'colorNiest':
                                        self.colorNiest = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'ileLuk':
                                        self.ileLuk = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'sex':
                                        self.sex = line[ line.rfind('=')+2:-1 ]
		
				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w linii', line
					
					self.textSize = 80
					self.checkTime = 8000
					self.colorGrat = 'lime green'
					self.colorNiest = 'indian red'
					self.ileLuk = 1
					self.maxPoints = 2
					self.sex = 'D'

                self.labels = [ 'A E B C D F G H I O J K L M N P U Y R S T W Z SPECIAL_CHARACTERS DELETE TRASH CHECK ORISPEAK SPEAK EXIT'.split( ), '1 2 3 4 5 6 7 8 9 0 + - * / = % $ & . , ; : " ? ! @ # ( ) [ ] { } < > ~ DELETE TRASH CHECK ORISPEAK SPEAK EXIT'.split( ) ]
                self.colouredLabels = [ 'A','E','I','O','U','Y']

                self.voice = False
		self.slowo = self.parent.WORD

		if self.ileLuk >= len( self.slowo ):
                        self.ileLuk = len( self.slowo ) - 1

                self.numberOfRows = [ 4, 5 ]
                self.numberOfColumns = [ 8, 9 ]
				
                self.flag = 'row'						
		self.pressFlag = False
                self.rowIteration = 0						
                self.columnIteration = 0							
                self.countRows = 0
                self.countColumns = 0										

                self.maxNumberOfColumns = 2									
	    
                self.numberOfPresses = 1
                self.subSizerNumber = 0

                self.mouseCursor = PyMouse( )
		self.mousePosition = self.winWidth - 8, self.winHeight - 8
		self.mouseCursor.move( *self.mousePosition )			

                mixer.init( )
                self.typewriterKeySound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_key.wav' )
                self.typewriterForwardSound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_forward.wav' )
                self.typewriterSpaceSound = mixer.Sound( self.pathToATPlatform + 'sounds/typewriter_space.wav' )
                
                self.phones = glob.glob( self.pathToATPlatform+'sounds/phone/*' )
                self.phoneLabels = [ item[ item.rfind( '/' )+1 : item.rfind( '.' ) ] for item in self.phones ]
                self.sounds = [ mixer.Sound( self.sound ) for self.sound in self.phones ]
	    
                self.parent.SetBackgroundColour( 'black' )
		
	#-------------------------------------------------------------------------
        def initializeBitmaps(self):

            self.path=self.pathToATPlatform+'icons/ewriting/'
            labelFiles = [ file for file in [ self.path+'speller/special_characters.png', self.path+'speller/DELETE.png', self.path+'speller/TRASH.png',   self.path+'speller/CHECK.png',self.path+'speller/ORISPEAK.png', self.path+'speller/SPEAK.png', self.path+'speller/exit.png', ] ]
            
            self.labelBitmaps = { }
	    
	    labelBitmapIndex = [ self.labels[ 0 ].index( self.labels[ 0 ][ -7 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -6 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -5 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -4 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -3 ] ),self.labels[ 0 ].index( self.labels[ 0 ][ -2 ] ), self.labels[ 0 ].index( self.labels[ 0 ][ -1 ] ) ]

            for labelFilesIndex, labelIndex in enumerate( labelBitmapIndex ):
		    self.labelBitmaps[ self.labels[ 0 ][ labelIndex ] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[ labelFilesIndex ], 'rb' )) )      

            self.labelBitmaps2 = { }
	    
	    labelBitmapIndex2 = [ self.labels[ 1 ].index( self.labels[ 1 ][ -6 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -5 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -4 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -3 ] ),self.labels[ 1 ].index( self.labels[ 1 ][ -2 ] ), self.labels[ 1 ].index( self.labels[ 1 ][ -1 ] ) ]

            for labelFilesIndex2, labelIndex2 in enumerate( labelBitmapIndex2 ):
		    self.labelBitmaps2[ self.labels[ 1 ][ labelIndex2 ] ] = wx.BitmapFromImage( wx.ImageFromStream( open( labelFiles[ 1: ][ labelFilesIndex2 ], 'rb' )) )

	#-------------------------------------------------------------------------	
	def createGui(self):
		
		self.textField = wx.TextCtrl( self.parent, style = wx.TE_CENTRE | wx.TE_RICH2, size = ( self.winWidth, 0.2 * ( self.winHeight - 100 ) ) )
		self.textField.SetFont( wx.Font(  69, wx.SWISS, wx.NORMAL, wx.NORMAL ) )
		self.parent.mainSizer.Add( self.textField, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3 )
		
		self.subSizers = [ ]
		
		subSizer = wx.GridBagSizer( 3, 3 )

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')

		for index_1, item in enumerate( self.labels[ 0 ][ :-7 ] ):
			b = bt.GenButton( self.parent, -1, item, name = item, size = ( 0.985*self.winWidth / self.numberOfColumns[ 0 ], 0.79 * self.winHeight / self.numberOfRows[ 0 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )

			if item in self.colouredLabels and self.vowelColour != 'False':
				b.SetForegroundColour( self.vowelColour )
			else:
				b.SetForegroundColour( self.textColour )

			b.Bind( event, self.onPress )
			subSizer.Add( b, ( index_1 / self.numberOfColumns[ 0 ], index_1 % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )

		for index_2, item in enumerate( self.labels[ 0 ][ -7 : ] ):
			b = bt.GenBitmapButton( self.parent, -1, name = item, bitmap = self.labelBitmaps[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )

                        if index_2 == 3:
                                subSizer.Add( b, ( ( index_1 + index_2 +1) / self.numberOfColumns[ 0 ], ( index_1 + index_2+1 ) % self.numberOfColumns[ 0 ] ), (1,3), wx.EXPAND )
                        elif index_2 > 3:
                                subSizer.Add( b, ( ( index_1 + index_2 +3) / self.numberOfColumns[ 0 ], ( index_1 + index_2 +3) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
                        else:
                                subSizer.Add( b, ( ( index_1 + index_2+1 ) / self.numberOfColumns[ 0 ], ( index_1 + index_2 +1) % self.numberOfColumns[ 0 ] ), wx.DefaultSpan, wx.EXPAND )
                        
		self.subSizers.append( subSizer )		    
		self.parent.mainSizer.Add( self.subSizers[ 0 ], proportion = 1, flag = wx.EXPAND )
		self.parent.SetSizer( self.parent.mainSizer )
		
		subSizer2 = wx.GridBagSizer( 3, 3 )

		for index_1, item in enumerate( self.labels[ 1 ][ :-6 ] ):
			b = bt.GenButton( self.parent, -1, item, name = item, size = ( 0.985*self.winWidth / self.numberOfColumns[ 1 ], 0.75 * self.winHeight / self.numberOfRows[ 1 ] ) )
			b.SetFont( wx.Font( 35, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
			b.SetBezelWidth( 3 )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetForegroundColour( self.textColour )
			b.Bind( event, self.onPress )
			subSizer2.Add( b, ( index_1 / self.numberOfColumns[ 1 ], index_1 % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )

		for index_2, item in enumerate( self.labels[ 1 ][ -6 :  ] ):
			b = bt.GenBitmapButton( self.parent, -1, name = item, bitmap = self.labelBitmaps2[ item ] )
			b.SetBackgroundColour( self.backgroundColour )
			b.SetBezelWidth( 3 )
                        b.Bind( event, self.onPress )

			if index_2 == 2:
                                subSizer2.Add( b, ( ( index_1 + index_2 +1) / self.numberOfColumns[ 1 ], ( index_1 + index_2 +1) % self.numberOfColumns[ 1 ] ), (1,4), wx.EXPAND )
                        elif index_2 > 2:
                                subSizer2.Add( b, ( ( index_1 + index_2 +4) / self.numberOfColumns[ 1], ( index_1 + index_2+4 ) % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )
                        else:
                                subSizer2.Add( b, ( ( index_1 + index_2+1 ) / self.numberOfColumns[ 1 ], ( index_1 + index_2 +1) % self.numberOfColumns[ 1 ] ), wx.DefaultSpan, wx.EXPAND )
                        
		self.subSizers.append( subSizer2 )		   
		self.parent.mainSizer.Add( self.subSizers[ 1 ], proportion = 1, flag = wx.EXPAND )
		self.parent.mainSizer.Show( item = self.subSizers[ 1 ], show = False, recursive = True )
		self.parent.SetSizer( self.parent.mainSizer )
		
		ktore=[ ] #ktore litery wykropkowac

		if len( self.slowo ) == 2:
                        ktore = [ 1 ]
                else:
                        while len( ktore ) < self.ileLuk:
                                ktore.append( np.random.randint( 0, len( self.slowo ), 1 )[ 0 ] )
                                ktore = list( set( ktore ) )

		slowo = list( self.slowo )
		ktore = sorted( ktore )
		self.samogloski = [ ]

		for i in ktore:
                        slowo[ i ] = '_'       

                self.ktore = ktore
		self.textField.WriteText( u''.join( slowo ) )
		self.ilejuz = 0
		self.czyjuz = False
		self.parent.Layout( )

	#----------------------------------------------------------------------------
	def onExit(self):

                self.parent.PicNr -= 1
		self.parent.stoper2.Stop( )
		self.parent.back( )
		
	#----------------------------------------------------------------------------
        def czytajLitere(self, litera):

                soundIndex = self.phoneLabels.index( [ item for item in self.phoneLabels if litera in item ][ 0 ] )
		sound = self.sounds[ soundIndex ]
		sound.play( )
                self.parent.SetFocus( )
                time.sleep( 1 )

	#----------------------------------------------------------------------------
	def onPress(self, event):

		if self.control == 'tracker':
			if self.pressFlag == False:
				self.button = event.GetEventObject( )
				self.button.SetBackgroundColour( self.selectionColour )
				self.pressFlag = True
				self.label = event.GetEventObject().GetName().encode( 'utf-8' )
				# print self.label
				# exit()
				self.parent.stoper2.Start( 0.15 * self.timeGap )

				if self.label == 'SPECIAL_CHARACTERS':								

					self.subSizerNumber = 1

					self.parent.mainSizer.Show( item = self.subSizers[ 1 ], show = True, recursive = True )
					self.parent.mainSizer.Show( item = self.subSizers[ 0 ], show = False, recursive = True )					
					self.parent.SetSizer( self.parent.mainSizer )
					self.parent.Layout( )
					if self.voice:
						item = self.button
						b = item.GetWindow( )
						b.SetBackgroundColour( 'indian red' )
						b.SetFocus( )
						b.Update( )
					else:
						item = self.button
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )

				elif self.label == 'DELETE':
					if self.ilejuz > 0 and self.czyjuz: 
						self.typewriterForwardSound.play( )
						self.textField.Replace( self.textField.GetInsertionPoint( ) - 1, self.textField.GetInsertionPoint( ), '_' )
						self.ilejuz -= 1
						self.czyjuz = False

				elif self.label == 'SPEAK':
					if not self.voice:
						self.voice = True
						b = self.button
						b.SetBackgroundColour( 'indian red' )
						b.SetFocus( )
						b.Update( )
					else:
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )
						self.voice = False

				elif self.label == 'ORISPEAK':
					self.parent.stoper2.Stop( )
					if str( self.parent.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):
						command = 'sox -m ' + self.pathToATPlatform + 'sounds/phone/' + list( self.parent.word )[ 0 ].swapcase( ) + '.wav'
						ile = 0
						for l in list( self.parent.word )[ 1: ]:
							ile += 2
							command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase() + '.wav' + ' -p pad ' + str( ile ) + '"'
						command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.parent.word + '.ogg'
						wykonaj = sp.Popen( shlex.split( command ) )

					time.sleep( 1.5 )
					do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.parent.word + '.ogg' )
					do_literowania.play( )
					self.parent.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

				elif self.label == 'TRASH':
					text = self.textField.GetValue( )

					if text.count( '_' ) < self.ileLuk:
						self.typewriterForwardSound.play( )
						for i in self.ktore:
							self.textField.Replace( i, i + 1, '_' )
							self.ilejuz = 0

				elif self.label == 'EXIT':

					if self.subSizerNumber == 0:
						self.onExit( )

					else:	
						self.parent.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = False, recursive = True )

						self.subSizerNumber = 0
						self.parent.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = True, recursive = True )

						self.parent.SetSizer( self.parent.mainSizer )
						self.parent.Layout( )

						if self.voice:
							b = self.button
							# b = item.GetWindow( )
							b.SetBackgroundColour( 'indian red' )
							b.SetFocus( )
							b.Update( )
						else:
							b = self.button
							# b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )
							b.Update( )

				elif self.label == 'CHECK':
					self.parent.stoper2.Stop( )
					self.parent.ownWord = self.textField.GetValue( )
					self.parent.check( )

				else:
					if self.ilejuz < self.ileLuk:
						self.typewriterKeySound.play( )
						self.textField.SetInsertionPoint( self.ktore[ self.ilejuz ] )
						self.textField.Remove( self.textField.GetInsertionPoint( ), self.textField.GetInsertionPoint( ) + 1 )
						self.textField.WriteText( self.label )
						self.ilejuz += 1
						self.czyjuz = True

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

					for i, button in enumerate( buttonsToHighlight ):
						if self.rowIteration - 1 == self.numberOfRows[ self.subSizerNumber ] - 1 and i == len( buttonsToHighlight ) - 2 and self.voice:
							pass
						else:
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

						self.parent.mainSizer.Show( item = self.subSizers[ 1 ], show = True, recursive = True )
						self.parent.mainSizer.Show( item = self.subSizers[ 0 ], show = False, recursive = True )					
						self.parent.SetSizer( self.parent.mainSizer )
						self.parent.Layout( )
						if self.voice:
							item = self.subSizers[ self.subSizerNumber ].GetItem( self.numberOfRows[self.subSizerNumber ] * self.numberOfColumns[ self.subSizerNumber ] - 5 )
							b = item.GetWindow( )
							b.SetBackgroundColour( 'indian red' )
							b.SetFocus( )
							b.Update( )
						else:
							item = self.subSizers[ self.subSizerNumber ].GetItem( self.numberOfRows[self.subSizerNumber ] * self.numberOfColumns[ self.subSizerNumber ] - 5 )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )
							b.Update( )

					else:
						if self.ilejuz < self.ileLuk:
							self.typewriterKeySound.play( )
							self.textField.SetInsertionPoint( self.ktore[ self.ilejuz ] )
							self.textField.Remove( self.textField.GetInsertionPoint( ), self.textField.GetInsertionPoint( ) + 1 )
							self.textField.WriteText( label )
							self.ilejuz += 1
							self.czyjuz = True

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

					if label == 'DELETE':
						if self.ilejuz > 0 and self.czyjuz: 
							self.typewriterForwardSound.play( )
							self.textField.Replace( self.textField.GetInsertionPoint( ) - 1, self.textField.GetInsertionPoint( ), '_' )
							self.ilejuz -= 1
							self.czyjuz = False

					elif label == 'SPEAK':
						if not self.voice:
							self.voice = True
							b.SetBackgroundColour( 'indian red' )
							b.SetFocus( )
							b.Update( )
						else:
							b.SetBackgroundColour( self.backgroundColour )
							b.SetFocus( )
							b.Update( )
							self.voice = False

					elif label == 'ORISPEAK':
						self.parent.stoper2.Stop( )
						if str( self.parent.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):
							command = 'sox -m ' + self.pathToATPlatform + 'sounds/phone/' + list( self.parent.word )[ 0 ].swapcase( ) + '.wav'
							ile = 0
							for l in list( self.parent.word )[ 1: ]:
								ile += 2
								command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase() + '.wav' + ' -p pad ' + str( ile ) + '"'
							command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.parent.word + '.ogg'
							wykonaj = sp.Popen( shlex.split( command ) )

						time.sleep( 1.5 )
						do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.parent.word + '.ogg' )
						do_literowania.play( )
						self.parent.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

					elif label == 'TRASH':
						text = self.textField.GetValue( )

						if text.count( '_' ) < self.ileLuk:
							self.typewriterForwardSound.play( )
							for i in self.ktore:
								self.textField.Replace( i, i + 1, '_' )
								self.ilejuz = 0

					elif label == 'EXIT':

						if self.subSizerNumber == 0:
							self.onExit( )

						else:	
							self.parent.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = False, recursive = True )

							self.subSizerNumber = 0
							self.parent.mainSizer.Show( item = self.subSizers[ self.subSizerNumber ], show = True, recursive = True )

							self.parent.SetSizer( self.parent.mainSizer )
							self.parent.Layout( )

							if self.voice:
								item = self.subSizers[ 0 ].GetItem( self.numberOfRows[ self.subSizerNumber ] * self.numberOfColumns[ self.subSizerNumber ] -4 )
								b = item.GetWindow( )
								b.SetBackgroundColour( 'indian red' )
								b.SetFocus( )
								b.Update( )
							else:
								item = self.subSizers[ 0 ].GetItem( self.numberOfRows[ self.subSizerNumber ] * self.numberOfColumns[ self.subSizerNumber ] - 4 )
								b = item.GetWindow( )
								b.SetBackgroundColour( self.backgroundColour )
								b.SetFocus( )
								b.Update( )

					else:
						self.parent.stoper2.Stop( )
						self.parent.ownWord = self.textField.GetValue( )
						self.parent.check( )

					self.flag = 'row'
					self.rowIteration = 0
					self.columnIteration = 0
					self.countRows = 0
					self.countColumns = 0

			else:
				event.Skip( )		
	
	#-------------------------------------------------------------------------
	def timerUpdate(self, event):

		if self.control == 'tracker':
			try:
				if self.button.GetBackgroundColour( ) == self.backgroundColour:
					self.button.SetBackgroundColour( self.selectionColour )

				else:
					self.button.SetBackgroundColour( self.backgroundColour )	

				self.parent.stoper2.Stop( )
				self.pressFlag = False
			except AttributeError:
				pass
		else:

			self.mouseCursor.move( *self.mousePosition )

			self.numberOfPresses = 0		

			if self.flag == 'row':

				self.rowIteration = self.rowIteration % self.numberOfRows[ self.subSizerNumber ]

				items = self.subSizers[ self.subSizerNumber ].GetChildren( )

				for i, item in enumerate( items ):
					if self.voice and i == len( items ) - 2:
						pass

					else:
						b = item.GetWindow( )
						b.SetBackgroundColour( self.backgroundColour )
						b.SetFocus( )
						b.Update( )

				if self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1:
					self.countRows += 1
					buttonsToHighlight = range( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ], self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + 6 )

				else:
					buttonsToHighlight = range( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ], self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.numberOfColumns[ self.subSizerNumber ] )

				for i, button in enumerate( buttonsToHighlight ):

					if self.voice and i == len( buttonsToHighlight ) - 2 and self.rowIteration == self.numberOfRows[ self.subSizerNumber ] - 1:
						pass
					else:
						item = self.subSizers[ self.subSizerNumber ].GetItem( button )
						b = item.GetWindow( )
						b.SetBackgroundColour( self.scanningColour )
						b.SetFocus( )
						b.Update( )

				self.rowIteration += 1

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

						for i, item in enumerate( items ):

							if self.voice and i == len(items)-2:
								b = item.GetWindow( )
								b.SetBackgroundColour( 'indian red' )
								b.SetFocus( )
								b.Update( )
							else:
								b = item.GetWindow( )
								b.SetBackgroundColour( self.backgroundColour )
								b.SetFocus( )
								b.Update( )

						if self.voice and self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration == self.numberOfRows[ self.subSizerNumber ] * self.numberOfColumns[ self.subSizerNumber ] - ( 4 + self.subSizerNumber ):
							item = self.subSizers[ self.subSizerNumber ].GetItem( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration )
							b = item.GetWindow( )
							b.SetBackgroundColour( 'orange red')
							b.SetFocus( )
							b.Update( )
						else:
							item = self.subSizers[ self.subSizerNumber ].GetItem( self.rowIteration * self.numberOfColumns[ self.subSizerNumber ] + self.columnIteration )
							b = item.GetWindow( )
							b.SetBackgroundColour( self.scanningColour )
							b.SetFocus( )
							b.Update( )

						if self.voice and self.subSizerNumber == 0 and self.rowIteration != self.numberOfRows[ 0 ] - 1:

							self.parent.stoper2.Stop( )
							label = self.labels[ 0 ][ self.rowIteration * self.numberOfColumns[ 0 ]+ self.columnIteration ]

							if label != 'SPECIAL_CHARACTERS':
								self.czytajLitere( label )
							else:
								time.sleep( 1.5 )

							self.parent.stoper2.Start( self.timeGap )

						self.columnIteration += 1
