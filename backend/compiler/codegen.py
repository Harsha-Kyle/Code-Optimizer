from typing import List, Dict, Optional
from .ir_builder import Instruction

class CodeGenerator:
    def __init__(self, instructions: List[Instruction], reg_map: Dict[str, str], spills: Dict[str, int]):
        self.instructions = instructions
        self.reg_map = reg_map
        self.spills = spills
        self.assembly: List[str] = []

    def get_val(self, val: str) -> str:
        # Check if constant or register or stack load
        if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
            return f"#{val}"
        if val in self.reg_map:
            return self.reg_map[val]
        return val # fallback string

    def load_if_spilled(self, val: str, temp_reg: str) -> Optional[str]:
        if val in self.spills:
            offset = self.spills[val]
            self.assembly.append(f"    LDR {temp_reg}, [SP, #{offset}]  @ Load spilled {val}")
            return temp_reg
        return None

    def store_if_spilled(self, val: str, source_reg: str):
        if val in self.spills:
            offset = self.spills[val]
            self.assembly.append(f"    STR {source_reg}, [SP, #{offset}]  @ Spill {val} to stack")

    def generate(self) -> str:
        self.assembly = []
        
        # Calculate stack frame size (spills + local space)
        total_spill_space = len(self.spills) * 4
        
        for inst in self.instructions:
            self.assembly.append(f"    @ {str(inst)}") # Keep track of original instruction in comments
            
            if inst.op == 'LABEL':
                self.assembly.append(f"{inst.arg1}:")
                # If function entry, set up stack frame
                if not inst.arg1.startswith('L'):
                    self.assembly.append("    PUSH {LR}")
                    if total_spill_space > 0:
                        self.assembly.append(f"    SUB SP, SP, #{total_spill_space}  @ Alloc frame")
                continue
                
            elif inst.op == 'RETURN':
                if inst.arg1:
                    reg = self.reg_map.get(inst.arg1, None)
                    if reg:
                        if reg != "R0":
                            self.assembly.append(f"    MOV R0, {reg}")
                    else:
                        # Spilled return value
                        self.load_if_spilled(inst.arg1, "R0")
                if total_spill_space > 0:
                    self.assembly.append(f"    ADD SP, SP, #{total_spill_space}  @ Free frame")
                self.assembly.append("    POP {PC}")
                continue
                
            elif inst.op == 'JUMP':
                self.assembly.append(f"    B {inst.arg1}")
                continue
                
            elif inst.op == 'IF':
                cond_reg = self.reg_map.get(inst.arg1, "R0")
                spill_reg = self.load_if_spilled(inst.arg1, "R0")
                use_reg = spill_reg if spill_reg else cond_reg
                
                # Check condition: if not zero, jump to arg2, else jump to result (else-label)
                self.assembly.append(f"    CMP {use_reg}, #0")
                self.assembly.append(f"    BNE {inst.arg2}")
                self.assembly.append(f"    B {inst.result}")
                continue
                
            elif inst.op == '=':
                dest = inst.result
                dest_reg = self.reg_map.get(dest, "R0")
                src_val = inst.arg1
                
                # Source spilled?
                spill_reg = self.load_if_spilled(src_val, "R1")
                src_repr = spill_reg if spill_reg else self.get_val(src_val)
                
                dest_use = dest_reg if dest not in self.spills else "R0"
                self.assembly.append(f"    MOV {dest_use}, {src_repr}")
                
                self.store_if_spilled(dest, dest_use)
                continue
                
            elif inst.op in ['+', '-', '*', '/', '<<', '>>', '&', '|', '^']:
                dest = inst.result
                dest_reg = self.reg_map.get(dest, "R0")
                
                # Load operands
                s1 = self.load_if_spilled(inst.arg1, "R1")
                r1 = s1 if s1 else self.get_val(inst.arg1)
                
                s2 = self.load_if_spilled(inst.arg2, "R2")
                r2 = s2 if s2 else self.get_val(inst.arg2)
                
                dest_use = dest_reg if dest not in self.spills else "R0"
                
                if inst.op == '+':
                    self.assembly.append(f"    ADD {dest_use}, {r1}, {r2}")
                elif inst.op == '-':
                    self.assembly.append(f"    SUB {dest_use}, {r1}, {r2}")
                elif inst.op == '*':
                    self.assembly.append(f"    MUL {dest_use}, {r1}, {r2}")
                elif inst.op == '<<':
                    self.assembly.append(f"    LSL {dest_use}, {r1}, {r2}")
                elif inst.op == '>>':
                    self.assembly.append(f"    LSR {dest_use}, {r1}, {r2}")
                elif inst.op == '&':
                    self.assembly.append(f"    AND {dest_use}, {r1}, {r2}")
                elif inst.op == '|':
                    self.assembly.append(f"    ORR {dest_use}, {r1}, {r2}")
                elif inst.op == '^':
                    self.assembly.append(f"    EOR {dest_use}, {r1}, {r2}")
                elif inst.op == '/':
                    self.assembly.append(f"    SDIV {dest_use}, {r1}, {r2}")
                    
                self.store_if_spilled(dest, dest_use)
                continue

            elif inst.op in ['==', '!=', '<', '>', '<=', '>=']:
                dest = inst.result
                dest_reg = self.reg_map.get(dest, "R0")
                
                s1 = self.load_if_spilled(inst.arg1, "R1")
                r1 = s1 if s1 else self.get_val(inst.arg1)
                
                s2 = self.load_if_spilled(inst.arg2, "R2")
                r2 = s2 if s2 else self.get_val(inst.arg2)
                
                dest_use = dest_reg if dest not in self.spills else "R0"
                
                self.assembly.append(f"    CMP {r1}, {r2}")
                if inst.op == '==':
                    self.assembly.append(f"    MOVEQ {dest_use}, #1")
                    self.assembly.append(f"    MOVNE {dest_use}, #0")
                elif inst.op == '!=':
                    self.assembly.append(f"    MOVNE {dest_use}, #1")
                    self.assembly.append(f"    MOVEQ {dest_use}, #0")
                elif inst.op == '<':
                    self.assembly.append(f"    MOVLT {dest_use}, #1")
                    self.assembly.append(f"    MOVGE {dest_use}, #0")
                elif inst.op == '>':
                    self.assembly.append(f"    MOVGT {dest_use}, #1")
                    self.assembly.append(f"    MOVLE {dest_use}, #0")
                elif inst.op == '<=':
                    self.assembly.append(f"    MOVLE {dest_use}, #1")
                    self.assembly.append(f"    MOVGT {dest_use}, #0")
                elif inst.op == '>=':
                    self.assembly.append(f"    MOVGE {dest_use}, #1")
                    self.assembly.append(f"    MOVLT {dest_use}, #0")
                    
                self.store_if_spilled(dest, dest_use)
                continue

            elif inst.op == 'LOAD':
                dest = inst.result
                dest_reg = self.reg_map.get(dest, "R0")
                addr_val = inst.arg1
                
                # Address reg
                addr_spill = self.load_if_spilled(addr_val, "R1")
                addr_reg = addr_spill if addr_spill else self.reg_map.get(addr_val, "R1")
                
                dest_use = dest_reg if dest not in self.spills else "R0"
                self.assembly.append(f"    LDR {dest_use}, [{addr_reg}]")
                self.store_if_spilled(dest, dest_use)
                continue

            elif inst.op == 'STORE':
                addr_val = inst.arg1
                val_val = inst.result
                
                addr_spill = self.load_if_spilled(addr_val, "R1")
                addr_reg = addr_spill if addr_spill else self.reg_map.get(addr_val, "R1")
                
                val_spill = self.load_if_spilled(val_val, "R2")
                val_reg = val_spill if val_spill else self.reg_map.get(val_val, "R2")
                
                self.assembly.append(f"    STR {val_reg}, [{addr_reg}]")
                continue

        return "\n".join(self.assembly)
