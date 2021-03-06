# Dinh, Tonytam T.
# ttd3179
# 2019-11-04
#---------#---------#---------#---------#---------#--------#
import logging
import sys
import traceback

import ply
import ply.yacc
import ply.lex

from pathlib            import Path
from time               import time

from Exceptions         import *
from ParseTree          import *

#---------#---------#---------#---------#---------#--------#
# Lexical analysis section

reserved = { rw : rw.upper() for rw in (
  'for', 'to', 'by', 'do', 'end',
  'if', 'then', 'elif', 'else',
  'while',
  'break', 'continue',

  'read', 'write',

  'int', 'real',
  ) }

tokens = [
  'ID', 'INT_LITERAL', 'REAL_LITERAL', 'STRING_LITERAL',
  'ASSIGN',
  'PLUS', 'MINUS',
  'MULTIPLY', 'DIVIDE', 'MODULUS',
  'EXPONENTIATION',
  'LPAREN', 'RPAREN', 'SEMICOLON', 'COMMA',
  'LBRACE', 'RBRACE',
  'AND', 'OR',
  'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
  'FACTORIAL',
  ] + list( reserved.values() )

# Tokens

t_AND       = r'&&'
t_OR        = r'\|\|'
t_EQ        = r'=='
t_NE        = r'<>'
t_LT        = r'<'
t_LE        = r'<='
t_GT        = r'>'
t_GE        = r'>='
t_FACTORIAL = r'!'

t_ASSIGN    = r'='
t_COMMA     = r','
t_DIVIDE    = r'/'
t_EXPONENTIATION = r'\^'
t_LBRACE    = r'{'
t_LPAREN    = r'\('
t_MINUS     = r'-'
t_MODULUS   = r'%'
t_MULTIPLY  = r'\*'
t_PLUS      = r'\+'
t_RBRACE    = r'}'
t_RPAREN    = r'\)'
t_SEMICOLON = r';'

def t_ID( t ) :
  r'[a-zA-Z_][a-zA-Z0-9_]*'
  t.type = reserved.get( t.value, 'ID' )
  return t

def t_REAL_LITERAL( t ) :
  r'((\d*(\d\.|\.\d)\d*)([eE][-+]?\d+)?)|(\d+([eE][-+]?\d+))'
  t.value = float( t.value )
  return t

def t_INT_LITERAL( t ) :
  r'\d+'
  t.value = int( t.value )
  return t

# TODO: Add t_STRING_LITERAL( t ) here.
#       Ensure that you deal with empty strings and strings
#       that use the escape sequences \", \\, \a, \b, \e, \f, \n,
#       \r, \t, and \v.  Note that Python does not support all
#       these escapes so you'll have to hand-code some of them.
def t_STRING_LITERAL( t ) :
  r' "(\\.|[^"]|\\")*" '
  t.type = reserved.get( t.value, 'STRING_LITERAL' )
  t.value = t.value.strip('\"')
  #t.value = t.value.replace('\\\\','\\')
  t.value = t.value.replace('\\a','\x07') #7
  t.value = t.value.replace('\\b','\x08') #8
  t.value = t.value.replace('\\e','\x1b') #27
  t.value = t.value.replace('\\f','\x0c') #12
  t.value = t.value.replace('\\r','\r') #13
  t.value = t.value.replace('\\t','\t') #9
  t.value = t.value.replace('\\n','\n')
  t.value = t.value.replace('\\v','\x0b') #11
  t.value = t.value.replace('\\\\','\\')
  #REALLY DUMB WAY TO DO THIS; DON'T JUDGE ME TOO HARD
  t.value = t.value.replace('\\\x07','\\a') #7
  t.value = t.value.replace('\\\x08','\\b') #8
  t.value = t.value.replace('\\\x1b','\\e') #27
  t.value = t.value.replace('\\\x0c','\\f') #12
  t.value = t.value.replace('\\\r','\\r') #13
  t.value = t.value.replace('\\\t','\\t') #9
  t.value = t.value.replace('\\\n','\\n')
  t.value = t.value.replace('\\\x0b','\\v') #11
  return t
