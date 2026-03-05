import os

from tools.terminal_tool import TerminalTool
from policies.shell_policy import ShellPolicy

if __name__ == "__main__":
    policy = ShellPolicy()
    terminal_tool = TerminalTool(policy_engine=policy, log_dir=os.path.expanduser('~/graywolf/logs/'))

    # py_compile komutunu TerminalTool üzerinden çalıştır
    compile_command = "python3 -m py_compile /home/adem/graywolf/temp_gemini_test.py"
    print(f"--- py_compile komutu çalıştırılıyor: {compile_command} ---")
    result = terminal_tool.run_command(compile_command)
    print(f"Komut Çıktısı: {result.get('stdout')}")
    print(f"Hata Çıktısı: {result.get('stderr')}")
    print(f"Durum: {result.get('status')}")

    # Log kaydını buradan doğrudan göstermiyoruz, TerminalTool içine yazacak.
