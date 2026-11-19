from typing import Dict, List, Optional, Any
from .ast_nodes import (
    ProgramNode, FunctionNode, ParamNode, CompoundStmtNode, StmtNode,
    VarDeclNode, AssignStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode,
    ReturnStmtNode, ExprStmtNode, ExprNode, BinOpNode, UnOpNode, LiteralNode,
    IdentifierNode, FuncCallNode, ArrayAccessNode
)

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, str] = {} # name -> type
        self.parent = parent

    def define(self, name: str, symbol_type: str) -> bool:
        if name in self.symbols:
            return False # Redefinition in same scope
        self.symbols[name] = symbol_type
        return True

    def lookup(self, name: str) -> Optional[str]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.globals = SymbolTable()
        # Track function signatures: name -> (return_type, [param_types])
        self.functions: Dict[str, tuple] = {}
        self.current_function: Optional[FunctionNode] = None

    def error(self, node: Any, message: str, line: int = 1, col: int = 1):
        self.errors.append({
            "line": line,
            "column": col,
            "type": "Semantic Error",
            "message": message
        })

    def analyze(self, program: ProgramNode):
        # First pass: collect function signatures
        for func in program.functions:
            param_types = [p.type_str for p in func.params]
            if func.name in self.functions:
                self.error(func, f"Redefinition of function '{func.name}'")
            self.functions[func.name] = (func.return_type, param_types)
            self.globals.define(func.name, f"function_{func.return_type}")

        # Second pass: check function bodies
        for func in program.functions:
            self.current_function = func
            func_scope = SymbolTable(parent=self.globals)
            for param in func.params:
                func_scope.define(param.name, param.type_str)
            self.analyze_statement(func.body, func_scope)
            
    def analyze_statement(self, stmt: StmtNode, scope: SymbolTable):
        if isinstance(stmt, CompoundStmtNode):
            inner_scope = SymbolTable(parent=scope)
            for s in stmt.statements:
                self.analyze_statement(s, inner_scope)
                
        elif isinstance(stmt, VarDeclNode):
            if not scope.define(stmt.name, stmt.type_str):
                self.error(stmt, f"Redefinition of variable '{stmt.name}'")
            if stmt.init_expr:
                init_type = self.analyze_expression(stmt.init_expr, scope)
                if init_type and init_type != stmt.type_str:
                    # Allow float/int conversion but warn/check
                    pass
                    
        elif isinstance(stmt, AssignStmtNode):
            var_type = scope.lookup(stmt.name)
            if not var_type:
                self.error(stmt, f"Undeclared identifier '{stmt.name}'")
            if stmt.index_expr:
                idx_type = self.analyze_expression(stmt.index_expr, scope)
                if idx_type != "int":
                    self.error(stmt, f"Array index must be integer, found '{idx_type}'")
            expr_type = self.analyze_expression(stmt.expr, scope)
            
        elif isinstance(stmt, IfStmtNode):
            cond_type = self.analyze_expression(stmt.cond, scope)
            self.analyze_statement(stmt.then_branch, scope)
            if stmt.else_branch:
                self.analyze_statement(stmt.else_branch, scope)
                
        elif isinstance(stmt, WhileStmtNode):
            cond_type = self.analyze_expression(stmt.cond, scope)
            self.analyze_statement(stmt.body, scope)
            
        elif isinstance(stmt, ForStmtNode):
            for_scope = SymbolTable(parent=scope)
            if stmt.init:
                self.analyze_statement(stmt.init, for_scope)
            if stmt.cond:
                self.analyze_expression(stmt.cond, for_scope)
            if stmt.post:
                self.analyze_statement(stmt.post, for_scope)
            self.analyze_statement(stmt.body, for_scope)
            
        elif isinstance(stmt, ReturnStmtNode):
            if stmt.expr:
                ret_type = self.analyze_expression(stmt.expr, scope)
                if self.current_function and ret_type != self.current_function.return_type:
                    self.error(stmt, f"Function '{self.current_function.name}' returns '{self.current_function.return_type}' but returns '{ret_type}' here.")
            else:
                if self.current_function and self.current_function.return_type != "void":
                    self.error(stmt, f"Function '{self.current_function.name}' expects a return value of type '{self.current_function.return_type}'")
                    
        elif isinstance(stmt, ExprStmtNode):
            self.analyze_expression(stmt.expr, scope)

    def analyze_expression(self, expr: ExprNode, scope: SymbolTable) -> Optional[str]:
        if isinstance(expr, LiteralNode):
            return expr.val_type
            
        elif isinstance(expr, IdentifierNode):
            var_type = scope.lookup(expr.name)
            if not var_type:
                self.error(expr, f"Undeclared identifier '{expr.name}'")
                return "int" # fallback
            return var_type
            
        elif isinstance(expr, ArrayAccessNode):
            var_type = scope.lookup(expr.name)
            if not var_type:
                self.error(expr, f"Undeclared array '{expr.name}'")
                return "int"
            idx_type = self.analyze_expression(expr.index, scope)
            if idx_type != "int":
                self.error(expr, f"Array index must be integer, found '{idx_type}'")
            return var_type # assuming 1D arrays match base type
            
        elif isinstance(expr, BinOpNode):
            l_type = self.analyze_expression(expr.left, scope)
            r_type = self.analyze_expression(expr.right, scope)
            if l_type == "float" or r_type == "float":
                return "float"
            return "int"
            
        elif isinstance(expr, UnOpNode):
            return self.analyze_expression(expr.expr, scope)
            
        elif isinstance(expr, FuncCallNode):
            if expr.name not in self.functions:
                self.error(expr, f"Call to undeclared function '{expr.name}'")
                return "int"
            ret_type, param_types = self.functions[expr.name]
            if len(expr.args) != len(param_types):
                self.error(expr, f"Function '{expr.name}' expects {len(param_types)} arguments, got {len(expr.args)}")
            else:
                for i, arg in enumerate(expr.args):
                    arg_type = self.analyze_expression(arg, scope)
                    if arg_type != param_types[i]:
                        # Warning / implicit promotion
                        pass
            return ret_type
            
        return "int"