#-------------------
# Ignored characters
# Space, formfeed, carriage return, tab, vertical tab
t_ignore = ' \f\r\t\v'

# Eats characters from the // marker to the end of the line.
def t_comment( _ ) :
  r'//[^\n]*'

# Keep track of what line we're on.
def t_newline( t ) :
  r'\n+'
  t.lexer.lineno += t.value.count( '\n' )

#-------------------
def t_error( t ) :
  # Go through elaborate shennanigans to determine the column
  # at which the lexical error occurred.
  lineStart = t.lexer.lexdata.rfind('\n', 0, t.lexer.lexpos) + 1
  column = t.lexer.lexpos - lineStart + 1

  msg = f'Illegal character "{t.value[0]}" at line {t.lexer.lineno}, column {column}.'

  raise LexicalError( msg )

#---------#---------#---------#---------#---------#--------#
# Syntactic analysis section

#-------------------
# The start symbol.
start = 'program'

#-------------------
# Precedence rules for the operators
precedence = (
  ( 'right', 'ASSIGN' ),
  ( 'left',  'OR' ),
  ( 'left',  'AND' ),
  ( 'left',  'EQ', 'NE' ),
  ( 'left',  'LT', 'LE', 'GT', 'GE' ),
  ( 'left',  'PLUS', 'MINUS' ),
  ( 'left',  'MULTIPLY', 'DIVIDE', 'MODULUS' ),
  ( 'right', 'EXPONENTIATION' ),
  ( 'right', 'UMINUS', 'UPLUS' ),
  ( 'left',  'FACTORIAL' ),
  )

#-------------------
# PROGRAM ...

def p_program( p ) :
  'program : block'
  p[0] = Program( p.lineno( 1 ), p[1] )

def p_block( p ) :
  'block : LBRACE statement_list semicolon_opt RBRACE'
  p[0] = Statement_List( p.lineno( 1 ), p[2] )

def p_semicolon_opt( p ) :
  '''semicolon_opt : epsilon
                   | SEMICOLON'''

#-------------------
# STATEMENTS ...

# Break statement
def p_statement_break( p ) :
  'statement : BREAK'
  p[0] = Statement_Break( p.lineno( 1 ) )

# Continue statement
def p_statement_continue( p ) :
  'statement : CONTINUE'
  p[0] = Statement_Continue( p.lineno( 1 ) )

# Declaration
def p_statement_decl( p ) :
  'statement : type identifier init_opt'
  p[0] = Statement_Declaration( p.lineno( 1 ), p[1], p[2], p[3] )

def p_type( p ) :
  '''type : INT
          | REAL'''
  p[0] = Type( p.lineno( 1 ), p[1] )

def p_init_opt( p ) :
  '''init_opt : epsilon
              | ASSIGN expression'''
  if p[1] is None :
    p[0] = Expression_Literal( 0, Type( 0, 'int' ), 0 )

  else :
    p[0] = p[2]

# Expression statement
def p_statement_expr( p ) :
  'statement : expression'
  p[0] = Statement_Expression( p.lineno( 1 ), p[1] )

# For statement
def p_statement_for( p ) :
  'statement : FOR identifier ASSIGN expression TO expression step_opt DO statement_list semicolon_opt END FOR'
  p[0] = Statement_For( p.lineno( 1 ), p[2], p[4], p[6], p[7], Statement_List( p.lineno( 9 ), p[9] ) )

def p_step_opt( p ) :
  '''step_opt : epsilon
              | BY expression'''
  if p[1] == None :
    p[0] = Expression_Literal( 0, Type( 0, 'int' ), 1 )

  else :
    p[0] = p[2]

