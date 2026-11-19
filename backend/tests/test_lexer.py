import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir_builder import IRBuilder

def test_lexer_parser_semantic_ir():
    source = """
    int calculate(int a, int b) {
        int x = a + b;
        int y = x * 2;
        int z = 10 * 20;
        return y;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert len(lexer.errors) == 0
    assert any(t.value == "calculate" for t in tokens)
    
    parser = Parser(tokens)
    program = parser.parse()
    assert len(parser.errors) == 0
    assert program is not None
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    assert len(analyzer.errors) == 0
    
    builder = IRBuilder()
    ir_dict = builder.build(program)
    assert "calculate" in ir_dict
    instructions = ir_dict["calculate"]
    # Check that IR was generated
    assert len(instructions) > 0
    ops = [inst.op for inst in instructions]
    assert "+" in ops
    assert "*" in ops
