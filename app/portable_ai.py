"""
PortableAI - Fully Offline USB Coding Assistant (C & Java)
Runs with Python 3.12 embeddable (stdlib only) + local llama-server.exe (CPU-only).
"""

import atexit
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"
PROMPTS_DIR = BASE_DIR / "config" / "prompts"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
ENGINE_EXE = BASE_DIR / "engine" / "llama-server.exe"


def load_settings() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def find_free_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", preferred)) != 0:
            return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def available_models(settings: dict) -> list[dict]:
    found = []
    for m in settings.get("models", []):
        p = BASE_DIR / m["path"]
        if p.exists() and p.is_file() and p.stat().st_size > 1_000_000:
            item = dict(m)
            item["abs_path"] = p
            item["size_gb"] = round(p.stat().st_size / (1024 ** 3), 2)
            found.append(item)
    return found


class LlamaServerManager:
    def __init__(self, settings: dict):
        self.settings = settings
        self.proc: subprocess.Popen | None = None
        self.port: int = settings["server"]["port"]
        self.base_url: str = ""
        self.current_model: dict | None = None
        self._log_file = None

    def start(self, model: dict) -> None:
        self.stop()
        if not ENGINE_EXE.exists():
            raise FileNotFoundError(f"Inference engine not found: {ENGINE_EXE}")

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.port = find_free_port(self.settings["server"]["port"])
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.current_model = model

        cmd = [
            str(ENGINE_EXE),
            "-m", str(model["abs_path"]),
            "--host", "127.0.0.1",
            "--port", str(self.port),
            "-c", str(model.get("ctx_size", 4096)),
            "-ngl", "0",
        ]
        threads = self.settings["server"].get("threads", 0)
        if threads and threads > 0:
            cmd.extend(["-t", str(threads)])

        log_path = LOGS_DIR / "llama-server.log"
        self._log_file = open(log_path, "w", encoding="utf-8", errors="replace")

        creation_flags = 0
        if os.name == "nt":
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        print(f"\nLoading model: {model['label']} ({model['size_gb']} GB)...")
        print("Mode: CPU-only, 100% offline. Please wait...")
        t0 = time.time()
        self.proc = subprocess.Popen(
            cmd,
            cwd=str(ENGINE_EXE.parent),
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
            creationflags=creation_flags,
        )

        timeout = self.settings["server"].get("startup_timeout_sec", 90)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                self._log_file.flush()
                err_detail = ""
                try:
                    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                        err_detail = "".join(lines[-15:])
                except Exception:
                    pass
                raise RuntimeError(
                    f"llama-server exited early (code {self.proc.returncode}).\n"
                    f"--- Engine Log Output ---\n{err_detail}\n"
                    f"See full log at {log_path}"
                )
            try:
                with urllib.request.urlopen(f"{self.base_url}/health", timeout=2) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        if data.get("status") in ("ok", None):
                            elapsed = time.time() - t0
                            print(f"Model ready in {elapsed:.1f}s (port {self.port}).\n")
                            return
            except Exception:
                pass
            time.sleep(0.5)

        self.stop()
        err_detail = ""
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                err_detail = "".join(f.readlines()[-15:])
        except Exception:
            pass
        raise TimeoutError(
            f"Model did not become ready within {timeout}s.\n"
            f"--- Engine Log Output ---\n{err_detail}\n"
            f"See full log at {log_path}"
        )

    def stop(self) -> None:
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None
        if self._log_file is not None:
            try:
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None

    def chat_stream(self, messages: list[dict], max_tokens: int, temperature: float, top_p: float) -> tuple[str, dict]:
        payload = json.dumps({
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        chunks: list[str] = []
        finish_reason = "unknown"
        t_start = time.time()
        t_first = None

        with urllib.request.urlopen(req, timeout=300) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    obj = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                token = delta.get("content")
                if token:
                    if t_first is None:
                        t_first = time.time() - t_start
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    chunks.append(token)
                if choices[0].get("finish_reason"):
                    finish_reason = choices[0]["finish_reason"]

        print()
        total_time = time.time() - t_start
        full_text = "".join(chunks)
        stats = {
            "first_token_s": round(t_first, 2) if t_first is not None else None,
            "total_s": round(total_time, 2),
            "finish_reason": finish_reason,
            "chars": len(full_text),
        }
        return full_text, stats


def build_system_prompt(language: str, c_level: int, c_profile: str, mode: str = "full") -> str:
    common = load_prompt("common.txt")
    if language == "C":
        lang_prompt = load_prompt("c.txt")
    elif language == "Java":
        lang_prompt = load_prompt("java.txt")
    else:
        lang_prompt = load_prompt("oracle.txt")

    if mode == "code_only":
        mode_instruction = "OUTPUT MODE: CODE ONLY. Return ONLY the complete source code or SQL queries in a single fenced code block, with no explanations."
    elif mode == "debug":
        mode_instruction = (
            "OUTPUT MODE: DEBUG / ERROR FIX. The user will provide their code along with compiler error messages, "
            "runtime errors, or unexpected outputs. You MUST:\n"
            "1. Explain the root cause of the error clearly and logically in '### Error Cause & Explanation'.\n"
            "2. Provide the 100% complete corrected code in '### Corrected Code' (no placeholders, ready to compile).\n"
            "3. Provide exact instructions to compile and run in '### How to Recompile & Run'."
        )
    else:
        mode_instruction = "OUTPUT MODE: FULL ANSWER. Include Interpretation, Concepts, Complete Code, Sample Input/Output, and Compile & Run."

    extra = f"Active language/topic: {language}."
    if language == "C":
        extra += f" Target difficulty: Level {c_level}. Compatibility profile: {c_profile}."
    return f"{common}\n\n{lang_prompt}\n\n{extra}\n{mode_instruction}"


def extract_code_block(text: str, language: str) -> str:
    pattern = r"```(?:c|java|sql|C|JAVA|SQL|plsql|PLSQL)?\s*\n(.*?)```"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    if matches:
        return max(matches, key=len).strip() + "\n"
    return text.strip() + "\n"


def check_integrity(text: str, finish_reason: str, language: str = "") -> list[str]:
    warnings = []
    if finish_reason == "length":
        warnings.append("Generation hit max_tokens limit (may be truncated).")
    fence_count = len(re.findall(r"```", text))
    if fence_count % 2 != 0:
        warnings.append("Unclosed markdown code fence detected.")
    code = extract_code_block(text, language)
    if language in ("C", "Java"):
        if code.count("{") != code.count("}"):
            warnings.append(f"Unbalanced braces detected ({{={code.count('{')}, }}={code.count('}')}).")
    return warnings


def read_multiline(prompt_label: str) -> str:
    print(prompt_label)
    print("(Type or paste your question. Enter 'END' on a new line, or press Enter twice to submit.)")
    lines = []
    empty_streak = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        if line == "":
            empty_streak += 1
            if empty_streak >= 2 and lines:
                break
            lines.append(line)
        else:
            empty_streak = 0
            lines.append(line)
    return "\n".join(lines).strip()


def save_output(content: str, language: str, is_code: bool) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    if is_code:
        if language == "C":
            filename = f"program_{ts}.c"
        elif language == "Java":
            filename = f"Main_{ts}.java"
        else:
            filename = f"query_{ts}.sql"
    else:
        prefix = "oracle" if "Oracle" in language else language.lower()
        filename = f"answer_{prefix}_{ts}.md"
    out_path = OUTPUT_DIR / filename
    out_path.write_text(content, encoding="utf-8")
    return out_path


def select_model(models: list[dict], settings: dict) -> dict:
    if len(models) == 1:
        return models[0]
    print("\nAvailable local models:")
    for idx, m in enumerate(models, 1):
        print(f"  {idx}. {m['label']} [{m['size_gb']} GB]")
    choice = input(f"Select model [1-{len(models)}] (Enter for 1): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(models):
        return models[int(choice) - 1]
    return models[0]


def main() -> int:
    print("=" * 60)
    print("   PORTABLE OFFLINE CODING ASSISTANT (C, Java & Oracle SQL)")
    print("=" * 60)

    if not CONFIG_PATH.exists():
        print(f"ERROR: Config file missing: {CONFIG_PATH}")
        return 1

    settings = load_settings()
    models = available_models(settings)
    if not models:
        print(f"ERROR: No valid .gguf models found in {BASE_DIR / 'models'}")
        return 1

    selected_model = select_model(models, settings)
    server = LlamaServerManager(settings)
    atexit.register(server.stop)

    try:
        server.start(selected_model)
    except Exception as exc:
        print(f"\nERROR starting inference engine: {exc}")
        return 1

    c_level = settings["defaults"].get("c_level", 3)
    c_profile = settings["defaults"].get("c_profile", "standard-c")
    gen_cfg = settings["generation"]

    try:
        while True:
            print("-" * 60)
            print("1. C Programming  (Level {}, {})".format(c_level, c_profile))
            print("2. Java Programming")
            print("3. Oracle SQL / PL-SQL")
            print("4. Debug Existing Code / Fix Error (C, Java, SQL)")
            print("5. Configure C Options (Difficulty / Turbo C)")
            print("6. Switch Model")
            print("7. Exit")
            choice = input("Select option [1-7]: ").strip()

            if choice == "7":
                break
            if choice == "6":
                selected_model = select_model(models, settings)
                server.start(selected_model)
                continue
            if choice == "5":
                lvl = input("C Difficulty Level [1-4, current={}]: ".format(c_level)).strip()
                if lvl in ("1", "2", "3", "4"):
                    c_level = int(lvl)
                prof = input("C Profile [1=standard-c, 2=turbo-c, current={}]: ".format(c_profile)).strip()
                if prof == "1":
                    c_profile = "standard-c"
                elif prof == "2":
                    c_profile = "turbo-c"
                continue
            if choice not in ("1", "2", "3", "4"):
                print("Invalid choice.")
                continue

            if choice == "4":
                print("\nSelect language of the code to debug:")
                print("  1. C (GCC / Turbo C)")
                print("  2. Java")
                print("  3. Oracle SQL")
                dbg_lang_choice = input("Choice [1-3, default 1]: ").strip()
                if dbg_lang_choice == "2":
                    language = "Java"
                elif dbg_lang_choice == "3":
                    language = "Oracle SQL"
                else:
                    language = "C"

                print(f"\n[{language} DEBUGGER]")
                print("Paste your code AND the error message / unexpected output below.")
                question = read_multiline("Enter code & error:")
                if not question:
                    print("Empty input, returning to menu.")
                    continue
                mode = "debug"
            else:
                if choice == "1":
                    language = "C"
                elif choice == "2":
                    language = "Java"
                else:
                    language = "Oracle SQL"

                question = read_multiline(f"\n[{language}] Enter your programming question:")
                if not question:
                    print("Empty question, returning to menu.")
                    continue

                mode_in = input("Output mode: [1] Full Answer  [2] Code Only (default 1): ").strip()
                mode = "code_only" if mode_in == "2" else "full"

            history: list[dict] = [
                {"role": "system", "content": build_system_prompt(language, c_level, c_profile, mode)},
                {"role": "user", "content": question},
            ]

            while True:
                print("\n" + "=" * 56)
                try:
                    reply, stats = server.chat_stream(
                        history,
                        max_tokens=gen_cfg.get("max_tokens", 2048),
                        temperature=gen_cfg.get("temperature", 0.2),
                        top_p=gen_cfg.get("top_p", 0.9),
                    )
                except KeyboardInterrupt:
                    print("\n[Generation interrupted]")
                    break
                except Exception as exc:
                    print(f"\nERROR during generation: {exc}")
                    break

                history.append({"role": "assistant", "content": reply})
                print(
                    f"\n[Done in {stats['total_s']}s | first token: {stats['first_token_s']}s | "
                    f"reason: {stats['finish_reason']}]"
                )
                for w in check_integrity(reply, stats["finish_reason"], language):
                    print(f"WARNING: {w}")

                print("\nNext action:")
                print("  1. Ask follow-up / modify code")
                print("  2. Continue truncated output")
                print("  3. Save code to output/")
                print("  4. Save full response to output/")
                print("  5. Back to main menu")
                act = input("Select [1-5]: ").strip()

                if act == "1":
                    followup = read_multiline("\nEnter follow-up instruction:")
                    if not followup:
                        continue
                    history.append({"role": "user", "content": followup})
                elif act == "2":
                    history.append({"role": "user", "content": "Continue from exactly where you stopped without repeating earlier lines."})
                elif act == "3":
                    code = extract_code_block(reply, language)
                    path = save_output(code, language, is_code=True)
                    print(f"Saved code to: {path}")
                elif act == "4":
                    path = save_output(reply, language, is_code=False)
                    print(f"Saved response to: {path}")
                elif act == "5":
                    break
                else:
                    print("Invalid choice, returning to main menu.")
                    break
    finally:
        server.stop()
        print("PortableAI stopped cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
