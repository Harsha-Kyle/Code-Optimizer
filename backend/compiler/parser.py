from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import (
    ProgramNode, FunctionNode, ParamNode, CompoundStmtNode, StmtNode,
    VarDeclNode, AssignStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode,
    ReturnStmtNode, ExprStmtNode, ExprNode, BinOpNode, UnOpNode, LiteralNode,
    IdentifierNode, FuncCallNode, ArrayAccessNode
)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current(self) -> Token:
        return self.tokens[self.position]

    def peek(self, offset: int = 1) -> Token:
        if self.position + offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position + offset]

    def is_at_end(self) -> bool:
        return self.current().type == TokenType.EOF

    def advance(self) -> Token:
        val = self.current()
        if not self.is_at_end():
            self.position += 1
        return val

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.current().type == type

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        tok = self.current()
        self.error(tok, f"Expected {type.value or type.name}. {message}")
        # Return a dummy error token to continue parsing
        return Token(TokenType.ERROR, tok.value, tok.line, tok.column)

    def error(self, token: Token, message: str):
        self.errors.append({
            "line": token.line,
            "column": token.column,
            "type": "Syntax Error",
            "message": message
        })

    def parse(self) -> Optional[ProgramNode]:
        functions = []
        while not self.is_at_end():
            func = self.parse_function()
            if func:
                functions.append(func)
            else:
                # Synchronize parse state to avoid infinite loops on syntax errors
                self.advance()
        return ProgramNode(functions)

    def parse_function(self) -> Optional[FunctionNode]:
        # Return Type
        if not self.check(TokenType.INT) and not self.check(TokenType.FLOAT) and not self.check(TokenType.CHAR) and not self.check(TokenType.VOID):
            tok = self.current()
            self.error(tok, f"Invalid function return type '{tok.value}'")
            return None
        ret_type = self.advance().value

        # Name
        name_tok = self.consume(TokenType.IDENT, "Expected function name.")
        name = name_tok.value

        # Parameters
        self.consume(TokenType.LPAREN, "Expected '(' after function name.")
        params = []
        if not self.check(TokenType.RPAREN):
            # Check if single 'void' parameter: func(void)
            if self.check(TokenType.VOID) and self.peek().type == TokenType.RPAREN:
                self.advance() # consume 'void'
            else:
                while True:
                    p_type = self.advance() # int, float, char
                    if p_type.type not in [TokenType.INT, TokenType.FLOAT, TokenType.CHAR]:
                        self.error(p_type, f"Invalid parameter type '{p_type.value}'")
                    p_name = self.consume(TokenType.IDENT, "Expected parameter name.")
                    params.append(ParamNode(p_type.value, p_name.value))
                    if not self.match(TokenType.COMMA):
                        break
        self.consume(TokenType.RPAREN, "Expected ')' after parameter list.")

        # Body
        body = self.parse_compound_stmt()
        
        return FunctionNode(ret_type, name, params, body)

    def parse_compound_stmt(self) -> CompoundStmtNode:
        self.consume(TokenType.LBRACE, "Expected '{' to start function body.")
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.consume(TokenType.RBRACE, "Expected '}' to close function body.")
        return CompoundStmtNode(statements)

    def parse_statement(self) -> Optional[StmtNode]:
        if self.match(TokenType.LBRACE):
            # Compound stmt
            statements = []
            while not self.check(TokenType.RBRACE) and not self.is_at_end():
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.consume(TokenType.RBRACE, "Expected '}' to close block.")
            return CompoundStmtNode(statements)
            
        if self.check(TokenType.INT) or self.check(TokenType.FLOAT) or self.check(TokenType.CHAR):
            return self.parse_var_declaration()
            
        if self.match(TokenType.IF):
            return self.parse_if_stmt()
            
        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()
            
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()
            
        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()
            
        # Assignment or Expression Statement
        return self.parse_expression_stmt()

    def parse_var_declaration(self) -> VarDeclNode:
        type_tok = self.advance()
        type_str = type_tok.value
        name_tok = self.consume(TokenType.IDENT, "Expected variable name.")
        
        init_expr = None
        if self.match(TokenType.ASSIGN):
            init_expr = self.parse_expression()
            
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return VarDeclNode(type_str, name_tok.value, init_expr)

    def parse_if_stmt(self) -> IfStmtNode:
        self.consume(TokenType.LPAREN, "Expected '(' before condition.")
        cond = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition.")
        
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.parse_statement()
            
        return IfStmtNode(cond, then_branch, else_branch)

    def parse_while_stmt(self) -> WhileStmtNode:
        self.consume(TokenType.LPAREN, "Expected '(' before condition.")
        cond = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition.")
        body = self.parse_statement()
        return WhileStmtNode(cond, body)

    def parse_for_stmt(self) -> ForStmtNode:
        self.consume(TokenType.LPAREN, "Expected '(' after 'for'.")
        
        init = None
        if not self.match(TokenType.SEMICOLON):
            if self.check(TokenType.INT) or self.check(TokenType.FLOAT) or self.check(TokenType.CHAR):
                init = self.parse_var_declaration()
            else:
                init = self.parse_expression_stmt() # handles semicolon automatically inside if it's assign

        cond = None
        if not self.check(TokenType.SEMICOLON):
            cond = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' in for-loop condition.")
        
        post = None
        if not self.check(TokenType.RPAREN):
            # Parse post-expression as a statement/expr
            expr = self.parse_expression()
            if isinstance(expr, BinOpNode) and expr.op == '=':
                post = AssignStmtNode(expr.left.name, expr.right)
            elif isinstance(expr, IdentifierNode):
                # t++ etc simulated
                post = ExprStmtNode(expr)
            else:
                post = ExprStmtNode(expr)
                
        self.consume(TokenType.RPAREN, "Expected ')' after for-loop controls.")
        body = self.parse_statement()
        return ForStmtNode(init, cond, post, body)

    def parse_return_stmt(self) -> ReturnStmtNode:
        expr = None
        if not self.check(TokenType.SEMICOLON):
            expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement.")
        return ReturnStmtNode(expr)

    def parse_expression_stmt(self) -> StmtNode:
        # Check if it looks like an assignment: `ident = expr` or `ident[idx] = expr`
        if self.check(TokenType.IDENT) and self.peek().type in [TokenType.ASSIGN, TokenType.LBRACKET]:
            name_tok = self.advance()
            name = name_tok.value
            
            index_expr = None
            if self.match(TokenType.LBRACKET):
                index_expr = self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after array index.")
                
            self.consume(TokenType.ASSIGN, "Expected '=' in assignment.")
            expr = self.parse_expression()
            self.consume(TokenType.SEMICOLON, "Expected ';' after assignment statement.")
            return AssignStmtNode(name, expr, index_expr)
            
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return ExprStmtNode(expr)

    def parse_expression(self) -> ExprNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> ExprNode:
        expr = self.parse_logical_and()
        while self.match(TokenType.OR):
            op = "||"
            right = self.parse_logical_and()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_logical_and(self) -> ExprNode:
        expr = self.parse_bitwise_or()
        while self.match(TokenType.AND):
            op = "&&"
            right = self.parse_bitwise_or()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_bitwise_or(self) -> ExprNode:
        expr = self.parse_bitwise_xor()
        while self.match(TokenType.BAR):
            op = "|"
            right = self.parse_bitwise_xor()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_bitwise_xor(self) -> ExprNode:
        expr = self.parse_bitwise_and()
        while self.match(TokenType.CARET):
            op = "^"
            right = self.parse_bitwise_and()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_bitwise_and(self) -> ExprNode:
        expr = self.parse_equality()
        while self.match(TokenType.AMP):
            op = "&"
            right = self.parse_equality()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_equality(self) -> ExprNode:
        expr = self.parse_relational()
        while self.match(TokenType.EQ, TokenType.NE):
            op = "==" if self.tokens[self.position - 1].type == TokenType.EQ else "!="
            right = self.parse_relational()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_relational(self) -> ExprNode:
        expr = self.parse_shift()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self.tokens[self.position - 1].value
            right = self.parse_shift()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_shift(self) -> ExprNode:
        expr = self.parse_additive()
        while self.match(TokenType.LSHIFT, TokenType.RSHIFT):
            op = self.tokens[self.position - 1].value
            right = self.parse_additive()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_additive(self) -> ExprNode:
        expr = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.tokens[self.position - 1].value
            right = self.parse_multiplicative()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_multiplicative(self) -> ExprNode:
        expr = self.parse_unary()
        while self.match(TokenType.MULT, TokenType.DIV, TokenType.MOD):
            op = self.tokens[self.position - 1].value
            right = self.parse_unary()
            expr = BinOpNode(op, expr, right)
        return expr

    def parse_unary(self) -> ExprNode:
        if self.match(TokenType.MINUS, TokenType.NOT, TokenType.TILDE):
            op = self.tokens[self.position - 1].value
            right = self.parse_unary()
            return UnOpNode(op, right)
        return self.parse_primary()

    def parse_primary(self) -> ExprNode:
        if self.match(TokenType.INT_LIT):
            return LiteralNode("int", self.tokens[self.position - 1].value)
        if self.match(TokenType.FLOAT_LIT):
            return LiteralNode("float", self.tokens[self.position - 1].value)
        if self.match(TokenType.CHAR_LIT):
            return LiteralNode("char", self.tokens[self.position - 1].value)
            
        if self.match(TokenType.IDENT):
            name = self.tokens[self.position - 1].value
            
            # Function Call: name(...)
            if self.match(TokenType.LPAREN):
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA):
                            break
                self.consume(TokenType.RPAREN, "Expected ')' after arguments.")
                return FuncCallNode(name, args)
                
            # Array Access: name[index]
            if self.match(TokenType.LBRACKET):
                index = self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after array index.")
                return ArrayAccessNode(name, index)
                
            return IdentifierNode(name)
            
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expr
            
        tok = self.current()
        self.error(tok, f"Expected expression, found: '{tok.value}'")
        self.advance() # recovery
        return LiteralNode("int", "0")
