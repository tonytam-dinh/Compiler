# Dinh, Tonytam T.
# ttd3179
# 2019-11-04
#---------#---------#---------#---------#---------#--------#
import sys

from .common       import *

#---------#---------#---------#---------#---------#--------#
class Statement_Break() :
  def __init__( self, lineNum ) :
    self.m_NodeType = 'Statement_Break'

    self.m_LineNum   = lineNum

  #---------------------------------------
  def dump( self, indent = 0, fp = sys.stdout ) :
    dumpHeaderLine( indent, self.m_LineNum,
      'STATEMENT (BREAK)', fp )

#---------#---------#---------#---------#---------#--------#
