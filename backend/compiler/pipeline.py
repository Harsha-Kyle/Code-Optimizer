from typing import Dict, Any, List
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .ir_builder import IRBuilder
from .optimizer import Optimizer
from .register_alloc import RegisterAllocator
from .codegen import CodeGenerator
from .analysis import ResourceAnalyzer

class CompilerPipeline:
    def __init__(self, source_code: str, target: str = "arm_cortex_m4", passes: Dict[str, bool] = None):
        self.source = source_code
        self.target = target
        self.passes = passes if passes is not None else {
            "constant_folding": True,
            "constant_propagation": True,
            "dead_code": True,
            "cse": True,
            "algebraic": True,
            "strength_reduction": True,
            "loop_optimization": True
        }

    def compile(self) -> Dict[str, Any]:
        import time

        result = {
            "success": False,
            "errors": [],
            "tokens": [],
            "ast": {},
            "ir_before": "",
            "ir_after": "",
            "optimization_log": [],
            "assembly": "",
            "assembly_o0": "",
            "cfg_mermaid": "",
            "timings": {},
            "metrics_before": {},
            "metrics_after": {},
            "register_allocation": {}
        }
        
        total_start = time.perf_counter()

        # 1. Lexer
        t0 = time.perf_counter()
        lexer = Lexer(self.source)
        tokens = lexer.tokenize()
        result["tokens"] = [t.to_dict() for t in tokens]
        result["timings"]["Lexing"] = round((time.perf_counter() - t0) * 1000, 3)

        if lexer.errors:
            result["errors"].extend(lexer.errors)
            return result

        # 2. Parser
        t0 = time.perf_counter()
        parser = Parser(tokens)
        program = parser.parse()
        result["timings"]["Parsing"] = round((time.perf_counter() - t0) * 1000, 3)

        if parser.errors:
            result["errors"].extend(parser.errors)
            return result
        result["ast"] = program.to_dict() if program else {}

        # 3. Semantic Analysis
        t0 = time.perf_counter()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)
        result["timings"]["Semantic Analysis"] = round((time.perf_counter() - t0) * 1000, 3)

        if analyzer.errors:
            result["errors"].extend(analyzer.errors)
            return result

        # 4. IR Generation
        t0 = time.perf_counter()
        builder = IRBuilder()
        ir_dict = builder.build(program)
        result["timings"]["IR Generation"] = round((time.perf_counter() - t0) * 1000, 3)
        
        # Convert IR list to structured string representation
        def ir_to_str(ir_list):
            return "\n".join([str(inst) for inst in ir_list])

        if not ir_dict:
            result["errors"].append({"line": 1, "column": 1, "type": "IR Error", "message": "No functions found."})
            return result
            
        func_name = list(ir_dict.keys())[0]
        raw_ir = ir_dict[func_name]
        result["ir_before"] = ir_to_str(raw_ir)

        # Calculate metrics for O0 (before optimizations)
        o0_allocator = RegisterAllocator(raw_ir)
        o0_reg_map, o0_spills = o0_allocator.allocate()
        o0_codegen = CodeGenerator(raw_ir, o0_reg_map, o0_spills)
        o0_asm = o0_codegen.generate()
        result["assembly_o0"] = o0_asm
        
        analyzer_m2 = ResourceAnalyzer(self.target)
        result["metrics_before"] = analyzer_m2.analyze_assembly(o0_asm, o0_allocator.spill_count)

        # 5. Optimization
        t0 = time.perf_counter()
        opt = Optimizer(raw_ir)
        optimized_ir = opt.run_all(self.passes)
        result["ir_after"] = ir_to_str(optimized_ir)
        result["optimization_log"] = opt.log
        result["timings"]["Optimization"] = round((time.perf_counter() - t0) * 1000, 3)

        # 6. Register Allocation (M3)
        t0 = time.perf_counter()
        allocator = RegisterAllocator(optimized_ir)
        reg_map, spills = allocator.allocate()
        result["register_allocation"] = {
            "mapping": reg_map,
            "spills": spills,
            "spill_count": allocator.spill_count,
            "utilization": allocator.utilization
        }
        result["timings"]["Register Allocation"] = round((time.perf_counter() - t0) * 1000, 3)

        # 7. Code Generation (M3)
        t0 = time.perf_counter()
        codegen = CodeGenerator(optimized_ir, reg_map, spills)
        optimized_asm = codegen.generate()
        result["assembly"] = optimized_asm
        result["timings"]["Code Generation"] = round((time.perf_counter() - t0) * 1000, 3)

        # 8. Optimized metrics calculation
        result["metrics_after"] = analyzer_m2.analyze_assembly(optimized_asm, allocator.spill_count)

        # 9. Generate Mermaid Control Flow Graph (CFG)
        result["cfg_mermaid"] = self._generate_mermaid_cfg(optimized_ir, func_name)

        result["timings"]["Total Pipeline Time"] = round((time.perf_counter() - total_start) * 1000, 3)
        result["success"] = True
        return result

    def _generate_mermaid_cfg(self, instrs: List[Any], func_name: str) -> str:
        # Group instructions into basic blocks
        blocks = []
        current_block_name = func_name
        current_instrs = []
        
        for inst in instrs:
            if inst.op == 'LABEL':
                if current_instrs:
                    blocks.append((current_block_name, current_instrs))
                current_block_name = inst.arg1
                current_instrs = [str(inst)]
            else:
                current_instrs.append(str(inst))
                
        if current_instrs:
            blocks.append((current_block_name, current_instrs))

        mermaid_lines = ["graph TD"]
        
        # Build block nodes and edges
        for idx, (b_name, b_code) in enumerate(blocks):
            # Escape code for mermaid block display
            clean_code = "<br/>".join([c.replace('"', "'") for c in b_code[:8]])
            if len(b_code) > 8:
                clean_code += "<br/>..."
            node_def = f'    {b_name}["<b>Block: {b_name}</b><br/>{clean_code}"]'
            mermaid_lines.append(node_def)
            
            # Check transitions/edges
            last_inst = b_code[-1] if b_code else ""
            if "goto" in last_inst or "IF" in last_inst or "if" in last_inst:
                # Find target labels
                words = last_inst.split()
                for word in words:
                    if word.startswith("L") and word[1:].isdigit():
                        mermaid_lines.append(f'    {b_name} --> {word}')
            else:
                # Sequential fallthrough to next block if available
                if idx + 1 < len(blocks):
                    next_block_name = blocks[idx + 1][0]
                    if not last_inst.startswith("return"):
                        mermaid_lines.append(f'    {b_name} --> {next_block_name}')
                        
        return "\n".join(mermaid_lines)
