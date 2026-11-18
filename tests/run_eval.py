"""
Automated offline evaluation script for PortableAI.
Tests model loading (CPU-only), C & Java code generation, and Java compilation (if javac is available).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "app"))

import portable_ai  # noqa: E402


TEST_CASES = [
    {
        "id": "c_level3_indirect",
        "lang": "C",
        "prompt": (
            "A library counter receives book return requests and needs to process them in order, "
            "while also keeping an undo stack of the last 10 issued books. Write a menu-driven C program "
            "that lets the librarian enqueue return requests, process the next return, push an issued book ID, "
            "undo the last issued book, and display both pending returns and recent issues."
        ),
    },
    {
        "id": "java_oop_indirect",
        "lang": "Java",
        "prompt": (
            "Design a smart home controller in Java where devices can be both Switchable (turnOn, turnOff) "
            "and Schedulable (scheduleAt). Implement SmartLight and SmartAC classes, store them in an array, "
            "and demonstrate dynamic dispatch and interface polymorphism in Main."
        ),
    },
]


def main() -> int:
    settings = portable_ai.load_settings()
    models = portable_ai.available_models(settings)
    if not models:
        print("No models found.")
        return 1

    javac_path = shutil.which("javac")
    java_path = shutil.which("java")
    results = []

    for model in models:
        print(f"\n=== Evaluating {model['id']} ({model['size_gb']} GB) ===")
        server = portable_ai.LlamaServerManager(settings)
        t0 = time.time()
        server.start(model)
        load_s = round(time.time() - t0, 2)

        try:
            for tc in TEST_CASES:
                print(f"\n--- Running {tc['id']} ({tc['lang']}) ---")
                sys_prompt = portable_ai.build_system_prompt(tc["lang"], 3, "standard-c", code_only=True)
                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": tc["prompt"]},
                ]
                reply, stats = server.chat_stream(messages, max_tokens=1536, temperature=0.2, top_p=0.9)
                code = portable_ai.extract_code_block(reply, tc["lang"])
                warnings = portable_ai.check_integrity(reply, stats["finish_reason"])

                compiled = None
                compile_err = ""
                if tc["lang"] == "Java" and javac_path:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        java_file = Path(tmpdir) / "Main.java"
                        java_file.write_text(code, encoding="utf-8")
                        proc = subprocess.run(
                            [javac_path, str(java_file)],
                            cwd=tmpdir,
                            capture_output=True,
                            text=True,
                            timeout=20,
                        )
                        compiled = proc.returncode == 0
                        if not compiled:
                            compile_err = proc.stderr.strip()
                        elif java_path:
                            run_proc = subprocess.run(
                                [java_path, "Main"],
                                cwd=tmpdir,
                                input="",
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )
                            print(f"[Java run exit={run_proc.returncode}]")

                results.append({
                    "model": model["id"],
                    "load_s": load_s,
                    "case": tc["id"],
                    "first_token_s": stats["first_token_s"],
                    "total_s": stats["total_s"],
                    "finish_reason": stats["finish_reason"],
                    "chars": len(code),
                    "warnings": warnings,
                    "compiled": compiled,
                    "compile_err": compile_err[:300],
                })
        finally:
            server.stop()

    report_path = BASE_DIR / "logs" / "eval_results.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved evaluation results to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
