# 带 DetectiveQA 小说正文的小规模复现报告

生成时间：2026-07-03  
实验目录：`runs/small_repro_with_novels_20260703/`  
本报告替代上一版 DetectiveQA 的 `annotation-only` 小测结果。

## 1. 这次更新了什么

上一版 DetectiveQA 只读取了标注文件中的题目、选项、答案和人工 reasoning，没有接入小说正文。因此它只能说明“标注结构能否被程序读取和评测”，不能算真正的长文本侦探推理测试。

这次我从 HuggingFace DetectiveQA 数据集中下载了前 10 道英文人工标注题所需的小说正文，并修改了 loader：

- 本地小说路径：
  - `data/DetectiveQA/hf_dataset/novel_data_en/117-阳光下的罪恶-阿加莎克里斯蒂.txt`
  - `data/DetectiveQA/hf_dataset/novel_data_en/118-顺水推舟-阿加莎克里斯蒂.txt`
- 代码位置：`src/detective_reasoning/datasets.py`
- 读取策略：根据 `novel_id` 找到对应小说，根据 `answer_position` 截取答案出现位置之前的段落。
- 上下文长度：每题最多保留尾部 24,000 字符，避免 API 上下文过大。
- 保存元信息：`context_status`、`novel_text_path`、`answer_position`、`paragraphs_used`、`context_chars`、`truncated_from_tail`。

注意：这仍然不是完整论文级复现，因为我们只跑了每个数据集 10 题，并且 DetectiveQA 做了 24,000 字符截断。但它已经比上一版更接近真实任务：模型确实看到了小说正文上下文。

## 2. 实验设置

本轮保持四个数据集、两个模型、两种方法的结构，每组 10 题：

- 数据集：
  - MuSR `murder_mystery`
  - DetectBench `test-hard`
  - DetectiveQA `en_human`
  - TurnaboutLLM `AA`
- 模型：
  - DeepSeek V4 Flash：`deepseek-v4-flash`
  - MiniMax：`MiniMax-M3`
- 方法：
  - `baseline_direct`：直接回答。
  - `paper_skill`：根据对应论文任务特点写成的提示/skill。
- 输出保存：
  - 每次实验保存 `manifest.json`
  - 每题保存 `predictions.jsonl`
  - 汇总保存 `summary.csv`
  - 总索引保存 `runs/small_repro_with_novels_20260703/experiment_index.json`

## 3. 结果总表

| 数据集 | 模型 | 方法 | Skill | 正确数 | 准确率 | 总 token | Run ID |
|---|---|---|---|---:|---:|---:|---|
| MuSR | DeepSeek V4 Flash | baseline | - | 5/10 | 50% | 12,869 | `run_20260703T142845Z_e71f06d0` |
| MuSR | DeepSeek V4 Flash | paper_skill | `musr_cot_plus` | 8/10 | 80% | 15,362 | `run_20260703T142908Z_e5a87617` |
| MuSR | MiniMax-M3 | baseline | - | 7/10 | 70% | 14,176 | `run_20260703T142950Z_05f445b8` |
| MuSR | MiniMax-M3 | paper_skill | `musr_cot_plus` | 9/10 | 90% | 17,311 | `run_20260703T143017Z_5aa31f38` |
| DetectBench | DeepSeek V4 Flash | baseline | - | 8/10 | 80% | 7,943 | `run_20260703T143121Z_d2554092` |
| DetectBench | DeepSeek V4 Flash | paper_skill | `detectbench_detective_prompt` | 9/10 | 90% | 9,432 | `run_20260703T143139Z_148e96ca` |
| DetectBench | MiniMax-M3 | baseline | - | 8/10 | 80% | 10,137 | `run_20260703T143208Z_362f4cba` |
| DetectBench | MiniMax-M3 | paper_skill | `detectbench_detective_prompt` | 7/10 | 70% | 13,193 | `run_20260703T143253Z_a899319e` |
| DetectiveQA | DeepSeek V4 Flash | baseline | - | 10/10 | 100% | 64,701 | `run_20260703T143357Z_141f0b8e` |
| DetectiveQA | DeepSeek V4 Flash | paper_skill | `detectiveqa_stepwise_reasoning` | 10/10 | 100% | 65,861 | `run_20260703T143415Z_765ab6bf` |
| DetectiveQA | MiniMax-M3 | baseline | - | 9/10 | 90% | 64,105 | `run_20260703T143438Z_9b967fc0` |
| DetectiveQA | MiniMax-M3 | paper_skill | `detectiveqa_stepwise_reasoning` | 10/10 | 100% | 65,908 | `run_20260703T143511Z_8647ec86` |
| TurnaboutLLM | DeepSeek V4 Flash | baseline | - | 0/10 | 0% | 14,682 | `run_20260703T143552Z_bf61b01a` |
| TurnaboutLLM | DeepSeek V4 Flash | paper_skill | `turnabout_contradiction_matrix` | 0/10 | 0% | 16,026 | `run_20260703T143612Z_c601d65f` |
| TurnaboutLLM | MiniMax-M3 | baseline | - | 0/10 | 0% | 17,387 | `run_20260703T143638Z_16e3b520` |
| TurnaboutLLM | MiniMax-M3 | paper_skill | `turnabout_contradiction_matrix` | 0/10 | 0% | 18,027 | `run_20260703T143727Z_93da6e03` |

