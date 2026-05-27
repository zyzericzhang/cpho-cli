# community-kb

## 用途

同步公开社区知识库到本机只读 cache，并让 `knowledge find`、`/explain` 在私有知识之后读取这些资料。

## 前置条件

- workspace 已有 `.cpho/vocabulary/private.yml` 或内置词表中能识别社区文件的 `canonical_tag_id`。
- 社区知识库以 GitHub release 发布，并固定 tag。
- 配置文件默认放在 `<workspace>/.cpho/community-kb.yml`。

## 用法 / 参数

```bash
uv run cpho knowledge sync --workspace /path/to/workspace
uv run cpho knowledge sync --workspace /path/to/workspace --config /path/to/community-kb.yml --force
```

配置格式：

```yaml
repositories:
  - url: https://github.com/owner/repo
    tag: v1.0.0
    enabled: true
github_token: null
```

- `url`: GitHub repository URL。
- `tag`: 固定 release tag；不会跟随 latest。
- `enabled`: 设为 `false` 时跳过。
- `github_token`: 可选，只用于读取 GitHub release 和 tarball。
- `--cache-dir`: 覆盖默认 cache 目录，测试时常用。
- `--force`: 同一个 repo/tag 已同步时也重新下载。

## 典型输出

```text
已同步: example-kb@v1.0.0 -> /Users/you/.cache/cpho/community-kb/example-kb (3 files)
```

如果同一个 repo/tag 已存在且没有 `--force`：

```text
跳过: example-kb@v1.0.0 -> /Users/you/.cache/cpho/community-kb/example-kb (3 files)
```

## 导出文件说明

- 默认 cache: `~/.cache/cpho/community-kb/<repo-name>/`
- 每个 repo cache 中包含同步出的 `.md/.markdown/.tex/.txt/.rst` 知识文件。
- `metadata.json` 记录 `url`、`tag`、`synced_at` 和文件数。
- 同步完成后 cache 会被设为只读。命令不会写入 `<workspace>/.cpho/knowledge/files/`。

解析优先级：

1. 私有知识：`<workspace>/.cpho/knowledge/files/` 和 `published/`
2. 社区知识：`~/.cache/cpho/community-kb/`

测试或临时环境可以设置：

```bash
export CPHO_COMMUNITY_KB_DIR=/tmp/cpho-community-kb
```

## 端到端完整示例

```bash
cat > /Users/you/物理竞赛资料/.cpho/community-kb.yml <<'YAML'
repositories:
  - url: https://github.com/owner/cpho-community-kb
    tag: v1.0.0
    enabled: true
YAML

uv run cpho knowledge sync --workspace /Users/you/物理竞赛资料
uv run cpho knowledge find problem-001 --workspace /Users/you/物理竞赛资料
```

`knowledge find` 输出 `community` 时，说明匹配来自社区 cache；如果同一 tag 有私有知识，私有知识排在前面。
