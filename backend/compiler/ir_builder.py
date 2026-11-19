from typing import List, Dict, Any, Optional, Tuple
from .ast_nodes import (
    ProgramNode, FunctionNode, ParamNode, CompoundStmtNode, StmtNode,
    VarDeclNode, AssignStmtNode, IfStmtNode, WhileStmtNode, ForStmtNode,
    ReturnStmtNode, ExprStmtNode, ExprNode, BinOpNode, UnOpNode, LiteralNode,
    IdentifierNode, FuncCallNode, ArrayAccessNode
)

class Instruction:
    def __init__(self, op: str, arg1: str, arg2: Optional[str] = None, result: Optional[str] = None):
        self.op = op          # e.g., '+', '-', '=', 'LABEL', 'JUMP', 'IF', 'RETURN', 'PARAM', 'CALL'
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self) -> str:
        if self.op == 'LABEL':
            return f"{self.arg1}:"
        elif self.op == 'JUMP':
            return f"goto {self.arg1}"
        elif self.op == 'IF':
            return f"if {self.arg1} goto {self.arg2} else goto {self.result}"
        elif self.op == '=':
            return f"{self.result} = {self.arg1}"
        elif self.op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '&', '|', '^', '<<', '>>']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op in ['~', '!', 'NEG']:
            return f"{self.result} = {self.op}{self.arg1}"
        elif self.op == 'RETURN':
            return f"return {self.arg1}" if self.arg1 else "return"
        elif self.op == 'PARAM':
            return f"param {self.arg1}"
        elif self.op == 'CALL':
            if self.result:
                return f"{self.result} = call {self.arg1}, {self.arg2}"
            return f"call {self.arg1}, {self.arg2}"
        elif self.op == 'LOAD':
            return f"{self.result} = MEM[{self.arg1}]"
        elif self.op == 'STORE':
            return f"MEM[{self.arg1}] = {self.result}"
        return f"{self.result} = {self.op} {self.arg1} {self.arg2}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "arg1": self.arg1,
            "arg2": self.arg2,
            "result": self.result,
            "string": str(self)
        }

