# Dinh, Tonytam T.
# ttd3179
# 2019-11-04
#---------#---------#---------#---------#---------#--------#
import sys

from .common       import *

#---------#---------#---------#---------#---------#--------#
class Statement_Continue() :
  def __init__( self, lineNum ) :
    self.m_NodeType = 'Statement_Continue'

    self.m_LineNum   = lineNum

  #---------------------------------------
  def dump( self, indent = 0, fp = sys.stdout ) :
    dumpHeaderLine( indent, self.m_LineNum,
      'STATEMENT (CONTINUE)', fp )

#---------#---------#---------#---------#---------#--------#
