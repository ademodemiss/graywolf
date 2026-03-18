import pytest
import os
import json
from unittest.mock import MagicMock, patch
from tools.oauth_tool import OAuthTool
from google.oauth2.credentials import Credentials

# Geçici dosyalar için fixture
@pytest.fixture
def temp_oauth_files(tmp_path):
    creds_path = tmp_path / "google_credentials.json"
    token_path = tmp_path / "google_token.json"
    # Sahte credentials.json oluştur (içeriği önemsiz, sadece dosyanın varlığı önemli)
    creds_path.write_text("{}")
    yield str(creds_path), str(token_path)
    if os.path.exists(creds_path):
        os.remove(creds_path)
    if os.path.exists(token_path):
        os.remove(token_path)

@pytest.fixture
def oauth_tool(temp_oauth_files):
    creds_path, token_path = temp_oauth_files
    return OAuthTool(creds_path, token_path)

# Mock Google'ın kimlik doğrulama ve servis oluşturma kısımları
@patch('google.auth.transport.requests.Request')
@patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
def test_authenticate_google_drive_new_token(mock_from_file, mock_flow, mock_request, oauth_tool):
    # Token dosyası yok veya geçersiz -> yeni token akışı
    mock_from_file.return_value = None # Token dosyası yokmuş gibi davran

    mock_creds = MagicMock(spec=Credentials)
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh_token = None
    mock_creds.id_token = {'email': 'test@example.com'}
    mock_creds.to_json.return_value = json.dumps({"token": "new_mock_token"})
    mock_flow.return_value.run_local_server.return_value = mock_creds

    result = oauth_tool.authenticate_google_drive()

    assert result["status"] == "ok"
    assert result["email"] == "test@example.com"
    mock_flow.assert_called_once()
    assert os.path.exists(oauth_tool.token_path) # Token dosyasının oluştuğunu kontrol et

@patch('google.auth.transport.requests.Request')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
def test_authenticate_google_drive_existing_valid_token(mock_from_file, mock_request, oauth_tool):
    # Mevcut geçerli token var
    mock_creds = MagicMock(spec=Credentials)
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.id_token = {'email': 'existing@example.com'}
    mock_from_file.return_value = mock_creds

    result = oauth_tool.authenticate_google_drive()

    assert result["status"] == "ok"
    assert result["email"] == "existing@example.com"
    mock_from_file.assert_called_once()
    mock_creds.refresh.assert_not_called()

@patch('google.auth.transport.requests.Request')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
def test_authenticate_google_drive_expired_token(mock_from_file, mock_request, oauth_tool):
    # Süresi dolmuş token var ve yenilenebilir
    mock_creds = MagicMock(spec=Credentials)
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "mock_refresh_token"
    mock_creds.id_token = {'email': 'expired@example.com'}
    mock_creds.to_json.return_value = json.dumps({"token": "refreshed_mock_token"})
    mock_from_file.return_value = mock_creds

    result = oauth_tool.authenticate_google_drive()

    assert result["status"] == "ok"
    assert result["email"] == "expired@example.com"
    mock_from_file.assert_called_once()
    mock_creds.refresh.assert_called_once_with(mock_request.return_value)
    assert os.path.exists(oauth_tool.token_path) # Token dosyasının güncellendiğini kontrol et

@patch('google.auth.transport.requests.Request')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
def test_authenticate_google_drive_no_credentials_file(mock_from_file, mock_request, oauth_tool):
    # credentials.json dosyası yok
    mock_from_file.return_value = None
    # credentials.json dosyasını test için sil
    os.remove(oauth_tool.credentials_path)

    result = oauth_tool.authenticate_google_drive()

    assert result["status"] == "error"
    assert "credentials.json dosyası bulunamadı" in result["error"]

@patch('googleapiclient.discovery.build')
@patch('google.auth.transport.requests.Request')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
def test_get_google_drive_service(mock_from_file, mock_request, mock_build, oauth_tool):
    mock_creds = MagicMock(spec=Credentials)
    mock_creds.valid = True
    mock_creds.expired = False
    mock_from_file.return_value = mock_creds

    service = oauth_tool.get_google_drive_service()
    assert service is not None
    mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
