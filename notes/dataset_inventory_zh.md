# 侦探推理数据集清点报告

更新日期：2026-06-26

## 总结

本文档整理当前项目中与侦探推理相关的数据集，用于后续研究：

> 外部结构化证据记忆 / skill-assisted test-time reasoning 是否能提升 LLM 在侦探推理任务中的表现。

本阶段只覆盖侦探和叙事推理资源：

- MuSR
- DetectBench
- DetectiveQA
- TurnaboutLLM
- LLM Mysteries

空间导航、具身智能和时空记忆类数据集暂不纳入第一阶段，避免研究范围过重。

## 总览

| 论文 / 项目 | 数据集 | 是否开源 | 本地状态 | 推荐用途 |
|---|---|---:|---|---|
| MuSR | murder mystery / object placements / team allocation | 是 | 已下载，可读取 | 凶手推理准确率主实验 |
| DetectBench | DetectBench English v1.3 | 是 | 已下载，可读取 | 隐含证据发现主实验 |
| DetectiveQA | DetectiveQA annotations | 是，HuggingFace | 标注 JSON 已下载；当前文件未包含完整小说正文 | 长上下文定性案例，需后续确认正文来源 |
| TurnaboutLLM | Ace Attorney + Danganronpa contradiction dataset | 是 | 核心 JSON 可读；source/eval 已补齐 | 证据-证词矛盾实验 |
| LLM Mysteries | mystery-solving reference code + small task data | 是 | 仓库已下载，可读 | belief graph / evidence graph demo 参考 |

## 1. MuSR

### 来源

- 论文：`papers/2310.16049_MuSR_Multistep_Soft_Reasoning.pdf`
- GitHub：`https://github.com/Zayne-sprague/MuSR`
- 本地路径：`data/MuSR/`

### 本地数据

| 文件 | 数量 | 用途 |
|---|---:|---|
| `data/MuSR/datasets/murder_mystery.json` | 250 | 侦探凶手判断主实验 |
| `data/MuSR/datasets/object_placements.json` | 64 | 空间 / 物品状态追踪辅助实验 |
| `data/MuSR/datasets/team_allocation.json` | 250 | 社会关系推理辅助实验 |

### 数据结构

```text
[
  {
    "context": str,
    "questions": [
      {
        "question": str,
        "answer": int,
        "choices": list[str],
        "intermediate_trees": list,
        "intermediate_data": ...
      }
    ]
  }
]
```

统一字段映射：

| 统一字段 | 来源 |
|---|---|
| `id` | 文件名 + 样本序号生成 |
| `context` | `context` |
| `question` | `questions[0].question` |
| `options` | `questions[0].choices` |
| `answer` | `questions[0].answer` |
| `evidence` | 无直接标注，可从 `intermediate_trees` 派生 |
| `reasoning` | `intermediate_trees`, `intermediate_data` |
| `metadata` | domain 名称、原始序号 |

### 样例

来自 `murder_mystery.json`：

```text
Context: In an adrenaline inducing bungee jumping site, Mack's thrill-seeking adventure came to a gruesome end by a nunchaku...
Question: Who is the most likely murderer?
Choices: ["Mackenzie", "Ana"]
Answer index: 0
```

### 可用性

| 评估目标 | 适配度 |
|---|---|
| 最终答案准确率 | 强 |
| 证据覆盖率 | 中，需要处理 intermediate tree |
| 推理步骤评估 | 中 |
| 矛盾检测 | 弱 |
| 长上下文案例 | 弱 |

### 建议

MuSR murder mystery 应作为第一阶段主 benchmark。它小、干净、已在本地，适合快速比较 Direct、CoT、Reflection、Self-Consistency 和轻量证据卡方法。

## 2. DetectBench

### 来源

- 论文：`papers/2406.12641_DetectBench.pdf`
- GitHub：`https://github.com/MikeGu721/DetectBench`
- ACL 数据：`https://aclanthology.org/2024.findings-emnlp.11.data.zip`
- 本地路径：`data/DetectBench/`

