# 50 条样本扩大复现报告

生成时间：2026-07-04  
实验目录：`runs/reproduction_50_20260704_v2`  
可视化：`notes/figures/reproduction_50_accuracy_by_dataset_model.svg`  

## 1. 实验范围

本轮把上一版 10 条 smoke test 扩大到每组 50 条。实验矩阵为 4 个数据集 × 2 个模型 × 2 种方法，共 16 组、800 次模型调用。

- 数据集：MuSR murder mystery、DetectBench test-hard、DetectiveQA en_human、TurnaboutLLM AA。
- 模型：DeepSeek V4 Flash、MiniMax-M3。
- 方法：Baseline 直接回答；Skill 使用对应任务的 paper-inspired prompt。
- DetectiveQA：前 50 条所需小说正文已下载，本轮 50/50 样本均加载小说上下文。每题根据 `answer_position` 取答案前段落，并保留尾部最多 24,000 字符。
- 运行状态：全部 16 组完成。

## 2. 总结果

| 数据集 | 模型 | 方法 | Skill | 正确数 | 准确率 | Parse errors | Run ID |
|---|---|---|---|---:|---:|---:|---|
| MuSR | DeepSeek V4 Flash | Baseline | - | 31/50 | 62.0% | 0 | `run_20260704T010630Z_2cdb93dd` |
| MuSR | DeepSeek V4 Flash | Skill | `musr_cot_plus` | 43/50 | 86.0% | 0 | `run_20260704T010820Z_2434f237` |
| MuSR | MiniMax-M3 | Baseline | - | 33/50 | 66.0% | 0 | `run_20260704T011158Z_f0be3167` |
| MuSR | MiniMax-M3 | Skill | `musr_cot_plus` | 37/50 | 74.0% | 0 | `run_20260704T011500Z_11b8e7ce` |
| DetectBench | DeepSeek V4 Flash | Baseline | - | 42/50 | 84.0% | 0 | `run_20260704T012013Z_643d9009` |
| DetectBench | DeepSeek V4 Flash | Skill | `detectbench_detective_prompt` | 43/50 | 86.0% | 0 | `run_20260704T012211Z_6c74e394` |
| DetectBench | MiniMax-M3 | Baseline | - | 39/50 | 78.0% | 1 | `run_20260704T012451Z_154c042a` |
| DetectBench | MiniMax-M3 | Skill | `detectbench_detective_prompt` | 41/50 | 82.0% | 0 | `run_20260704T013321Z_f93d2d52` |
| DetectiveQA | DeepSeek V4 Flash | Baseline | - | 48/50 | 96.0% | 0 | `run_20260704T014146Z_1de6ab7e` |
| DetectiveQA | DeepSeek V4 Flash | Skill | `detectiveqa_stepwise_reasoning` | 49/50 | 98.0% | 0 | `run_20260704T014302Z_02f7b416` |
| DetectiveQA | MiniMax-M3 | Baseline | - | 47/50 | 94.0% | 0 | `run_20260704T014449Z_f98a2beb` |
| DetectiveQA | MiniMax-M3 | Skill | `detectiveqa_stepwise_reasoning` | 45/50 | 90.0% | 0 | `run_20260704T014713Z_fa71fcbb` |
| TurnaboutLLM | DeepSeek V4 Flash | Baseline | - | 0/50 | 0.0% | 1 | `run_20260704T015101Z_d219f2fc` |
| TurnaboutLLM | DeepSeek V4 Flash | Skill | `turnabout_contradiction_matrix` | 1/50 | 2.0% | 0 | `run_20260704T015246Z_20d566a9` |
| TurnaboutLLM | MiniMax-M3 | Baseline | - | 0/50 | 0.0% | 2 | `run_20260704T015435Z_2285c12a` |
| TurnaboutLLM | MiniMax-M3 | Skill | `turnabout_contradiction_matrix` | 3/50 | 6.0% | 1 | `run_20260704T015916Z_b93d6bb6` |

## 3. Skill 提升/下降

| 数据集 | 模型 | Baseline | Skill | 差值 |
|---|---|---:|---:|---:|
| DetectBench | DeepSeek V4 Flash | 84.0% | 86.0% | +2.0 pp |
| DetectBench | MiniMax-M3 | 78.0% | 82.0% | +4.0 pp |
| DetectiveQA | DeepSeek V4 Flash | 96.0% | 98.0% | +2.0 pp |
| DetectiveQA | MiniMax-M3 | 94.0% | 90.0% | -4.0 pp |
| MuSR | DeepSeek V4 Flash | 62.0% | 86.0% | +24.0 pp |
| MuSR | MiniMax-M3 | 66.0% | 74.0% | +8.0 pp |
| TurnaboutLLM | DeepSeek V4 Flash | 0.0% | 2.0% | +2.0 pp |
| TurnaboutLLM | MiniMax-M3 | 0.0% | 6.0% | +6.0 pp |

## 4. 初步观察

MuSR 仍然是最适合第一阶段主实验的数据集之一，因为它稳定、成本适中，且能直接观察结构化 CoT 是否提升多步侦探推理。

DetectBench 的结果需要看模型差异：如果 skill 对某个模型提升、对另一个模型下降，就说明“外部结构化提示”不是无条件有效，后续应拆成 evidence card、timeline、contradiction check、verifier 做 ablation。

DetectiveQA 本轮已经是带小说正文的长文本测试。由于固定 24,000 字符尾部截断仍然比较粗糙，下一步更有研究价值的是加入 retrieval/context selection，比较“固定截断”和“问题相关证据检索”的差异。

TurnaboutLLM 如果仍然低分，优先不要把它当主 benchmark，而应把它改造成候选 pair 选择任务：先枚举 evidence-testimony pair，再让模型在候选项中选择，减少编号和顺序错误。

## 5. 下一步

1. 在 MuSR 和 DetectBench 上做 skill ablation。
2. 给 DetectiveQA 加检索式外部证据库。
3. 将 GUI 增加图表入口，显示不同模型/方法的准确率和 token 成本。
4. TurnaboutLLM 单独做 candidate-pair 版本 evaluator。
