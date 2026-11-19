import pytest
from compiler.pipeline import CompilerPipeline

def test_full_pipeline_success():
    source = """
    int run() {
        int a = 10;
        int b = a + 5;
        int c = b * 2;
        return c;
    }
    """
    pipeline = CompilerPipeline(source, target="arm_cortex_m4")
    res = pipeline.compile()
    
    assert res["success"] is True
    assert "run" in res["assembly"]
    assert res["metrics_before"]["instruction_count"] > 0
    assert res["metrics_after"]["instruction_count"] > 0
    
    # Verify optimization reduced instruction count or kept it same/optimal
    assert res["metrics_after"]["instruction_count"] <= res["metrics_before"]["instruction_count"]

def test_full_pipeline_with_semantic_error():
    source = """
    int run() {
        int a = x + 5; // x is undeclared
        return a;
    }
    """
    pipeline = CompilerPipeline(source)
    res = pipeline.compile()
    
    assert res["success"] is False
    assert len(res["errors"]) > 0
    assert any("Undeclared" in e["message"] for e in res["errors"])
