# probe

## 用途

连续追问学生或教练，帮助定位题目的关键物理点、处理步骤和易错假设。

## 前置条件

- 已选中当前题目。
- 推荐先运行 `/solve`。

## 用法 / 参数

```text
/probe
/set probe.max_rounds 12
```

退出：输入 `/exit` 或连续两次空回答。

## 典型输出

Probe 最终 markdown 前半是所有问题，后半是对应解答。

## 导出文件说明

输出为 `.probe.md`。进行中每轮 Q+A 会先增量写入，退出时再整理为问题/解答分区。

## 端到端完整示例

```text
cpho> /show 1
cpho> /probe
这一步应该先判断什么守恒？
cpho:probe> 动量守恒
cpho:probe> /exit
```