## 4. 直观结论

MuSR 上，`musr_cot_plus` 对两个模型都有明显提升：DeepSeek 从 50% 到 80%，MiniMax 从 70% 到 90%。这说明“先整理线索、嫌疑人、动机、时间线，再回答”的结构化 CoT 在短篇侦探推理里是有价值的。

DetectBench 上，DeepSeek 从 80% 到 90%，但 MiniMax 从 80% 降到 70%。这提醒我们：同一个 skill 不一定对所有模型都正向，提示变长后也可能引入干扰。后面应该做更细的 ablation，例如只加线索表、只加矛盾检查、只加答案校验。

DetectiveQA 这次已经接入小说正文。DeepSeek 两组都是 100%，MiniMax 从 90% 到 100%。但这 10 题来自两本小说的前 10 个英文人工标注样本，样本量太小，不能说明模型已经解决长篇侦探推理。它更适合作为“长文本上下文接入已经成功”的 smoke test。

TurnaboutLLM 仍然 0%。这不是程序崩溃，所有输出都被解析出来了；问题在于当前 prompt 让模型输出的 pair 顺序、证据编号、证词编号经常和 gold 不一致。它需要单独复现论文中的 action space、candidate pair 枚举和格式约束，否则不适合直接和 MuSR/DetectBench 放在同一批主实验里。

## 5. 对开题的启发

目前最可行的论文切口不是“证明某个大 skill 一定提升所有任务”，而是：

**外部结构化记忆/证据库什么时候能提升侦探推理，什么时候反而会干扰？**

可以把方法拆成几个可评估模块：

- `evidence_card`：抽取人物、地点、时间、事件、物证。
- `timeline_memory`：按时间顺序整理案件事件。
- `contradiction_check`：检查证词和证据是否冲突。
- `answer_verifier`：最终答案前做一次证据一致性检查。
- `retrieval_context`：长文本任务中只取与问题相关的段落，而不是固定尾部截断。

第一阶段主实验建议只用 MuSR 和 DetectBench，因为它们稳定、成本低、样本数量清楚。DetectiveQA 放第二阶段做长文本 case study。TurnaboutLLM 暂时作为结构化矛盾检测的困难案例，不建议一开始作为主 benchmark。

## 6. 下一步建议

1. 给 DetectiveQA 做 retrieval 版本：用问题和选项从小说中检索相关段落，而不是固定截取答案前 24,000 字符。
2. 给 MuSR / DetectBench 做 skill ablation：baseline、CoT、evidence card、timeline、contradiction check、verifier。
3. 对每个数据集扩大到 50 或全量，再看趋势是否稳定。
4. TurnaboutLLM 先重写专用 loader 和 evaluator，把候选 evidence-testimony pair 枚举出来，要求模型只从候选 pair 中选择。
5. GUI 中把每次运行的上下文状态显示出来，尤其是 DetectiveQA 是否加载小说正文、截断长度、来源小说。