### 本地数据

| 文件 | 数量 | 说明 |
|---|---:|---|
| `data/DetectBench/DetectBench_eng_v1.3/train.jsonl` | 367 | 训练集 |
| `data/DetectBench/DetectBench_eng_v1.3/dev.jsonl` | 1764 | 开发集 |
| `data/DetectBench/DetectBench_eng_v1.3/test.jsonl` | 1196 | 普通测试集 |
| `data/DetectBench/DetectBench_eng_v1.3/test-hard.jsonl` | 300 | 难题集，证据更多、逻辑跳跃更深 |
| `data/DetectBench/DetectBench_eng_v1.3/test-distract.jsonl` | 300 | 长上下文干扰集 |

### 数据结构

大多数 split：

```text
{
  "id": int,
  "context": str,
  "question": str,
  "options": list[str],
  "answer": int,
  "clue_graph": {
    "evidence": str,
    "multi_hop_reasoning": str
  }
}
```

`test-distract.jsonl` 略有不同：

```text
{
  "context": str,
  "question": str,
  "options": list[str],
  "answer": int,
  "reasoning_process": {
    "evidence": ...,
    ...
  }
}
```

统一字段映射：

| 统一字段 | 来源 |
|---|---|
| `id` | `id`，或为 `test-distract` 自动生成 |
| `context` | `context` |
| `question` | `question` |
| `options` | `options` |
| `answer` | `answer` |
| `evidence` | `clue_graph.evidence` 或 `reasoning_process.evidence` |
| `reasoning` | `clue_graph.multi_hop_reasoning` 或 `reasoning_process` |
| `metadata` | split 名称、数据版本 |

### 样例

来自 `test-hard.jsonl`：

```text
Question: How can you divide 24 pounds of oil into three equal parts using containers of 5, 11, and 13 pounds?
Answer index: 0
Evidence: 24 jin of oil -> Fill the 13 jin container -> Remaining 11 jin of oil ...
```

### 可用性

| 评估目标 | 适配度 |
|---|---|
| 最终答案准确率 | 强 |
| 证据覆盖率 | 强 |
| 推理步骤评估 | 强 |
| 矛盾检测 | 弱到中 |
| 长上下文案例 | 中，尤其是 `test-distract` |

### 建议

DetectBench 应作为第一阶段的证据发现 benchmark。`test-hard.jsonl` 特别适合测试 evidence card、critic checklist 是否能提升关键证据识别和多跳推理。

## 3. DetectiveQA

### 来源

- 论文：`papers/2409.02465_DetectiveQA.pdf`
- GitHub 脚本：`https://github.com/Phospheneser/DetectiveQA`
- HuggingFace 数据集：`https://huggingface.co/datasets/Phospheneser/DetectiveQA`
- 本地仓库：`data/DetectiveQA/`
- 本地 HF 标注：`data/DetectiveQA/hf_dataset/`

### 本地状态

GitHub 仓库主要包含 README 和评估脚本，不含真实数据。HuggingFace 数据集是公开且非 gated 的，标注 JSON 已下载到：

```text
data/DetectiveQA/hf_dataset/
```

下载到的标注数量：

| 文件夹 | 文件数 | 问题数 | 说明 |
|---|---:|---:|---|
| `anno_data_en/AIsup_anno` | 62 | 446 | 英文 AI 辅助标注 |
| `anno_data_en/human_anno` | 24 | 154 | 英文人工标注 |
| `anno_data_zh/AIsup_anno` | 62 | 446 | 中文 AI 辅助标注 |
| `anno_data_zh/human_anno` | 24 | 154 | 中文人工标注 |

重要限制：

当前下载的 JSON 包含问题、选项、答案、推理步骤、线索位置和答案位置，但没有直接包含完整小说正文。如果要完整复现长上下文问答，还需要继续确认原文获取方式或官方脚本的数据准备流程。

