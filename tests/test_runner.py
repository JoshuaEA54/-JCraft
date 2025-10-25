from lang.interpreter import run_source

with open("test_menu.jcraft", "r", encoding="utf-8") as f:
    code = f.read()

try:
    out = run_source(code, input_callback=lambda p: "1", debug=True)
    print("RESULTS:", out)
except Exception as e:
    print(f"ERROR: {e}")
