from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    # Keywords
    INT = "int"
    FLOAT = "float"
    CHAR = "char"
    VOID = "void"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    
    # Literals & Identifiers
    IDENT = "identifier"
    INT_LIT = "integer_literal"
    FLOAT_LIT = "float_literal"
    CHAR_LIT = "char_literal"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"
    ASSIGN = "="
    
    # Comparisons
    EQ = "=="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    
    # Logical
    AND = "&&"
    OR = "||"
    NOT = "!"
    
    # Bitwise
    AMP = "&"
    BAR = "|"
    CARET = "^"
    LSHIFT = "<<"
    RSHIFT = ">>"
    TILDE = "~"
    
    # Punctuation
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    SEMICOLON = ";"
    COMMA = ","
    
    # Special
    EOF = "EOF"
    ERROR = "ERROR"
    COMMENT = "COMMENT"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def to_dict(self):
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column
        }