### 数据结构

每个文件通常是一个只含一个 novel-level object 的 list：

```text
[
  {
    "novel_id": int,
    "num_paragraphs": int,
    "time_cost": ...,
    "questions": [
      {
        "question": str,
        "options": dict[str, str],
        "answer": "A" | "B" | "C" | "D",
        "distraction": dict,
        "reasoning": list[str],
        "clue_position": ...,
        "answer_position": ...
      }
    ]
  }
]
```

统一字段映射：

| 统一字段 | 来源 |
|---|---|
| `id` | novel id + question index |
| `context` | 当前标注文件中不存在 |
| `question` | `questions[].question` |
| `options` | `questions[].options` |
| `answer` | `questions[].answer` |
| `evidence` | `questions[].reasoning` + `clue_position` |
| `reasoning` | `questions[].reasoning` |
| `metadata` | 语言、标注类型、novel id、paragraph count |

### 样例

来自 `anno_data_en/human_anno/117.json`：

```text
Question: Aveline instructed Polo not to tell anyone when she left, which implies that:
Options: A rendezvous / swim at the beach / buy clothes / enjoys being alone
Answer: A
Reasoning: multiple reference steps explaining the hidden relationship and motive for secrecy.
```

### 可用性

| 评估目标 | 适配度 |
|---|---|
| 最终答案准确率 | 中，需要上下文正文 |
| 证据覆盖率 | 强，可用 reference reasoning |
| 推理步骤评估 | 强 |
| 矛盾检测 | 中 |
| 长上下文案例 | 强，但需先补正文 |

### 建议

DetectiveQA 放在第二阶段，用于长上下文定性案例和 reasoning-step 评估。第一阶段不建议作为主 benchmark，除非先解决完整小说正文获取问题。

## 4. TurnaboutLLM

### 来源

- GitHub：`https://github.com/zharry29/turnabout_llm`
- 本地路径：`data/TurnaboutLLM/`

### 本地文件

| 文件 | 数量 / 状态 | 用途 |
|---|---:|---|
| `data/TurnaboutLLM/data/AA_integrated_dataset.json` | 200 | Ace Attorney 矛盾样本 |
| `data/TurnaboutLLM/data/DR_integrate_dataset.json` | 31 | Danganronpa 矛盾样本 |
| `data/TurnaboutLLM/source/run_models.py` | 存在 | 模型推理脚本 |
| `data/TurnaboutLLM/source/evaluate.py` | 存在 | 评估脚本 |
| `data/TurnaboutLLM/eval/*_report.json` | 26 个报告 | 已有模型评测结果 |
| `data/TurnaboutLLM/eval/eval.csv` | 存在 | 聚合评估表 |

`source/` 和 `eval/` 已从 `data/repo_zips/TurnaboutLLM.zip` 补解。

### 数据结构

```text
{
  "source": str,
  "input": {
    "prefix": str,
    "evidence": str,
    "testimonies": str,
    "summarized_context": str,
    "suffix": str,
    "full_input": str
  },
  "output": [[evidence_index, testimony_index], ...]
}
```

统一字段映射：

| 统一字段 | 来源 |
|---|---|
| `id` | `source` |
| `context` | `input.summarized_context` 或 `input.full_input` |
| `question` | 自动生成：找出矛盾的 evidence-testimony pair |
| `options` | evidence 与 testimony 的笛卡尔积 |
| `answer` | `output` |
| `evidence` | `input.evidence` |
| `reasoning` | 原始 source 数据或 eval report |
| `metadata` | 游戏来源、context 设置 |

### 样例

来自 `AA_integrated_dataset.json`：

```text
Source: 2-4-2_Farewell,_My_Turnabout_1
Evidence: [0] Attorney's Badge ... [1] Maya's Magatama ...
Testimonies: indexed witness statements
Output: [[5, 15]]
```

已有 eval summary 包含：

