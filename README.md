# PortableAI — Offline USB Coding Assistant (C, Java & Oracle SQL)

Fully self-contained, CPU-only, offline coding assistant for Windows 10/11 x64.
Compatible with **both AMD (Ryzen / Athlon / FX) and Intel (Core / Xeon)** processors via dynamic SIMD runtime dispatch (AVX512 / AVX2 / AVX / SSE4.2 / x64).

## How to Use on College PC (Step-by-Step)

1. Plug in the USB drive (or copy the `PORTABLE_AI` folder to Desktop if permitted by college policy).
2. Double-click **`DIAGNOSTICS.bat`** first (or run it from Command Prompt) to verify that Python, `llama-server.exe`, CPU architecture (Intel or AMD), the `.gguf` model, RAM, and write permissions all work on that PC.
3. Double-click **`START.bat`** to launch the assistant.
4. Choose a model:
   - **Qwen3 4B Instruct (~2.5 GB):** Better reasoning on complex Level 3/4 C, OOP Java, and advanced Oracle SQL/PL-SQL queries.
   - **Qwen2.5 Coder 1.5B (~1.0 GB):** Faster token generation on slower CPUs (Intel Core i3/i5 or older AMD CPUs).
5. Select:
   - **1 (C Programming)**
   - **2 (Java Programming)**
   - **3 (Oracle SQL / PL-SQL)**
   - **4 (Debug Existing Code / Fix Error)**
   Paste or type your practical question or faulty code + compiler error, and submit with `END` on a new line (or press Enter twice).
6. Choose **1 (Full Answer)** or **2 (Code Only)**.
7. After generation, you can ask follow-ups, continue truncated output, or save the output directly to `output\` as `.c`, `.java`, or `.sql`.

## Troubleshooting

- **`llama-server.exe` blocked or fails to start:** Check `logs\llama-server.log`. If blocked by college antivirus/AppLocker, do not bypass—run from an IT-approved folder or ask IT.
- **Slow generation:** Switch to `Qwen2.5 Coder 1.5B` from the main menu (`4. Switch Model`).
- **Turbo C compatibility:** From the main menu choose `3. Configure C Options` -> select `2` (`turbo-c`).