# If statement
def p_statement_if( p ) :
  'statement : IF expression THEN statement_list semicolon_opt elif_opt else_opt END IF'
  p[0] = Statement_If( p.lineno( 1 ), p[2], Statement_List( p.lineno( 4 ), p[4] ), p[6], p[7] )

def p_elif_opt( p ) :
  '''elif_opt : epsilon
              | elif_opt ELIF expression THEN statement_list semicolon_opt'''
  if p[1] is None :
    p[0] = []

  else :
    p[1].append( ( p[3], Statement_List( p.lineno( 5 ), p[5] ) ) )
    p[0] = p[1]

def p_else_opt( p ) :
  '''else_opt : epsilon
              | ELSE statement_list semicolon_opt'''
  if p[1] is None :
    p[0] = Statement_List( 0, [] )

  else :
    p[0] = Statement_List( p.lineno( 2 ), p[2] )

# Read statement
def p_statement_read( p ) :
  'statement : READ LPAREN id_list RPAREN'
  p[0] = Statement_Read( p.lineno( 1 ), p[3] )

def p_id_list( p ) :
  '''id_list : id_list COMMA identifier
             | identifier'''
  if isinstance( p[1], list ) :
    p[1].append( p[3] )
    p[0] = p[1]

  else :
    p[0] = [ p[1] ]

# While statement
def p_statement_while( p ) :
  'statement : WHILE expression DO statement_list semicolon_opt END WHILE'
  p[0] = Statement_While( p.lineno( 1 ), p[2], Statement_List( p.lineno( 4 ), p[4] ) )

# Write statement
def p_statement_write( p ) :
  'statement : WRITE LPAREN expression_list_opt RPAREN'
  p[0] = Statement_Write( p.lineno( 1 ), p[3] )

def p_expression_list_opt( p ) :
  '''expression_list_opt : epsilon
                         | expression_list'''
  if p[1] is None :
    p[0] = []

  else :
    p[0] = p[1]

def p_expression_list_A( p ) :
  'expression_list : expression_list COMMA expression'
  p[1].append( p[3] )
  p[0] = p[1]

def p_expression_list_B( p ) :
  'expression_list : expression'
  p[0] = [ p[1] ]

# List of statements separated by semicolons
def p_statement_list_A( p ) :
  'statement_list : statement_list SEMICOLON statement'
  p[1].append( p[3] )
  p[0] = p[1]

def p_statement_list_B( p ) :
  'statement_list : statement'
  p[0] = [ p[1] ]

#-------------------
# IDENTIFIER ...

def p_identifier( p ) :
  'identifier : ID'
  p[0] = Expression_Identifier( p.lineno( 1 ), p[1] )

#-------------------
# EXPRESSIONS ...

# Binary operator expression
def p_expression_binop( p ) :
  '''expression : expression PLUS     expression
                | expression MINUS    expression
                | expression MULTIPLY expression
                | expression DIVIDE   expression
                | expression MODULUS  expression
                | expression EXPONENTIATION expression
                | expression EQ       expression
                | expression NE       expression
                | expression LT       expression
                | expression LE       expression
                | expression GT       expression
                | expression GE       expression
                | expression AND      expression
                | expression OR       expression
                | identifier ASSIGN   expression'''
  p[0] = Expression_BinaryOp( p.lineno( 2 ), p[2], p[1], p[3] )

# Unary operator expression
def p_expression_unop( p ) :
  '''expression : expression FACTORIAL
                | MINUS expression %prec UMINUS
                | PLUS  expression %prec UPLUS'''
  if isinstance( p[1], str ) :
    # It's a prefix operator
    p[0] = Expression_UnaryOp( p.lineno( 1 ), p[1], p[2] )

  else :
    # It's a postfix operator
    p[0] = Expression_UnaryOp( p.lineno( 2 ), p[2], p[1] )

# Parenthesized expression
def p_expression_group( p ) :
  'expression : LPAREN expression RPAREN'
  p[0] = p[2]

