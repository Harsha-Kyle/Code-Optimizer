from typing import List, Dict, Set, Tuple
from .ir_builder import Instruction

class RegisterAllocator:
    def __init__(self, instructions: List[Instruction], num_registers: int = 12):
        # We target ARM Cortex-M general registers R0 - R11 (12 general registers)
        self.instructions = instructions
        self.num_regs = num_registers
        self.register_mapping: Dict[str, str] = {} # var -> reg (e.g. 'R0')
        self.spills: Dict[str, int] = {}          # var -> stack offset
        self.stack_offset = 0
        self.utilization = 0
        self.spill_count = 0

    def allocate(self) -> Tuple[Dict[str, str], Dict[str, int]]:
        # Step 1: Compute live intervals
        # Map variables to (start_instr_idx, end_instr_idx)
        intervals: Dict[str, List[int]] = {}
        
        for idx, inst in enumerate(self.instructions):
            # Define (write)
            if inst.result and inst.op not in ['STORE', 'CALL', 'LABEL']:
                var = inst.result
                if var.startswith('t') or var.isidentifier():
                    if var not in intervals:
                        intervals[var] = [idx, idx]
                    else:
                        intervals[var][1] = idx
            # Use (read)
            for var in [inst.arg1, inst.arg2]:
                if var and (var.startswith('t') or (var.isidentifier() and not var.isdigit())):
                    if var not in intervals:
                        intervals[var] = [idx, idx]
                    else:
                        intervals[var][1] = idx

        # Step 2: Linear Scan allocation
        # Sort intervals by start time
        sorted_vars = sorted(intervals.keys(), key=lambda v: intervals[v][0])
        
        active: List[str] = []
        free_regs = [f"R{i}" for i in range(self.num_regs)]
        
        for var in sorted_vars:
            start, end = intervals[var]
            
            # Expire old intervals
            active_copy = active[:]
            for active_var in active_copy:
                a_start, a_end = intervals[active_var]
                if a_end < start:
                    # Free register
                    reg = self.register_mapping[active_var]
                    free_regs.append(reg)
                    active.remove(active_var)
            
            # Allocate or spill
            if len(free_regs) > 0:
                reg = free_regs.pop(0)
                self.register_mapping[var] = reg
                active.append(var)
            else:
                # Spill candidate: variable in active with the furthest end time
                spill_candidate = max(active, key=lambda v: intervals[v][1])
                if intervals[spill_candidate][1] > end:
                    # Spill the candidate, give its register to current var
                    reg = self.register_mapping[spill_candidate]
                    del self.register_mapping[spill_candidate]
                    active.remove(spill_candidate)
                    
                    # Store spilled var on stack
                    self.stack_offset += 4
                    self.spills[spill_candidate] = self.stack_offset
                    self.spill_count += 1
                    
                    self.register_mapping[var] = reg
                    active.append(var)
                else:
                    # Spill current var
                    self.stack_offset += 4
                    self.spills[var] = self.stack_offset
                    self.spill_count += 1
                    
        # Calculate utilization metrics
        unique_allocated = set(self.register_mapping.values())
        self.utilization = len(unique_allocated)
        
        return self.register_mapping, self.spills
