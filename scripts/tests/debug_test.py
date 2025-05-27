#!/usr/bin/env python3
"""
Debug Test - Identificar problemas específicos
"""

import sys
import traceback

def test_imports():
    """Testa imports um por um"""
    print("🔍 Testando imports...")
    
    try:
        print("1. Testando import openai...")
        import openai
        print("   ✅ openai OK")
    except Exception as e:
        print(f"   ❌ openai ERRO: {e}")
    
    try:
        print("2. Testando import SafeCodeGenerator...")
        from src.core.self_modify.safe_code_generator import SafeCodeGenerator
        print("   ✅ SafeCodeGenerator import OK")
        
        print("3. Testando inicialização SafeCodeGenerator...")
        generator = SafeCodeGenerator()
        print("   ✅ SafeCodeGenerator init OK")
        
        print("4. Testando método _analyze_code_locally...")
        test_code = "def test(): pass"
        result = generator._analyze_code_locally(test_code)
        print(f"   ✅ _analyze_code_locally OK: {type(result)}")
        
        print("5. Testando get_generation_stats...")
        stats = generator.get_generation_stats()
        print(f"   ✅ get_generation_stats OK: {stats}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_imports() 