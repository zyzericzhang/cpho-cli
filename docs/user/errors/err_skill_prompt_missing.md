# err_skill_prompt_missing

## 发生了什么

`skill.yml` 中某个 step 引用的 prompt 文件不存在。

## 常见原因

`prompt_template` 写错、文件未随 skill 提交，或 prompt 被移动后没有更新配置。

## 修复方法

创建错误信息中给出的 prompt 文件，或修改 `skill.yml` 里的 `prompt_template` 指向实际文件。

