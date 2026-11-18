# Target College PC Checklist

Run `DIAGNOSTICS.bat` on the college PC first and record the results below:

- [ ] Windows version (10/11) and x64 architecture verified
- [ ] Available RAM (~16 GB expected) verified
- [ ] `runtime\python\python.exe` allowed to execute
- [ ] `engine\llama-server.exe` allowed to execute
- [ ] Model file(s) visible in `models\`
- [ ] `output\` and `logs\` writable
- [ ] Java version (`java -version`, `javac -version`) recorded
- [ ] C compiler (`gcc` or Turbo C) availability recorded
- [ ] Offline test passed (model loads, generates C and Java, code compiles)

If `llama-server.exe` or `python.exe` is blocked by college endpoint security, **do not bypass**. Record the exact error message and ask college IT for an approved folder/runtime.