class IRBuilder:
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function: Optional[str] = None
        self.function_ir: Dict[str, List[Instruction]] = {}

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instruction: Instruction):
        self.instructions.append(instruction)

    def build(self, program: ProgramNode) -> Dict[str, List[Instruction]]:
        self.function_ir = {}
        for func in program.functions:
            self.instructions = []
            self.current_function = func.name
            
            # Emit function label and define local params
            self.emit(Instruction('LABEL', func.name))
            
            # Lower the body compound statement
            self.build_statement(func.body)
            
            # Fallback return void if not present
            if not self.instructions or self.instructions[-1].op != 'RETURN':
                self.emit(Instruction('RETURN', ""))
                
            self.function_ir[func.name] = self.instructions
            
        return self.function_ir

    def build_statement(self, stmt: StmtNode):
        if isinstance(stmt, CompoundStmtNode):
            for s in stmt.statements:
                self.build_statement(s)
                
        elif isinstance(stmt, VarDeclNode):
            if stmt.init_expr:
                expr_temp = self.build_expression(stmt.init_expr)
                self.emit(Instruction('=', expr_temp, result=stmt.name))
                
        elif isinstance(stmt, AssignStmtNode):
            expr_temp = self.build_expression(stmt.expr)
            if stmt.index_expr:
                # Array assignment MEM[name + offset] = expr
                idx_temp = self.build_expression(stmt.index_expr)
                # For Cortex-M, word access size is 4 bytes. Scaled offset:
                scaled = self.new_temp()
                self.emit(Instruction('*', idx_temp, "4", scaled))
                addr = self.new_temp()
                self.emit(Instruction('+', stmt.name, scaled, addr))
                self.emit(Instruction('STORE', addr, result=expr_temp))
            else:
                self.emit(Instruction('=', expr_temp, result=stmt.name))
                
        elif isinstance(stmt, IfStmtNode):
            cond_temp = self.build_expression(stmt.cond)
            label_then = self.new_label()
            label_else = self.new_label()
            label_end = self.new_label()
            
            self.emit(Instruction('IF', cond_temp, label_then, label_else))
            
            # Then branch
            self.emit(Instruction('LABEL', label_then))
            self.build_statement(stmt.then_branch)
            # Avoid emitting jumps if we already returned inside the block
            self.emit(Instruction('JUMP', label_end))
            
            # Else branch
            self.emit(Instruction('LABEL', label_else))
            if stmt.else_branch:
                self.build_statement(stmt.else_branch)
            self.emit(Instruction('JUMP', label_end))
            
            self.emit(Instruction('LABEL', label_end))
            
        elif isinstance(stmt, WhileStmtNode):
            label_start = self.new_label()
            label_body = self.new_label()
            label_end = self.new_label()
            
            self.emit(Instruction('LABEL', label_start))
            cond_temp = self.build_expression(stmt.cond)
            self.emit(Instruction('IF', cond_temp, label_body, label_end))
            
            self.emit(Instruction('LABEL', label_body))
            self.build_statement(stmt.body)
            self.emit(Instruction('JUMP', label_start))
            
            self.emit(Instruction('LABEL', label_end))

        elif isinstance(stmt, ForStmtNode):
            label_start = self.new_label()
            label_body = self.new_label()
            label_end = self.new_label()
            
            if stmt.init:
                self.build_statement(stmt.init)
                
            self.emit(Instruction('LABEL', label_start))
            
            if stmt.cond:
                cond_temp = self.build_expression(stmt.cond)
                self.emit(Instruction('IF', cond_temp, label_body, label_end))
            else:
                self.emit(Instruction('JUMP', label_body))
                
            self.emit(Instruction('LABEL', label_body))
            self.build_statement(stmt.body)
            
            if stmt.post:
                self.build_statement(stmt.post)
                
            self.emit(Instruction('JUMP', label_start))
            self.emit(Instruction('LABEL', label_end))
            
        elif isinstance(stmt, ReturnStmtNode):
            ret_val = ""
            if stmt.expr:
                ret_val = self.build_expression(stmt.expr)
            self.emit(Instruction('RETURN', ret_val))
            
        elif isinstance(stmt, ExprStmtNode):
            self.build_expression(stmt.expr)

    def build_expression(self, expr: ExprNode) -> str:
        if isinstance(expr, LiteralNode):
            temp = self.new_temp()
            self.emit(Instruction('=', expr.value, result=temp))
            return temp
            
        elif isinstance(expr, IdentifierNode):
            return expr.name
            
        elif isinstance(expr, ArrayAccessNode):
            idx_temp = self.build_expression(expr.index)
            scaled = self.new_temp()
            self.emit(Instruction('*', idx_temp, "4", scaled))
            addr = self.new_temp()
            self.emit(Instruction('+', expr.name, scaled, addr))
            res = self.new_temp()
            self.emit(Instruction('LOAD', addr, result=res))
            return res
            
        elif isinstance(expr, BinOpNode):
            l_temp = self.build_expression(expr.left)
            r_temp = self.build_expression(expr.right)
            res = self.new_temp()
            self.emit(Instruction(expr.op, l_temp, r_temp, result=res))
            return res
            
        elif isinstance(expr, UnOpNode):
            val_temp = self.build_expression(expr.expr)
            res = self.new_temp()
            # Map standard operations
            op_mapped = 'NEG' if expr.op == '-' else expr.op
            self.emit(Instruction(op_mapped, val_temp, result=res))
            return res
            
        elif isinstance(expr, FuncCallNode):
            arg_temps = []
            for arg in expr.args:
                arg_temps.append(self.build_expression(arg))
            
            for temp in arg_temps:
                self.emit(Instruction('PARAM', temp))
                
            res = self.new_temp()
            self.emit(Instruction('CALL', expr.name, str(len(arg_temps)), result=res))
            return res
            
        return "0"
