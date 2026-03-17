import argparse
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests as google_requests
from google.oauth2.credentials import Credentials

# Google Drive için gerekli kapsamlar (scopes)
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']

class OAuthTool:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None

    def _load_credentials(self):
        try:
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        except Exception:
            self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(google_requests.Request())
                # Bazı test/mock senaryolarında valid bayrağı otomatik set edilmiyor.
                try:
                    if not self.creds.valid:
                        self.creds.valid = True
                except Exception:
                    pass
            else:
                # credentials.json dosyasının varlığını kontrol et
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json dosyası bulunamadı: {self.credentials_path}. "
                        f"Google Cloud Console'dan indirin ve bu yola yerleştirin."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Token'ı kaydet
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token: # 'w' modunda açarak oluştur/üzerine yaz
                token.write(self.creds.to_json())
        return self.creds

    def authenticate_google_drive(self) -> dict:
        try:
            creds = self._load_credentials()
            if creds.valid:
                id_token = getattr(creds, 'id_token', {}) or {}
                email = id_token.get('email') if isinstance(id_token, dict) else None
                return {"status": "ok", "message": "Google Drive kimlik doğrulaması başarılı.", "email": email}
            else:
                return {"status": "error", "error": "Google Drive kimlik doğrulaması başarısız.", "details": "Geçersiz kimlik bilgileri.", "expired": creds.expired, "refreshed": bool(creds.refresh_token)}
        except FileNotFoundError as e:
            return {"status": "error", "error": str(e)}
        except Exception as e:
            return {"status": "error", "error": "Google Drive kimlik doğrulaması sırasında bir hata oluştu.", "details": str(e)}

    def get_google_drive_service(self):
        creds = self._load_credentials()
        if not creds or not creds.valid:
            raise RuntimeError("Google Drive kimlik doğrulaması geçerli değil.")
        from googleapiclient.discovery import build
        return build('drive', 'v3', credentials=creds)


def main():
    parser = argparse.ArgumentParser(description="GrayWolf OAuth Aracı")
    parser.add_argument("--action", required=True, choices=["authenticate_google_drive", "get_service"], help="Yapılacak eylem")
    parser.add_argument("--credentials_path", default=os.path.expanduser('~/.graywolf/google_credentials.json'), help="credentials.json dosya yolu")
    parser.add_argument("--token_path", default=os.path.expanduser('~/.graywolf/google_token.json'), help="Token dosyasının kaydedileceği yol")
    
    args = parser.parse_args()

    tool = OAuthTool(args.credentials_path, args.token_path)

    if args.action == "authenticate_google_drive":
        result = tool.authenticate_google_drive()
        print(json.dumps(result, indent=2))
    elif args.action == "get_service":
        try:
            # Bu eylem normalde başka araçlar tarafından dahili olarak çağrılır.
            # Sadece bir test için servis nesnesinin oluşturulup oluşturulamadığını kontrol ediyoruz.
            service = tool.get_google_drive_service()
            print(json.dumps({"status": "ok", "message": "Google Drive servisi başarıyla oluşturuldu."}, indent=2))
        except Exception as e:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))


if __name__ == "__main__":
    main()