```text
overall_accuracy, overall_evidence_accuracy, overall_testimony_accuracy,
temporal_accuracy, spatial_accuracy, causal_accuracy, physical_accuracy
```

### 可用性

| 评估目标 | 适配度 |
|---|---|
| 最终答案准确率 | 强，但答案是 pair selection |
| 证据覆盖率 | 强 |
| 推理步骤评估 | 中 |
| 矛盾检测 | 强 |
| 长上下文案例 | 中 |

### 建议

TurnaboutLLM 作为矛盾检测辅助 benchmark。它特别适合测试 evidence-vs-testimony conflict、temporal contradiction、spatial contradiction 等能力。

## 5. LLM Mysteries

### 来源

- GitHub：`https://github.com/metareflection/llm-mysteries`
- 本地路径：`data/llm-mysteries/`

### 重点文件

| 文件 | 用途 |
|---|---|
| `data/llm-mysteries/tiny.json` | 小型 mystery QA task |
| `data/llm-mysteries/load_musr.py` | MuSR loader 参考 |
| `data/llm-mysteries/main_musr.py` | MuSR 运行参考 |
| `data/llm-mysteries/main_detect_bench_prompt.py` | DetectBench 风格 prompt 参考 |
| `data/llm-mysteries/belief_graph.py` | belief graph 抽取参考 |
| `data/llm-mysteries/graph.py` | evidence graph 推理参考 |

### 作用

`tiny.json` 是 BIG-Bench 风格的 minute mysteries task descriptor，不如 MuSR / DetectBench 适合作为第一阶段主 benchmark。但这个仓库里的代码对我们的 demo 很有参考价值：

- 让模型抽取 incriminating / exonerating evidence；
- 构建 belief graph；
- 做 symbolic consistency check；
- 借鉴 DetectBench prompt。

### 可用性

| 评估目标 | 适配度 |
|---|---|
| 最终答案准确率 | 中 |
| 证据覆盖率 | 中 |
| 推理步骤评估 | 中 |
| 矛盾检测 | 中 |
| 长上下文案例 | 弱 |

### 建议

LLM Mysteries 不作为第一阶段主 benchmark，而作为 evidence graph / belief graph demo 的参考实现。

## 第一批统一 Loader 优先级

推荐顺序：

1. **MuSR murder mystery**
   - 最容易读取；
   - 多选凶手判断干净；
   - 适合作为第一批 baseline。

2. **DetectBench test-hard / test**
   - 证据发现标注最强；
   - 自带 clue graph；
   - 直接支持 evidence-card 实验。

3. **TurnaboutLLM**
   - 最适合矛盾检测；
   - 但答案格式是 pair selection，需要单独评估逻辑。

4. **DetectiveQA**
   - 有价值，但需要补完整小说正文。

5. **LLM Mysteries**
   - 作为参考代码和 demo 灵感。

## 下一步建议

建立统一数据样本 schema：

```python
{
    "id": str,
    "dataset": str,
    "split": str,
    "context": str | None,
    "question": str,
    "options": list | dict | None,
    "answer": int | str | list,
    "evidence": object | None,
    "reasoning": object | None,
    "metadata": dict,
}
```

优先实现：

- `load_musr_murder_mystery()`
- `load_detectbench(split="test-hard")`

随后实现：

- `load_turnabout(source="AA")`
- `load_detectiveqa_annotations(lang="en", anno="human")`

## 验证清单

- MuSR murder mystery 可读：是，250 条。
- DetectBench 五个 JSONL split 可读：是。
- DetectBench Test-Hard 可读：是，300 条。
- TurnaboutLLM 核心 JSON 可读：是，AA 200 条 + DR 31 条。
- TurnaboutLLM source/eval 已恢复：是。
- DetectiveQA HuggingFace 标注已下载：是，172 个 JSON 文件。
- DetectiveQA 样本可读：是。
- DetectiveQA 完整小说正文：当前标注文件中未包含，需要后续处理。