# Integer literal
def p_expression_int_literal( p ) :
  'expression : INT_LITERAL'
  p[0] = Expression_Literal( p.lineno( 1 ), Type( p.lineno( 1 ), 'int' ), p[1] )

# Real literal
def p_expression_real_literal( p ) :
  'expression : REAL_LITERAL'
  p[0] = Expression_Literal( p.lineno( 1 ), Type( p.lineno( 1 ), 'real' ), p[1] )

# String literal
# TODO: Put p_expression_string_literal( p ) here.
#       Use 'string' as the name of the type. (Look at the
#       INT_LITERAL and REAL_LITERAL cases for examples of what
#       this should look like.
def p_expression_string_literal( p ) :
  'expression : STRING_LITERAL'
  p[0] = Expression_Literal( p.lineno( 1 ), Type( p.lineno( 1 ), 'string' ), p[1] )
  # Name
def p_expression_id( p ) :
  'expression : identifier'
  p[0] = p[1]

#-------------------
# The 'empty' value.  It's possible to just have an empty RHS
# in a production, but having the non-terminal 'epsilon' makes
# it much more obvious that the empty string is being parsed.
def p_epsilon( p ) :
  'epsilon :'
  p[0] = None

#-------------------
# Gets called if an unexpected token (or the EOF) is seen during
# a parse.  We throw an exception
def p_error( p ) :
  msg = 'Syntax error at '
  if p is None :
    msg += 'EOF.'

  else :
    # Go through elaborate shennanigans to determine the column
    # at which the parse error occurred.
    lineStart = p.lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
    column = p.lexpos - lineStart + 1

    msg += f'token "{p.value}", line {p.lineno}, column {column}'

  raise SyntacticError( msg )

#---------#---------#---------#---------#---------#--------#
def _main( inputFileName ) :
  debug = True
  logging.basicConfig(
    level = logging.DEBUG,
    filename = 'parselog.txt',
    filemode = 'w',
    format = '%(filename)10s:%(lineno)4d:%(message)s'
  )

  log = logging.getLogger()

  begin = time()

  fileName  = str( Path( inputFileName ).name )
  parseFile = str( Path( inputFileName ).with_suffix( '.parse' ) )

  print( f'* Reading source file {inputFileName!r} ...' )

  try :
    strt = time()
    with open( inputFileName, 'r' ) as fp :
      data = fp.read()

    print( f'    Read succeeded.  ({time()-strt:.3f}s)\n* Beginning parse ...' )

    strt    = time()
    lexer   = ply.lex.lex( debug = debug, debuglog = log )
    parser  = ply.yacc.yacc( debug = debug, debuglog = log )
    program = parser.parse( data, tracking = True, debug = log )

    print( f'    Parse succeeded.  ({time()-strt:.3f}s)\n* Beginning parse dump to {parseFile!r} ...' )

    strt = time()
    with open( parseFile, 'w' ) as fp :
      program.dump( fp = fp )

    print( f'    Parse dumped.  ({time()-strt:.3f}s)' )

    total = time() - begin
    print( f'# Total time {total:.3f}s.\n#----------')

  except FileNotFoundError as e :
    print( f'File {inputFileName!r} not found.' )
    sys.exit( 1 )

  except LexicalError as e :
    print( 'Exception detected during lexical analysis.' )
    print( e )
    #traceback.print_exc()
    sys.exit( 1 )

  except SyntacticError as e :
    print( 'Exception detected during syntactic analysis.' )
    print( e )
    #traceback.print_exc()
    sys.exit( 1 )

  except :
    print( '*** (Unknown) exception detected during parse/result dump.' )
    traceback.print_exc()
    sys.exit( 1 )

#---------#---------#---------#
if __name__ == '__main__' :
  if len( sys.argv ) > 1 :
    _main( sys.argv[ 1 ] )

  else :
    print( 'Input file name required.' )

#---------#---------#---------#---------#---------#--------#
