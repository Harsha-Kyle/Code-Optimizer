from typing import List, Dict, Set, Tuple
from .ir_builder import Instruction

class Optimizer:
    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.log: List[Dict[str, str]] = []

    def log_opt(self, opt_name: str, before: str, after: str, reason: str):
        self.log.append({
            "pass": opt_name,
            "before": before,
            "after": after,
            "reason": reason
        })

    def run_all(self, passes_config: Dict[str, bool]) -> List[Instruction]:
        # Run optimizations repeatedly until no more changes occur (converge)
        iter_limit = 5
        changed = True
        current_instrs = self.instructions[:]
        
        for _ in range(iter_limit):
            if not changed:
                break
            changed = False
            
            if passes_config.get("constant_folding", True):
                current_instrs, fold_changed = self.constant_folding(current_instrs)
                changed = changed or fold_changed
                
            if passes_config.get("constant_propagation", True):
                current_instrs, prop_changed = self.constant_propagation(current_instrs)
                changed = changed or prop_changed
                
            if passes_config.get("algebraic", True):
                current_instrs, alg_changed = self.algebraic_simplification(current_instrs)
                changed = changed or alg_changed
                
            if passes_config.get("strength_reduction", True):
                current_instrs, str_changed = self.strength_reduction(current_instrs)
                changed = changed or str_changed
                
            if passes_config.get("cse", True):
                current_instrs, cse_changed = self.cse(current_instrs)
                changed = changed or cse_changed
                
            if passes_config.get("dead_code", True):
                current_instrs, dce_changed = self.dead_code_elimination(current_instrs)
                changed = changed or dce_changed

            if passes_config.get("loop_optimization", True):
                current_instrs, loop_changed = self.loop_invariant_code_motion(current_instrs)
                changed = changed or loop_changed

        return current_instrs

    def constant_folding(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        new_instrs = []
        changed = False
        
        for inst in instrs:
            # Binary operations folding: e.g. t1 = 10 * 20
            if inst.op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '&', '|', '^', '<<', '>>']:
                if inst.arg1.isdigit() and inst.arg2 and inst.arg2.isdigit():
                    val1 = int(inst.arg1)
                    val2 = int(inst.arg2)
                    res_val = None
                    
                    try:
                        if inst.op == '+': res_val = val1 + val2
                        elif inst.op == '-': res_val = val1 - val2
                        elif inst.op == '*': res_val = val1 * val2
                        elif inst.op == '/': res_val = val1 // val2 if val2 != 0 else 0
                        elif inst.op == '%': res_val = val1 % val2 if val2 != 0 else 0
                        elif inst.op == '==': res_val = 1 if val1 == val2 else 0
                        elif inst.op == '!=': res_val = 1 if val1 != val2 else 0
                        elif inst.op == '<': res_val = 1 if val1 < val2 else 0
                        elif inst.op == '>': res_val = 1 if val1 > val2 else 0
                        elif inst.op == '<=': res_val = 1 if val1 <= val2 else 0
                        elif inst.op == '>=': res_val = 1 if val1 >= val2 else 0
                        elif inst.op == '&&': res_val = 1 if val1 and val2 else 0
                        elif inst.op == '||': res_val = 1 if val1 or val2 else 0
                        elif inst.op == '&': res_val = val1 & val2
                        elif inst.op == '|': res_val = val1 | val2
                        elif inst.op == '^': res_val = val1 ^ val2
                        elif inst.op == '<<': res_val = val1 << val2
                        elif inst.op == '>>': res_val = val1 >> val2
                    except Exception:
                        pass
                        
                    if res_val is not None:
                        new_inst = Instruction('=', str(res_val), result=inst.result)
                        self.log_opt("Constant Folding", str(inst), str(new_inst), "Folded constant expression")
                        new_instrs.append(new_inst)
                        changed = True
                        continue
            
            # Unary operations folding: e.g. t1 = -5 or t1 = !0
            if inst.op in ['NEG', '!', '~'] and inst.arg1.isdigit():
                val1 = int(inst.arg1)
                res_val = None
                if inst.op == 'NEG': res_val = -val1
                elif inst.op == '!': res_val = 1 if not val1 else 0
                elif inst.op == '~': res_val = ~val1
                
                if res_val is not None:
                    new_inst = Instruction('=', str(res_val), result=inst.result)
                    self.log_opt("Constant Folding", str(inst), str(new_inst), "Folded unary constant expression")
                    new_instrs.append(new_inst)
                    changed = True
                    continue
                    
            new_instrs.append(inst)
        return new_instrs, changed

    def constant_propagation(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        new_instrs = []
        changed = False
        consts: Dict[str, str] = {} # var -> constant_value_string
        
        for inst in instrs:
            # Check assignments to constants: t1 = 5
            if inst.op == '=' and inst.arg1 and (inst.arg1.isdigit() or (inst.arg1.startswith('-') and inst.arg1[1:].isdigit())):
                consts[inst.result] = inst.arg1
                new_instrs.append(inst)
                continue
                
            # If target variable is redefined to a non-constant, remove it from mapping
            if inst.result and inst.op != '=' and inst.result in consts:
                del consts[inst.result]
                
            # Propagate values
            arg1_new = consts.get(inst.arg1, inst.arg1)
            arg2_new = consts.get(inst.arg2, inst.arg2) if inst.arg2 else inst.arg2
            
            if arg1_new != inst.arg1 or arg2_new != inst.arg2:
                new_inst = Instruction(inst.op, arg1_new, arg2_new, result=inst.result)
                self.log_opt("Constant Propagation", str(inst), str(new_inst), "Propagated known constants")
                new_instrs.append(new_inst)
                changed = True
            else:
                new_instrs.append(inst)
                
        return new_instrs, changed

    def algebraic_simplification(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        new_instrs = []
        changed = False
        
        for inst in instrs:
            # x + 0 -> x
            if inst.op == '+' and (inst.arg1 == '0' or inst.arg2 == '0'):
                non_zero = inst.arg2 if inst.arg1 == '0' else inst.arg1
                new_inst = Instruction('=', non_zero, result=inst.result)
                self.log_opt("Algebraic Simplification", str(inst), str(new_inst), "Simplified x + 0 to x")
                new_instrs.append(new_inst)
                changed = True
                continue
            # x * 1 -> x, x * 0 -> 0
            if inst.op == '*':
                if inst.arg1 == '1' or inst.arg2 == '1':
                    non_one = inst.arg2 if inst.arg1 == '1' else inst.arg1
                    new_inst = Instruction('=', non_one, result=inst.result)
                    self.log_opt("Algebraic Simplification", str(inst), str(new_inst), "Simplified x * 1 to x")
                    new_instrs.append(new_inst)
                    changed = True
                    continue
                if inst.arg1 == '0' or inst.arg2 == '0':
                    new_inst = Instruction('=', '0', result=inst.result)
                    self.log_opt("Algebraic Simplification", str(inst), str(new_inst), "Simplified x * 0 to 0")
                    new_instrs.append(new_inst)
                    changed = True
                    continue
            # x - 0 -> x
            if inst.op == '-' and inst.arg2 == '0':
                new_inst = Instruction('=', inst.arg1, result=inst.result)
                self.log_opt("Algebraic Simplification", str(inst), str(new_inst), "Simplified x - 0 to x")
                new_instrs.append(new_inst)
                changed = True
                continue
                
            new_instrs.append(inst)
        return new_instrs, changed

    def strength_reduction(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        new_instrs = []
        changed = False
        
        for inst in instrs:
            # x * 2 -> x << 1 (or other powers of 2)
            if inst.op == '*':
                for power in [1, 2, 3, 4]:
                    val = 2 ** power
                    if inst.arg1 == str(val) or inst.arg2 == str(val):
                        non_power = inst.arg2 if inst.arg1 == str(val) else inst.arg1
                        new_inst = Instruction('<<', non_power, str(power), result=inst.result)
                        self.log_opt("Strength Reduction", str(inst), str(new_inst), f"Replaced * {val} with << {power}")
                        new_instrs.append(new_inst)
                        changed = True
                        break
                else:
                    new_instrs.append(inst)
                continue
            new_instrs.append(inst)
        return new_instrs, changed

    def cse(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        new_instrs = []
        changed = False
        # Store computed expressions: (op, arg1, arg2) -> temp_var_name
        exprs: Dict[Tuple[str, str, Optional[str]], str] = {}
        
        for inst in instrs:
            # Filter compute binops
            if inst.op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&', '|', '^', '<<', '>>']:
                expr_key = (inst.op, inst.arg1, inst.arg2)
                if expr_key in exprs:
                    existing_temp = exprs[expr_key]
                    new_inst = Instruction('=', existing_temp, result=inst.result)
                    self.log_opt("Common Subexpression Elimination", str(inst), str(new_inst), f"Replaced duplicate calculation with value from {existing_temp}")
                    new_instrs.append(new_inst)
                    changed = True
                else:
                    exprs[expr_key] = inst.result
                    new_instrs.append(inst)
            else:
                # If variables are overwritten, clear expression table keys referencing them
                if inst.result:
                    keys_to_del = [k for k, v in exprs.items() if k[1] == inst.result or k[2] == inst.result or v == inst.result]
                    for k in keys_to_del:
                        del exprs[k]
                new_instrs.append(inst)
                
        return new_instrs, changed

    def dead_code_elimination(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        # Live variables analysis from back to front
        used_vars: Set[str] = set()
        
        # Pre-populate return values and call parameters
        for inst in instrs:
            if inst.op == 'RETURN' and inst.arg1:
                used_vars.add(inst.arg1)
            if inst.op == 'PARAM':
                used_vars.add(inst.arg1)
            if inst.op == 'IF':
                used_vars.add(inst.arg1)
            if inst.op == 'STORE':
                used_vars.add(inst.arg1)
                if inst.result:
                    used_vars.add(inst.result)
                    
        new_instrs = []
        changed = False
        
        # Traverse backwards
        for inst in reversed(instrs):
            # If assignment, check if variable is ever used
            if inst.result and inst.op not in ['STORE', 'CALL', 'LABEL']:
                # Do not eliminate inputs or global output names (non-temporaries might be globals)
                if inst.result.startswith('t') and inst.result not in used_vars:
                    # Eliminate it!
                    self.log_opt("Dead Code Elimination", str(inst), "", f"Removed unused temporary {inst.result}")
                    changed = True
                    continue
                else:
                    used_vars.add(inst.arg1)
                    if inst.arg2:
                        used_vars.add(inst.arg2)
            else:
                if inst.arg1:
                    used_vars.add(inst.arg1)
                if inst.arg2:
                    used_vars.add(inst.arg2)
                    
            new_instrs.append(inst)
            
        new_instrs.reverse()
        return new_instrs, changed

    def loop_invariant_code_motion(self, instrs: List[Instruction]) -> Tuple[List[Instruction], bool]:
        # Basic LICM for simple blocks. Finds loops via jump labels
        new_instrs = []
        changed = False
        
        # Find basic loop regions based on JUMP back to an earlier LABEL
        loop_starts = []
        loop_ends = []
        label_positions = {}
        
        for idx, inst in enumerate(instrs):
            if inst.op == 'LABEL':
                label_positions[inst.arg1] = idx
            elif inst.op == 'JUMP':
                target = inst.arg1
                if target in label_positions: # backward jump -> loop
                    loop_starts.append(label_positions[target])
                    loop_ends.append(idx)
                    
        if not loop_starts:
            return instrs, False

        # Optimize the first detected loop
        start = loop_starts[0]
        end = loop_ends[0]
        
        # Find all variables modified inside loop
        modified_in_loop = set()
        for idx in range(start, end + 1):
            inst = instrs[idx]
            if inst.result:
                modified_in_loop.add(inst.result)
                
        # Find invariant expressions (whose operands are not modified in loop and are constants or external)
        invariants = []
        remaining_loop_body = []
        
        for idx in range(start + 1, end): # exclude boundary labels/jumps
            inst = instrs[idx]
            if inst.op in ['+', '-', '*', '/', '<<', '>>', '='] and inst.result:
                # Check operands
                op1_ok = inst.arg1.isdigit() or (inst.arg1 not in modified_in_loop)
                op2_ok = not inst.arg2 or inst.arg2.isdigit() or (inst.arg2 not in modified_in_loop)
                
                if op1_ok and op2_ok:
                    invariants.append(inst)
                    modified_in_loop.remove(inst.result) # no longer modified in a changing way
                    self.log_opt("Loop Invariant Code Motion", str(inst), "Moved outside loop", "Operand values do not change inside the loop")
                    changed = True
                else:
                    remaining_loop_body.append(inst)
            else:
                remaining_loop_body.append(inst)
                
        if changed:
            # Reconstruct instructions
            # Insert invariants right before the loop start label
            prefix = instrs[:start]
            loop_label = instrs[start]
            suffix = instrs[end+1:]
            
            new_instrs = prefix + invariants + [loop_label] + remaining_loop_body + [instrs[end]] + suffix
            return new_instrs, True
            
        return instrs, False
