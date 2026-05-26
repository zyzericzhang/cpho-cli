from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace

import pytest

from cpho_cli.cli.repl.commands import set_cmd
from cpho_cli.cli.repl.commands import Command, registry
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.llm import LLMProviderError
from cpho_cli.models.config import AppConfig, ProviderProfile
from cpho_cli.models.llm import ModelCapabilities


async def _handler(session: object, args: list[str]) -> None:
    calls = getattr(session, "calls", 0)
    setattr(session, "calls", calls + 1)


def test_command_defaults_and_registry_empty() -> None:
    cmd = Command(name="/x", help="h", usage="u", handler=_handler)

    assert cmd.completer is None
    assert cmd.category == "其他"
    assert registry == {}


@pytest.mark.asyncio
async def test_registered_command_handler_invokes() -> None:
    local = {"/x": Command(name="/x", help="h", usage="u", handler=_handler)}
    session = SimpleNamespace()

    await local["/x"].handler(session, [])

    assert getattr(session, "calls") == 1


def test_command_is_mutable_and_prompt_toolkit_lazy() -> None:
    cmd = Command(name="/x", help="h", usage="u", handler=_handler)

    cmd.help = "新"

    assert cmd.help == "新"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import cpho_cli.cli.repl.commands; "
            "assert 'prompt_toolkit' not in sys.modules",
        ],
        check=True,
    )
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_set_provider_refreshes_model_capabilities(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(
            providers={
                "backup": ProviderProfile(
                    kind="openrouter",
                    api_key="sk-test",
                    default_model="test/multimodal",
                )
            }
        ),
    )
    calls = {}

    def fake_create_llm_provider(kind, api_key, base_url, *, timeout):  # type: ignore[no-untyped-def]
        calls["provider"] = (kind, api_key, base_url, timeout)
        return object()

    def fake_detect(provider, model_name):  # type: ignore[no-untyped-def]
        calls["model_name"] = model_name
        return ModelCapabilities(input_modalities={"text", "file"})

    monkeypatch.setattr(set_cmd, "create_llm_provider", fake_create_llm_provider)
    monkeypatch.setattr(set_cmd, "detect_model_capabilities", fake_detect)

    await set_cmd.do_set(session, ["provider", "backup"])

    assert session.provider_name == "backup"
    assert session.config.model.name == "test/multimodal"
    assert session.model_capabilities.supports_file
    assert calls["model_name"] == "test/multimodal"


@pytest.mark.asyncio
async def test_set_provider_capability_failure_warns_and_falls_back(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    session = SessionState(
        workspace_path=tmp_path,
        config=AppConfig(
            providers={
                "backup": ProviderProfile(
                    kind="openrouter",
                    api_key="sk-test",
                    default_model="test/text",
                )
            }
        ),
    )

    monkeypatch.setattr(
        set_cmd,
        "create_llm_provider",
        lambda *args, **kwargs: object(),
    )

    def fail_detect(provider, model_name):  # type: ignore[no-untyped-def]
        raise LLMProviderError("metadata unavailable")

    monkeypatch.setattr(set_cmd, "detect_model_capabilities", fail_detect)

    await set_cmd.do_set(session, ["provider", "backup"])

    assert session.provider_name == "backup"
    assert session.model_capabilities == ModelCapabilities()
    assert "模型能力检测失败" in capsys.readouterr().out
