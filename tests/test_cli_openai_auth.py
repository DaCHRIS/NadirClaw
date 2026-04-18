"""Tests for openai auth CLI semantics around browser vs headless mode."""

from click.testing import CliRunner

from nadirclaw.cli import main


def _patch_openai_auth_deps(monkeypatch, *, token_data):
    monkeypatch.setattr("nadirclaw.credentials.get_credential", lambda provider: None)
    monkeypatch.setattr("nadirclaw.credentials.get_credential_source", lambda provider: None)
    monkeypatch.setattr("nadirclaw.credentials._read_credentials", lambda: {})
    monkeypatch.setattr("nadirclaw.credentials.save_oauth_credential", lambda *args, **kwargs: None)
    captured = {}

    def _fake_login_openai(timeout=300, auth_mode="browser"):
        captured["timeout"] = timeout
        captured["auth_mode"] = auth_mode
        return token_data

    monkeypatch.setattr("nadirclaw.oauth.login_openai", _fake_login_openai)
    return captured


def test_openai_login_headless_mode_message_and_auth_mode(monkeypatch):
    captured = _patch_openai_auth_deps(
        monkeypatch,
        token_data={"access_token": "tok-1234567890", "refresh_token": "ref-1", "expires_at": 9999999999},
    )
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "openai", "login", "--headless", "--timeout", "123"])
    assert result.exit_code == 0
    assert captured["auth_mode"] == "headless"
    assert captured["timeout"] == 123
    assert "Headless mode: complete login in a browser and paste the final redirect URL here." in result.output
    assert "A browser window will open" not in result.output


def test_openai_login_browser_mode_message_and_auth_mode(monkeypatch):
    captured = _patch_openai_auth_deps(
        monkeypatch,
        token_data={"access_token": "tok-1234567890", "refresh_token": "ref-1", "expires_at": 9999999999},
    )
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "openai", "login", "--timeout", "45"])
    assert result.exit_code == 0
    assert captured["auth_mode"] == "browser"
    assert captured["timeout"] == 45
    assert "A browser window will open for you to sign in with your OpenAI account." in result.output
