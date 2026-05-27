# err_config_missing_api_key

## 发生了什么

指定 provider profile 没有可用 API key。

## 常见原因

环境变量未设置，或 `config.local.yml` 中的 `providers.<name>.api_key` / `api_key_env` 没填。

## 修复方法

在环境变量中设置提示的 key，或在本地配置文件补齐对应 provider。不要把真实 key 提交到 Git。

