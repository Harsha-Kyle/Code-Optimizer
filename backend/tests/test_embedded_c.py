import pytest
from compiler.pipeline import CompilerPipeline

def test_embedded_c_features():
    code = """
    #include <stdint.h>

    #define LED_PIN_0    (1 << 0)
    #define LED_PIN_1    (1 << 1)
    #define LED_PIN_2    (1 << 2)

    void bit_manipulation_demo(void) {
        uint8_t GPIO_Register = 0x00;

        GPIO_Register |= LED_PIN_0;
        GPIO_Register ^= LED_PIN_1;
        GPIO_Register &= ~LED_PIN_0;

        if (GPIO_Register & LED_PIN_1) {
            GPIO_Register = 1;
        }
    }
    """
    pipeline = CompilerPipeline(code)
    res = pipeline.compile()
    
    assert res["success"] is True
    assert len(res["errors"]) == 0
    assert "bit_manipulation_demo" in res["assembly"]
