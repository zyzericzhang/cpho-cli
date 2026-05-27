from __future__ import annotations

from pathlib import Path


def _format_error(what: str, reason: str, fix: str) -> str:
    return f"[发生了什么] {what}\n[原因] {reason}\n[修复方法] {fix}"


def err_config_missing_api_key(provider_name: str, source: str, config_path: Path | None = None) -> str:
    location = f"配置文件 {config_path}" if config_path is not None else "config.local.yml"
    return _format_error(
        f"provider profile '{provider_name}' 缺少 API key。",
        f"未从环境变量或 {location} 读取到可用密钥；不会在错误信息中打印任何已配置密钥。",
        f"设置 {source}，或在 {location} 中补齐对应 provider 的 api_key/api_key_env。",
    )


def err_api_call_failed(provider_label: str, operation: str, detail: str) -> str:
    return _format_error(
        f"{provider_label} {operation} failed。",
        f"上游 API 返回错误、网络失败或重试后仍不可用：{detail}",
        "检查 provider base_url、模型名、额度和网络；如果是 OpenRouter，优先换更便宜兼容模型重试。",
    )


def err_skill_prompt_missing(skill_dir: Path, step_id: str, prompt_path: Path) -> str:
    return _format_error(
        f"skill step '{step_id}' 引用的 prompt 文件不存在。",
        f"skill.yml 指向 {prompt_path}，但该文件不在 {skill_dir / 'prompts'} 中。",
        f"创建 {prompt_path}，或修改 {skill_dir / 'skill.yml'} 里的 prompt_template。",
    )


def err_knowledge_frontmatter_invalid(path: Path, detail: str) -> str:
    return _format_error(
        f"知识文件 frontmatter 无效：{path}",
        detail,
        "修复文件开头的 YAML frontmatter，至少保留 canonical_tag_id，并确认它存在于 workspace 词表。",
    )


def err_community_sync_failed(subject: str, detail: str) -> str:
    return _format_error(
        f"社区知识库同步失败：{subject}",
        detail,
        "检查 .cpho/community-kb.yml 的 repository URL/tag、GitHub release tarball、网络和知识文件 frontmatter。",
    )

