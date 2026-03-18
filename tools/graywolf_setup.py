import os
import json

# Yapılandırma dosyasının yolu
ENV_FILE = os.path.expanduser("~/graywolf/.env")

def get_user_input(prompt: str, default: str = "") -> str:
    """Kullanıcıdan girdi almak için kullanılır. Varsayılan değer belirtebilir.
    exec aracıyla kullanıldığında, bu fonksiyon etkileşimli olacaktır.
    """
    # Bu kısım, exec aracı tarafından yakalanacak ve kullanıcının girdisi olarak iletilecek.
    # Bu yüzden burada doğrudan input() çağırmak yerine, aracın bu girdiyi sağlamasını bekliyoruz.
    # Eğer araç girdi sağlamazsa, bu fonksiyon boş dönebilir veya hata verebilir.
    # Şimdilik, araçtan gelecek girdiyi temsil edecek bir yer tutucu döndürelim.
    # Gerçekte, araç bu prompt'u kullanıcıya gösterip cevabı alacak.
    # Bu simülasyonda, ben sizden bilgileri alacağım ve betiği oluşturacağım.
    return ""

def setup_graywolf():
    print("GrayWolf Kurulum Sihirbazına Hoş Geldiniz!")
    print("Bu süreç, GrayWolf'u ihtiyaçlarınıza göre yapılandırmanıza yardımcı olacaktır.")
    print("-" * 30)

    config = {}

    # --- API Anahtarları ---
    print("\n--- API Yapılandırmaları ---")
    print("Lütfen kullanmak istediğiniz API anahtarlarını girin. Atlamak için boş bırakın.")

    openai_key = input("OpenAI API Anahtarınız (eğer varsa): ")
    if openai_key:
        config["OPENAI_API_KEY"] = openai_key

    google_key = input("Google API Anahtarınız (eğer varsa): ")
    if google_key:
        config["GOOGLE_API_KEY"] = google_key

    # --- LLM Model Tercihi ---
    print("\n--- LLM Yapılandırması ---")
    print("GrayWolf'un hangi LLM modelini kullanmasını tercih edersiniz?")
    print("Seçenekler: openai, gemini, auto, none")
    print("auto seçeneği, mevcut API anahtarlarınıza göre en uygun modeli otomatik seçecektir.")
    llm_model = input("Tercih ettiğiniz LLM modelini girin (örn. 'gemini', boş bırakın): ").lower()
    if llm_model:
        config["LLM_MODEL_PREFERENCE"] = llm_model
    elif not openai_key and not google_key:
        config["LLM_MODEL_PREFERENCE"] = "none" # Eğer hiç anahtar girilmediyse
    elif not llm_model: # Eğer model seçimi boş bırakıldıysa otomatik seçimi tetikle
        # Otomatik seçim mantığı (basit): OpenAI varsa OpenAI, yoksa Gemini varsa Gemini, yoksa none
        if openai_key: 
            config["LLM_MODEL_PREFERENCE"] = "openai"
        elif google_key: 
            config["LLM_MODEL_PREFERENCE"] = "gemini"
        else:
            config["LLM_MODEL_PREFERENCE"] = "none"


    # --- Bildirim Ayarları ---
    print("\n--- Bildirim Yapılandırmaları (Telegram) ---")
    print("Bildirim almak için Telegram Chat ID ve Bot Token girin.")
    print("Chat ID'nizi almak için @userinfobot gibi botları kullanabilirsiniz.")
    print("Bot Token'ınızı @BotFather ile oluşturabilirsiniz.")

    telegram_id = input("Telegram Chat ID (boş bırakın): ")
    if telegram_id:
        config["TELEGRAM_CHAT_ID"] = telegram_id

    telegram_token = input("Telegram Bot Token'ınız (boş bırakın): ")
    if telegram_token:
        config["TELEGRAM_BOT_TOKEN"] = telegram_token

    # --- Etkinleştirilecek Yetenekler/Araçlar ---
    print("\n--- Yetenek Seçimi ---")
    print("GrayWolf'un hangi temel yetenekleri etkinleştirmesini istersiniz?")
    print("Seçenekler (virgülle ayırarak): coding, finance, terminal, excel, mail, all")
    enabled_capabilities = input("Etkinleştirmek istediklerinizi girin (örn. 'coding,terminal'): ").lower()
    if enabled_capabilities:
        config["ENABLED_CAPABILITIES"] = enabled_capabilities

    # --- Yapılandırmayı .env dosyasına kaydetme ---
    env_content = ""
    if config:
        for key, value in config.items():
            # Güvenlik için değerleri tırnak içine alalım
            env_content += f"{key}='{value}'\n"
    else:
        # Eğer hiç config girilmediyse, en azından bir yorum satırı ekle
        env_content = "# GrayWolf configuration\n"

    try:
        os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
        with open(ENV_FILE, "w") as f:
            f.write(env_content)
        print(f"\nGrayWolf yapılandırması başarıyla {ENV_FILE} dosyasına kaydedildi.")
    except Exception as e:
        print(f"\nGrayWolf yapılandırması kaydedilirken hata oluştu {ENV_FILE}: {e}")

    print("\nGrayWolf kurulum sihirbazı tamamlandı. Ayarlarınız yapılandırıldı.")
    print("Şimdi GrayWolf'u başlatmaya hazırsınız.")

if __name__ == "__main__":
    setup_graywolf()
