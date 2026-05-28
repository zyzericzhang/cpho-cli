# err_community_sync_failed

## 发生了什么

社区知识库同步失败。

## 常见原因

`.cpho/community-kb.yml` 的 GitHub URL/tag 不存在，release 没有 tarball，网络失败，或 tarball 内知识文件 frontmatter 无效。

## 修复方法

确认 repository URL 和 tag 固定且可访问；必要时设置 `github_token`；修复 tarball 内知识文件 frontmatter 后重新发布 release。

