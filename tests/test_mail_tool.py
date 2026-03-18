import os
import pytest
import json
import datetime
from tools.mail_tool import MailTool

@pytest.fixture
def mail_draft_dir(tmp_path):
    # Geçici bir mail taslak dizini oluştur
    draft_path = tmp_path / "mail_drafts"
    draft_path.mkdir()
    yield str(draft_path)

def test_create_draft(mail_draft_dir):
    tool = MailTool(draft_dir=mail_draft_dir)
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test Body"
    result = tool.create_draft(to, subject, body)

    assert result["status"] == "draft_created"
    assert "draft_id" in result
    assert "path" in result
    assert os.path.exists(result["path"])

    with open(result["path"], "r", encoding="utf-8") as f:
        draft_data = json.load(f)
    assert draft_data["to"] == to
    assert draft_data["subject"] == subject
    assert draft_data["body"] == body
    assert draft_data["status"] == "draft"

def test_confirm_draft(mail_draft_dir):
    tool = MailTool(draft_dir=mail_draft_dir)
    create_result = tool.create_draft("test@example.com", "Sub", "Body")
    draft_id = create_result["draft_id"]

    confirm_result = tool.confirm_draft(draft_id, approved=True)
    assert confirm_result["status"] == "draft_confirmed"
    assert confirm_result["approved"] is True

    with open(create_result["path"], "r", encoding="utf-8") as f:
        draft_data = json.load(f)
    assert draft_data["status"] == "approved"

def test_confirm_non_existent_draft(mail_draft_dir):
    tool = MailTool(draft_dir=mail_draft_dir)
    result = tool.confirm_draft("non_existent_id", approved=True)
    assert result["status"] == "error"
    assert result["error"] == "draft_not_found"

# send_draft metodunu test etmek için harici SMTP sunucusuna ihtiyaç duyarız.
# Bu, duman testi için karmaşık olduğundan atlıyoruz.
