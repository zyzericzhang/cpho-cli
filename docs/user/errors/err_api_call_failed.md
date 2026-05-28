# err_api_call_failed

## 发生了什么

模型 provider 的 request 或 stream 调用失败。

## 常见原因

上游 API 返回错误、网络不可用、模型名不兼容、额度不足，或 base URL 配错。

## 修复方法

检查 `config.local.yml` 的 provider、模型名、额度和网络。OpenRouter 失败时，优先换兼容且更便宜的模型重试。

