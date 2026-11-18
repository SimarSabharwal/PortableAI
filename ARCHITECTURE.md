# PortableAI Architecture & Decision Record

## Chosen Runtime Stack
1. **Inference Engine:** `llama.cpp` (`b12318`, `llama-b12318-bin-win-cpu-x64.zip` in `engine/`)
   - **Why:** Native C++ CPU-only binary with dynamic SIMD dispatch (`ggml-cpu-*.dll`), zero CUDA/GPU requirement, zero admin installation, native GGUF support, and an OpenAI-compatible local HTTP server (`llama-server.exe`) that keeps the model loaded in RAM across follow-up turns.
   - **Why not a JVM-only library:** Many Java LLM wrappers either require JNI native builds tied to specific JDK versions (17/21+) or lack support for newer GGUF quantizations and chat templates. `llama-server.exe` is decoupled from whatever JDK version is installed on the college PC.
2. **CLI Application Runtime:** Python 3.12.8 Embeddable (`runtime/python/`) + `app/portable_ai.py`
   - **Why:** ~11 MB self-contained runtime using only Python's standard library (`urllib.request`, `subprocess`, `json`, `pathlib`), avoiding any `pip install` or internet dependency.
3. **Models (`models/`):**
   - **Primary:** `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` (Apache 2.0, ~2.5 GB) — strong instruction-following and multi-concept C/Java synthesis without `<think>` token overhead.
   - **Fast Fallback:** `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf` (Apache 2.0, ~1.0 GB) — lower RAM footprint and faster CPU token rate on older college CPUs.
4. **Portability:** All scripts resolve paths relative to `%~dp0` / `Path(__file__).resolve().parent.parent`, so `PORTABLE_AI` works from any USB drive letter or when copied to Desktop.
