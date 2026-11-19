import re
from typing import List
from .tokens import TokenType, Token

KEYWORDS = {
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "char": TokenType.CHAR,
    "void": TokenType.VOID,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    # stdint types
    "uint8_t": TokenType.INT,
    "uint16_t": TokenType.INT,
    "uint32_t": TokenType.INT,
    "uint64_t": TokenType.INT,
    "int8_t": TokenType.INT,
    "int16_t": TokenType.INT,
    "int32_t": TokenType.INT,
    "int64_t": TokenType.INT,
    "unsigned": TokenType.INT,
    "short": TokenType.INT,
    "long": TokenType.INT,
}

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source)
        self.errors = []
        self.macros = {}

    def peek(self, offset: int = 0) -> str:
        if self.position + offset >= self.length:
            return ""
        return self.source[self.position + offset]

    def advance(self) -> str:
        if self.position >= self.length:
            return ""
        char = self.source[self.position]
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def error(self, message: str):
        self.errors.append({
            "line": self.line,
            "column": self.column,
            "type": "Lexical Error",
            "message": message
        })

    def skip_whitespace_and_comments(self):
        while self.position < self.length:
            char = self.peek()
            if char.isspace():
                self.advance()
            # Double slash comments
            elif char == '/' and self.peek(1) == '/':
                self.advance() # slash
                self.advance() # slash
                while self.position < self.length and self.peek() != '\n':
                    self.advance()
            # Multi-line comments
            elif char == '/' and self.peek(1) == '*':
                start_line = self.line
                start_col = self.column
                self.advance() # slash
                self.advance() # star
                closed = False
                while self.position < self.length:
                    if self.peek() == '*' and self.peek(1) == '/':
                        self.advance() # star
                        self.advance() # slash
                        closed = True
                        break
                    self.advance()
                if not closed:
                    self.error(f"Unterminated block comment starting at line {start_line}, col {start_col}")
            else:
                break

    def read_number(self) -> Token:
        start_col = self.column
        num_str = ""
        is_float = False
        
        while self.position < self.length:
            char = self.peek()
            if char.isdigit():
                num_str += self.advance()
            elif char == '.' and not is_float and self.peek(1).isdigit():
                is_float = True
                num_str += self.advance() # dot
            else:
                break
                
        token_type = TokenType.FLOAT_LIT if is_float else TokenType.INT_LIT
        return Token(token_type, num_str, self.line, start_col)

    def read_identifier_or_keyword(self) -> Token:
        start_col = self.column
        ident_str = ""
        
        while self.position < self.length:
            char = self.peek()
            if char.isalnum() or char == '_':
                ident_str += self.advance()
            else:
                break
                
        token_type = KEYWORDS.get(ident_str, TokenType.IDENT)
        return Token(token_type, ident_str, self.line, start_col)

    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.position < self.length:
            self.skip_whitespace_and_comments()
            if self.position >= self.length:
                break
                
            char = self.peek()
            start_col = self.column
            
            # Preprocessor directives: handle #define macro substitution or skip #include etc.
            if char == '#':
                self.advance() # consume '#'
                directive = ""
                while self.position < self.length and self.peek().isalpha():
                    directive += self.advance()
                
                if directive == "define":
                    self.skip_whitespace_and_comments()
                    macro_name = ""
                    while self.position < self.length and (self.peek().isalnum() or self.peek() == '_'):
                        macro_name += self.advance()
                    
                    # Skip spaces after macro_name
                    while self.position < self.length and self.peek() in ' \t':
                        self.advance()
                        
                    # Read the rest of line as macro expansion expression
                    macro_val = ""
                    while self.position < self.length and self.peek() != '\n':
                        macro_val += self.advance()
                    
                    if macro_name and macro_val.strip():
                        # Sub-tokenize macro_val
                        sub_lexer = Lexer(macro_val.strip())
                        sub_tokens = sub_lexer.tokenize()
                        # Exclude EOF
                        self.macros[macro_name] = [t for t in sub_tokens if t.type != TokenType.EOF]
                else:
                    # Skip rest of preprocessor line (#include etc.)
                    while self.position < self.length and self.peek() != '\n':
                        self.advance()
                continue
            
            # Identifiers and keywords (with #define macro substitution)
            if char.isalpha() or char == '_':
                tok = self.read_identifier_or_keyword()
                if tok.type == TokenType.IDENT and tok.value in self.macros:
                    for mt in self.macros[tok.value]:
                        # Copy macro token with current line and column tracking
                        tokens.append(Token(mt.type, mt.value, tok.line, tok.column))
                else:
                    tokens.append(tok)
                continue
                
            # Numbers (Hexadecimal 0x... or Decimal / Float)
            if char.isdigit():
                if char == '0' and (self.peek(1) == 'x' or self.peek(1) == 'X'):
                    # Hexadecimal literal
                    hex_str = self.advance() + self.advance() # '0x'
                    while self.position < self.length and (self.peek().isdigit() or self.peek().lower() in 'abcdef'):
                        hex_str += self.advance()
                    tokens.append(Token(TokenType.INT_LIT, str(int(hex_str, 16)), self.line, start_col))
                    continue
                tokens.append(self.read_number())
                continue

            # Character Literals
            if char == "'":
                self.advance() # leading quote
                if self.peek() == '\\': # escape
                    val = self.advance() + self.advance()
                else:
                    val = self.advance()
                if self.peek() == "'":
                    self.advance() # trailing quote
                    tokens.append(Token(TokenType.CHAR_LIT, val, self.line, start_col))
                else:
                    self.error("Unterminated character literal")
                    tokens.append(Token(TokenType.ERROR, val, self.line, start_col))
                continue

            # Multi-character Operators (3-char and 2-char)
            three_chars = self.peek() + self.peek(1) + self.peek(2)
            if three_chars in ["<<=", ">>="]:
                self.advance(); self.advance(); self.advance()
                tokens.append(Token(TokenType.ASSIGN, three_chars, self.line, start_col))
                continue

            two_chars = self.peek() + self.peek(1)
            two_char_ops = {
                "==": TokenType.EQ,
                "!=": TokenType.NE,
                "<=": TokenType.LE,
                ">=": TokenType.GE,
                "&&": TokenType.AND,
                "||": TokenType.OR,
                "<<": TokenType.LSHIFT,
                ">>": TokenType.RSHIFT,
                "+=": TokenType.ASSIGN,
                "-=": TokenType.ASSIGN,
                "*=": TokenType.ASSIGN,
                "/=": TokenType.ASSIGN,
                "&=": TokenType.ASSIGN,
                "|=": TokenType.ASSIGN,
                "^=": TokenType.ASSIGN,
            }
            
            if two_chars in two_char_ops:
                val = two_chars
                self.advance()
                self.advance()
                tokens.append(Token(two_char_ops[val], val, self.line, start_col))
                continue
                
            # Single-character Operators/Punctuation
            single_char_ops = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.MULT,
                "/": TokenType.DIV,
                "%": TokenType.MOD,
                "=": TokenType.ASSIGN,
                "<": TokenType.LT,
                ">": TokenType.GT,
                "&": TokenType.AMP,
                "|": TokenType.BAR,
                "^": TokenType.CARET,
                "~": TokenType.TILDE,
                "!": TokenType.NOT,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                ";": TokenType.SEMICOLON,
                ",": TokenType.COMMA,
            }
            
            if char in single_char_ops:
                self.advance()
                tokens.append(Token(single_char_ops[char], char, self.line, start_col))
                continue
                
            # Invalid character
            self.error(f"Unexpected character: {repr(char)}")
            self.advance()
            tokens.append(Token(TokenType.ERROR, char, self.line, start_col))

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens
