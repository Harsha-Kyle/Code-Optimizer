from typing import List, Dict, Any
from .ir_builder import Instruction

# Predefined estimated CPU cycle cost model for targets
CYCLE_WEIGHTS = {
    "arm_cortex_m4": {
        "MOV": 1, "ADD": 1, "SUB": 1, "MUL": 2, "SDIV": 8, "LSL": 1, "LSR": 1,
        "AND": 1, "ORR": 1, "EOR": 1, "CMP": 1, "B": 2, "BNE": 2,
        "LDR": 2, "STR": 2, "PUSH": 3, "POP": 3, "default": 1
    },
    "arm_cortex_m0": {
        "MOV": 1, "ADD": 1, "SUB": 1, "MUL": 32, "SDIV": 45, "LSL": 1, "LSR": 1,
        "AND": 1, "ORR": 1, "EOR": 1, "CMP": 1, "B": 3, "BNE": 3,
        "LDR": 2, "STR": 2, "PUSH": 4, "POP": 4, "default": 1
    },
    "avr_atmega328p": {
        "MOV": 1, "ADD": 1, "SUB": 1, "MUL": 2, "SDIV": 120, "LSL": 1, "LSR": 1,
        "AND": 1, "ORR": 1, "EOR": 1, "CMP": 1, "B": 2, "BNE": 2,
        "LDR": 3, "STR": 3, "PUSH": 2, "POP": 2, "default": 1
    }
}

class ResourceAnalyzer:
    def __init__(self, target_profile: str = "arm_cortex_m4"):
        self.target = target_profile
        self.weights = CYCLE_WEIGHTS.get(target_profile, CYCLE_WEIGHTS["arm_cortex_m4"])

    def analyze_assembly(self, assembly_text: str, spill_count: int) -> Dict[str, Any]:
        lines = assembly_text.split('\n')
        instruction_count = 0
        estimated_cycles = 0
        memory_accesses = 0
        code_size_bytes = 0
        
        # AVR/Atmega has 2-byte word width; ARM Cortex M has 4-byte / 2-byte instructions.
        word_size = 4 if "arm" in self.target else 2
        
        for line in lines:
            line_strip = line.strip()
            # Skip comments or labels
            if not line_strip or line_strip.startswith('@') or line_strip.endswith(':'):
                continue
                
            instruction_count += 1
            # Basic code size estimate (2 or 4 bytes per instruction)
            code_size_bytes += word_size
            
            # Extract first word as instruction op
            parts = line_strip.split()
            op = parts[0].upper()
            
            # Map cost
            cycles = self.weights.get(op, self.weights["default"])
            estimated_cycles += cycles
            
            # If load or store, increment memory access counter
            if op in ["LDR", "STR", "PUSH", "POP"]:
                memory_accesses += 1
                
        # Stack usage calculation: spills + active links
        stack_usage_bytes = (spill_count * 4) + (4 if "PUSH" in assembly_text else 0)
        
        # Estimate power cost score based on cycles + memory transactions
        # E.g. 1 cycle = 1 unit energy, 1 memory transaction = 5 units energy
        estimated_power_cost = estimated_cycles * 1.2 + memory_accesses * 4.5
        
        return {
            "instruction_count": instruction_count,
            "estimated_cycles": estimated_cycles,
            "code_size_bytes": code_size_bytes,
            "stack_usage_bytes": stack_usage_bytes,
            "memory_accesses": memory_accesses,
            "estimated_power_cost": round(estimated_power_cost, 1)
        }
