# 复现框架说明

当前项目已经加入一个最小可用、零额外依赖的复现框架，用于复现侦探推理 baseline，并观察不同模型和推理方法的输出。

## 入口命令

列出支持的数据集：

```bash
python3 -m src.detective_reasoning.cli list-datasets
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

## 输出文件

批量评测会输出：

- 每条样本一行的 JSONL 结果
- 汇总准确率、解析错误和 token 用量的 CSV

默认输出目录：

```text
outputs/
```

该目录已被 git ignore，不会提交到 GitHub。

