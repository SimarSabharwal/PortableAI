# PortableAI Test Report (Development Laptop — CPU-Only)

**Date:** 2026-11-12  
**Machine:** Windows 11 x64 (`Version 10.0.26300.9711`), 31.73 GB RAM, JDK 17.0.21 (`javac` / `java` available; `gcc` not installed).  
**Inference Mode:** CPU-only (`-ngl 0`), 100% local from `i:\PORTABLE_AI\`.

## 1. Diagnostics (`DIAGNOSTICS.bat`)
- Portable Python 3.12.8 (`runtime\python\python.exe`): **PASS**
- `llama-server.exe` (`engine\llama-server.exe`): **PASS**
- Local models present:
  - `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` (2,497,281,120 bytes)
  - `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` (1,117,320,768 bytes)
- Write permissions (`output\`, `logs\`): **PASS**

## 2. CPU-Only Generation Benchmarks (`tests\run_eval.py`)

| Model | Load Time | Case | First Token | Total Time | Output Size | Integrity Warnings | `javac` Compile |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `qwen3-4b` | 6.19s | `c_level3_indirect` | 10.31s | 123.43s | 5,911 chars | None | Not tested (no `gcc` on laptop) |
| `qwen3-4b` | 6.19s | `java_oop_indirect` | 5.88s | 57.26s | 3,485 chars | None | Failed (`SmartLight` not converted to `SmartDevice`) |
| `qwen25-1.5b` | 3.59s | `c_level3_indirect` | 4.09s | 24.82s | 3,102 chars | None | Not tested (no `gcc` on laptop) |
| `qwen25-1.5b` | 3.59s | `java_oop_indirect` | 2.06s | 33.80s | 5,970 chars | None | Failed (`String name` redeclared across `switch` cases) |

**Action taken after test:** Updated `config\prompts\java.txt` with explicit rules against `switch`-case variable redeclaration and mismatched polymorphic array base types.

## 3. Unverified on Target College PC
- College PC execution policy for `.exe` (`python.exe`, `llama-server.exe`), actual college CPU speed/RAM usage, C compilation (`gcc` / Turbo C), and offline run on the college machine remain to be verified tomorrow using `DIAGNOSTICS.bat` and `TARGET_CHECKLIST.md`.
