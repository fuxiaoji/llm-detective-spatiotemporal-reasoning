# 复现框架说明

当前项目已经加入一个模块化、零额外依赖的复现实验框架，用于复现侦探推理 baseline、测试可插拔 skill，并保存可审计的实验记录。

## 入口命令

列出支持的数据集：

```bash
python3 -m src.detective_reasoning.cli list-datasets
```

列出支持的方法和 skill：

```bash
python3 -m src.detective_reasoning.cli list-methods
python3 -m src.detective_reasoning.cli list-skills
```

查看统一格式样本：

```bash
python3 -m src.detective_reasoning.cli peek --dataset musr --split murder_mystery --limit 2
python3 -m src.detective_reasoning.cli peek --dataset detectbench --split test-hard --limit 2
```

使用 mock 模型跑批量评测：

```bash
python3 -m src.detective_reasoning.cli eval \
  --dataset musr \
  --split murder_mystery \
  --method cot \
  --skills dummy_skill \
  --provider mock \
  --model mock \
  --limit 10
```

使用 OpenAI-compatible 模型：

```bash
OPENAI_API_KEY=... python3 -m src.detective_reasoning.cli eval \
  --dataset detectbench \
  --split test-hard \
  --method evidence_card \
  --skills external_evidence_bank,structured_memory_stub \
  --provider openai \
  --model gpt-4o-mini \
  --limit 20
```

启动本地网页 demo：

```bash
python3 -m src.detective_reasoning.demo_server
```

然后打开：

```text
http://127.0.0.1:8765
```

## 已支持数据集

- MuSR：`murder_mystery`, `object_placements`, `team_allocation`
- DetectBench：`train`, `dev`, `test`, `test-hard`, `test-distract`
- DetectiveQA 标注：`en_human`, `en_ai`, `zh_human`, `zh_ai`
- TurnaboutLLM：`AA`, `DR`

## 已支持推理方法

- `direct`：直接回答
- `cot`：普通 Chain-of-Thought
- `reflection`：回答后自我检查
- `evidence_card`：先整理轻量证据卡再回答
- `critic_checklist`：先生成答案，再用 checklist 检查和修正

## 已支持 Skill

- `dummy_skill`：无实际效果的测试 skill，用于确认注册表和 GUI 可识别新组件。
- `external_evidence_bank`：把已有结构化证据和 reasoning 标注附加到 prompt。
- `structured_memory_stub`：要求模型先建立临时时间线、地点、实体、证据记忆，再回答。

新的工具 / skill 可以注册到 `src/detective_reasoning/registry.py`。

## 保存文件

GUI 单题测试和 CLI 批量评测都会输出：

- `manifest.json`：run id、运行配置、时间戳和汇总结果。
- `predictions.jsonl`：每条样本一行，包含 prompt、模型可见输出、工具 trace、prediction、gold answer、correct、parse error 和 token 用量。
- `summary.csv`：准确率、解析错误和 token 用量汇总。

默认保存目录：

```text
runs/<run_id>/
```

该目录已被 git ignore，不会提交到 GitHub。这里保存的“思考过程”只包括模型实际返回的可见文本和工具中间结果，不包含隐藏链路。

## GUI

本地网页 GUI 支持选择数据集 / split、样本编号、模型、推理方法和 skill，并会保存每次运行记录。启动方式：

```bash
python3 -m src.detective_reasoning.demo_server
```
