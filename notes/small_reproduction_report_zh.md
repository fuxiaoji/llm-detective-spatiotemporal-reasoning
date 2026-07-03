# 小规模复现报告：侦探推理数据集与论文式 Skill

日期：2026-07-03  
实验目录：`runs/small_repro_20260703/`  
样本规模：每个数据集前 10 条样本  
模型：DeepSeek V4 Flash、MiniMax-M3  

## 1. 实验目的

本次实验不是完整论文复现，而是一次小规模可行性复现，目标是验证：

1. 当前 GUI / CLI / run 保存系统能否稳定跑真实 API。
2. 从相关论文中提炼出的 prompt-skill 是否能在小样本上提升最终答案准确率。
3. 哪些数据集适合作为后续正式复现实验的主 benchmark。

API key 只作为临时环境变量使用，没有写入代码、报告或 run 文件。

## 2. 数据集与 Skill 设计

| 数据集 | Split | 样本数 | Baseline | 论文式 Skill | Skill 来源思想 |
|---|---|---:|---|---|---|
| MuSR | `murder_mystery` | 10 | `direct` | `musr_cot_plus` | MuSR 的 CoT+：逐候选人比较 means / motive / opportunity / evidence |
| DetectBench | `test-hard` | 10 | `direct` | `detectbench_detective_prompt` | DetectBench 的 detective reasoning：先找隐含证据，再多跳推理 |
| DetectiveQA | `en_human` | 10 | `direct` | `detectiveqa_stepwise_reasoning` | DetectiveQA 的 step-wise reasoning：用有序证据步骤支持答案 |
| TurnaboutLLM | `AA` | 10 | `direct` | `turnabout_contradiction_matrix` | TurnaboutLLM 的矛盾检测：按 temporal / spatial / causal / physical conflict 找证据-证词对 |

## 3. 结果总表

| 数据集 | 模型 | Baseline | Paper-skill | 变化 | Run IDs |
|---|---|---:|---:|---:|---|
| MuSR murder mystery | DeepSeek V4 Flash | 50.0% | 80.0% | +30.0% | `run_20260703T135121Z_420b97e7` / `run_20260703T135211Z_1dbc12bf` |
| MuSR murder mystery | MiniMax-M3 | 60.0% | 90.0% | +30.0% | `run_20260703T135314Z_d6ebf6a2` / `run_20260703T135342Z_d2f88dd6` |
| DetectBench test-hard | DeepSeek V4 Flash | 70.0% | 90.0% | +20.0% | `run_20260703T135448Z_0f973995` / `run_20260703T135509Z_05a63500` |
| DetectBench test-hard | MiniMax-M3 | 90.0% | 90.0% | +0.0% | `run_20260703T135541Z_a950ad13` / `run_20260703T135610Z_6590e685` |
| DetectiveQA en_human | DeepSeek V4 Flash | 90.0% | 100.0% | +10.0% | `run_20260703T135724Z_f8a78415` / `run_20260703T135739Z_c7dbe0de` |
| DetectiveQA en_human | MiniMax-M3 | 90.0% | 100.0% | +10.0% | `run_20260703T135757Z_72c6a9df` / `run_20260703T135831Z_f15577d8` |
| TurnaboutLLM AA | DeepSeek V4 Flash | 0.0% | 0.0% | +0.0% | `run_20260703T135912Z_54897720` / `run_20260703T135930Z_ff61fa31` |
| TurnaboutLLM AA | MiniMax-M3 | 0.0% | 0.0% | +0.0% | `run_20260703T135955Z_3d0d97e6` / `run_20260703T140050Z_970d68f5` |

## 4. 主要发现

### 4.1 MuSR

MuSR 的论文式 `musr_cot_plus` 在两个模型上都带来 +30 个百分点提升。

这说明在短篇 murder mystery 中，让模型显式比较每个候选人的 means、motive、opportunity 和 evidence，确实比直接回答更稳。MuSR 适合作为第一批主实验，因为样本短、可控、评估简单。

### 4.2 DetectBench

DetectBench 上 DeepSeek 从 70% 提升到 90%，MiniMax baseline 已经达到 90%，paper-skill 没有进一步提升。

这说明 DetectBench 的“先找隐含证据、再连接证据链”方向有效，但强模型在前 10 条样本上可能已经接近小样本上限。后续应扩大到 `test-hard` 全 300 条，并增加 evidence coverage 指标，而不是只看 accuracy。

### 4.3 DetectiveQA

DetectiveQA 的 step-wise reasoning skill 在两个模型上都从 90% 提升到 100%。

但需要谨慎解读：当前本地 DetectiveQA 只有 annotation，没有完整小说正文。因此这组更像“标注问答小样本测试”，不能代表完整长上下文小说复现。它适合后续做定性案例和 reasoning-step 评价。

### 4.4 TurnaboutLLM

TurnaboutLLM 在两个模型、两个条件下都是 0%。

这不是解析失败：parse error 都是 0。模型确实输出了 `[evidence_index, testimony_index]`，但答案不对。一个明显错误模式是 evidence/testimony 顺序混淆，例如预测 `[15, 5]`，而 gold 是 `[5, 15]`。这说明 TurnaboutLLM 需要更强的任务专用格式控制、候选 pair 验证，甚至可能需要单独 evaluator 处理顺序、部分正确和 contradiction type。

## 5. 结论

这次小复现支持一个初步判断：

> 论文式 prompt-skill 对短篇侦探推理、隐含证据发现和 step-wise reasoning 有帮助，但对证据-证词矛盾 pair selection 还不够。

最适合继续推进的主线是：

1. MuSR：验证结构化候选人比较和证据卡是否提升 murder mystery accuracy。
2. DetectBench：验证隐含证据发现 skill 是否提升 test-hard accuracy 和 evidence coverage。
3. TurnaboutLLM：作为困难错误分析数据集，用来研究 pair order、证据-证词对齐和矛盾类型识别。

## 6. 下一步建议

1. 把 MuSR `murder_mystery` 扩展到完整 250 条。
2. 把 DetectBench `test-hard` 扩展到完整 300 条。
3. 为 DetectBench 增加 evidence coverage 评价，而不是只看最终答案。
4. 为 TurnaboutLLM 增加部分正确指标：evidence accuracy、testimony accuracy、pair order error。
5. 将当前 paper-skill 与我们自己的 `structured_memory_stub` 组合，测试“论文式推理 + 外部结构化记忆”是否更强。

