from typing import List, Optional, Union, Dict, Any

class ASTNode:
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

class ProgramNode(ASTNode):
    def __init__(self, functions: List['FunctionNode']):
        self.functions = functions
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "functions": [f.to_dict() for f in self.functions]
        }

class FunctionNode(ASTNode):
    def __init__(self, return_type: str, name: str, params: List['ParamNode'], body: 'CompoundStmtNode'):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Function",
            "return_type": self.return_type,
            "name": self.name,
            "params": [p.to_dict() for p in self.params],
            "body": self.body.to_dict()
        }

class ParamNode(ASTNode):
    def __init__(self, type_str: str, name: str):
        self.type_str = type_str
        self.name = name
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Parameter",
            "var_type": self.type_str,
            "name": self.name
        }

# Statements
class StmtNode(ASTNode):
    pass

class CompoundStmtNode(StmtNode):
    def __init__(self, statements: List[StmtNode]):
        self.statements = statements
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CompoundStatement",
            "statements": [s.to_dict() for s in self.statements]
        }

class VarDeclNode(StmtNode):
    def __init__(self, type_str: str, name: str, init_expr: Optional['ExprNode'] = None):
        self.type_str = type_str
        self.name = name
        self.init_expr = init_expr
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "VariableDeclaration",
            "var_type": self.type_str,
            "name": self.name,
            "init": self.init_expr.to_dict() if self.init_expr else None
        }

class AssignStmtNode(StmtNode):
    def __init__(self, name: str, expr: 'ExprNode', index_expr: Optional['ExprNode'] = None):
        self.name = name
        self.expr = expr
        self.index_expr = index_expr
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Assignment",
            "name": self.name,
            "index": self.index_expr.to_dict() if self.index_expr else None,
            "expr": self.expr.to_dict()
        }

class IfStmtNode(StmtNode):
    def __init__(self, cond: 'ExprNode', then_branch: StmtNode, else_branch: Optional[StmtNode] = None):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "IfStatement",
            "condition": self.cond.to_dict(),
            "then": self.then_branch.to_dict(),
            "else": self.else_branch.to_dict() if self.else_branch else None
        }

class WhileStmtNode(StmtNode):
    def __init__(self, cond: 'ExprNode', body: StmtNode):
        self.cond = cond
        self.body = body
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WhileStatement",
            "condition": self.cond.to_dict(),
            "body": self.body.to_dict()
        }

class ForStmtNode(StmtNode):
    def __init__(self, init: Optional[StmtNode], cond: Optional['ExprNode'], post: Optional[StmtNode], body: StmtNode):
        self.init = init
        self.cond = cond
        self.post = post
        self.body = body
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ForStatement",
            "init": self.init.to_dict() if self.init else None,
            "condition": self.cond.to_dict() if self.cond else None,
            "post": self.post.to_dict() if self.post else None,
            "body": self.body.to_dict()
        }

class ReturnStmtNode(StmtNode):
    def __init__(self, expr: Optional['ExprNode'] = None):
        self.expr = expr
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ReturnStatement",
            "expr": self.expr.to_dict() if self.expr else None
        }

class ExprStmtNode(StmtNode):
    def __init__(self, expr: 'ExprNode'):
        self.expr = expr
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ExpressionStatement",
            "expr": self.expr.to_dict()
        }

# Expressions
class ExprNode(ASTNode):
    pass

class BinOpNode(ExprNode):
    def __init__(self, op: str, left: ExprNode, right: ExprNode):
        self.op = op
        self.left = left
        self.right = right
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOperation",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

class UnOpNode(ExprNode):
    def __init__(self, op: str, expr: ExprNode):
        self.op = op
        self.expr = expr
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOperation",
            "op": self.op,
            "expr": self.expr.to_dict()
        }

class LiteralNode(ExprNode):
    def __init__(self, val_type: str, value: str):
        self.val_type = val_type
        self.value = value
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Literal",
            "val_type": self.val_type,
            "value": self.value
        }

class IdentifierNode(ExprNode):
    def __init__(self, name: str):
        self.name = name
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Identifier",
            "name": self.name
        }

class ArrayAccessNode(ExprNode):
    def __init__(self, name: str, index: ExprNode):
        self.name = name
        self.index = index
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ArrayAccess",
            "name": self.name,
            "index": self.index.to_dict()
        }

class FuncCallNode(ExprNode):
    def __init__(self, name: str, args: List[ExprNode]):
        self.name = name
        self.args = args
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "FunctionCall",
            "name": self.name,
            "args": [a.to_dict() for a in self.args]
        }
