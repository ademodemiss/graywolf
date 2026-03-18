import os
import sys

from tools.terminal_tool import TerminalTool
from policies.shell_policy import ShellPolicy
from adapters.llm.gemini_adapter import GeminiAdapter

# Ortam değişkenini manuel olarak ayarlamanız gerekebilir
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

if __name__ == "__main__":
    # Policy Engine'ı başlat
    policy = ShellPolicy()
    # TerminalTool'u başlat (policy_engine ve log_dir ile)
    terminal_tool = TerminalTool(policy_engine=policy, log_dir=os.path.expanduser('~/graywolf/logs/'))

    # Gemini Adapter'ı başlat
    try:
        llm_adapter = GeminiAdapter()
    except ValueError as e:
        print(f"LLM Adaptörü Başlatılırken Hata: {e}")
        sys.exit(1)

    # Gemini Adapter üzerinden bir prompt gönder
    print("--- Gemini Adapter aracılığıyla prompt gönderiliyor ---")
    prompt_text = "GrayWolf projesi nedir? Kısaca açıklar mısın?"
    response_text = llm_adapter.generate_response(prompt_text)
    print(f"LLM Yanıtı: {response_text}")

    # Bu LLM çağrısını TerminalTool üzerinden simüle etmenin
    # doğrudan bir yolu yoktur, çünkü TerminalTool dış komutları çalıştırır.
    # Ancak, bu betiği çalıştıran Python komutunu loglayabiliriz.
    print("--- TerminalTool üzerinden Python komutu loglanıyor ---")
    python_command = f"/home/adem/graywolf/venv/bin/python {os.path.expanduser('~/graywolf/temp_gemini_test.py')}" # Bu betiği çalıştıran komut
    
    # Bu simülasyon TerminalTool'un dış komut loglamasını gösterecektir
    # Kendi içinde LLM çağrısı yapan bir betiği TerminalTool ile çalıştırmak.
    # Bu, asıl entegrasyonu göstermez, sadece TerminalTool'un yeteneğini gösterir.
    
    # Gerçek entegrasyon Orchestrator katmanında gerçekleşecektir.
    # Şimdilik, sadece LLM adaptörünün çalıştığını doğrulamak için manuel test yapıyoruz.
