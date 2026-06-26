# 开题报告 PPT Agent 输入稿

## 基本要求

- 页数：6 页，最多 7 页。
- 语言：中文为主，英文术语可保留。
- 风格：学术但不要太硬，适合暑期科研开题汇报。
- 重点：突出跨领域结合，不要只讲“LLM 做侦探题”。
- 推荐标题：
  - 中文：基于时空证据记忆的大语言模型侦探推理能力提升研究
  - 英文：Improving LLM Detective Reasoning with Spatio-Temporal Evidence Memory

## 一句话研究定位

本项目研究在侦探叙事推理任务中，如何结合 Chain-of-Thought / Test-Time Improvement、时空信息建模、图结构证据记忆和复杂叙事理解，让大语言模型更可靠地追踪人物、时间、地点、物品和证词矛盾，并在有限 thinking budget 下做出更准确的推理。

## 可用于支撑研究动机的数据

建议不要只写“LLM 在侦探推理中容易出错”，可以改成：

> 虽然强 LLM 在通用问答中表现突出，但在需要长上下文、多步证据整合和时空状态追踪的侦探推理 benchmark 上，仍然与人类或理想推理过程存在明显差距。

可放入 PPT 的证据：

- MuSR murder mystery：GPT-4 + CoT+ 在 Murder Mystery 上为 80.4%，人类为 94.1%；在 Object Placements 上 GPT-4 为 60.9%，人类为 95.0%。这说明即使使用 CoT 类提示，模型在叙事多步推理和空间/物品状态追踪上仍有明显差距。
- DetectBench：论文报告 GPT4-Turbo 的平均 evidence detection RougeL-F 只有 44.4；作者指出当前 LLM 在长上下文中的证据发现能力仍不足。Test-Hard 中 GPT4 Naive 的 evidence detection 为 31.4，correct answering 为 29.6。
- DetectiveQA：长篇侦探小说平均上下文约 118k tokens，答案平均涉及 8.48 个 reference reasoning steps。GPT-4-1106 在 Question+Context 下 answer accuracy 为 73.99，但 step-wise reasoning score 只有 27.43；Claude3-Opus answer accuracy 为 81.95，reasoning score 为 37.33。这说明模型可能答对一部分问题，但推理链条仍不完整。

## 核心研究问题

1. 大语言模型在侦探推理中主要错在哪里？
2. 结构化的时空证据记忆是否能提升模型推理准确率？
3. 不同 test-time reasoning 策略在准确率和推理成本之间有什么差异？
4. 模型什么时候应该继续“思考”，什么时候应该停止？

## Slide 1 - 题目与研究动机

### 标题

基于时空证据记忆的大语言模型侦探推理能力提升研究

### 页面要点

- LLM 已经能进行一定的文本推理，但在复杂侦探叙事中仍然容易出错。
- 侦探推理不只是回答问题，还需要持续追踪：
  - 人物关系
  - 时间线
  - 地点移动
  - 物品状态
  - 证词矛盾
- 本项目希望研究：如何让 LLM 更可靠地组织证据、推理案件、控制思考成本。

### 讲稿提示

普通问答通常只要求模型理解一段文本并给出答案，但侦探故事更接近一个动态系统。人物会移动，证据会出现或消失，证词可能互相矛盾。LLM 如果只依赖普通 CoT，很容易在长文本和复杂线索中遗忘或混淆信息。

### 图示建议

用一张简单示意图：

`Detective Story -> LLM Reasoning -> Suspect / Evidence / Explanation`

旁边标注问题：

`timeline error`, `location confusion`, `missed contradiction`, `wrong evidence`.

## Slide 2 - 跨领域结合

### 标题

跨领域视角：LLM 推理 × 侦探叙事 × 时空记忆 × 图结构

### 页面要点

- LLM 推理：CoT、Tree of Thoughts、Reflection、Self-Consistency。
- Test-Time Improvement：在推理阶段动态增加思考、采样、验证。
- 侦探叙事推理：嫌疑人、动机、作案机会、证词矛盾。
- 时空信息理解：谁在什么时间、什么地点、做了什么。
- 图结构记忆：把文本线索转化为人物-时间-地点-物品-事件图。

### 讲稿提示

这个选题的特点不是单一 NLP 任务，而是把多个方向结合起来。我们既关注语言模型的推理方式，也关注侦探故事本身的结构，还借鉴 cognitive map 和 evidence graph 的思想，帮助模型把线索存下来、查回来、比对起来。

### 图示建议

做一个四象限或中心辐射图：

中心：`LLM Detective Reasoning`

四周：

- `CoT / Test-Time Scaling`
- `Detective Narrative`
- `Spatio-Temporal Memory`
- `Evidence Graph`

## Slide 3 - 已有研究与不足

### 标题

相关研究：已有基础与尚未解决的问题

### 页面要点

**CoT / Test-Time Improvement**

- Tree of Thoughts：让模型探索多条推理路径。
- s1 / test-time scaling：通过增加测试时计算提升结果。
- Adaptive Generate-Rank-Verify：在生成、排序、验证之间分配推理成本。

**侦探推理数据集**

- MuSR：包含 murder mystery 多步推理任务。
- DetectBench：关注隐含证据发现和多跳推理。
- DetectiveQA：面向长篇侦探小说的长上下文问答。

**时空记忆与 Cognitive Map**

- Tag Map、Cog-GA 等工作说明结构化地图和记忆能帮助空间推理。

### 不足

- 许多 CoT 方法只是让模型“多想”，但没有显式保存时空证据。
- 侦探 benchmark 多看最终答案，较少细分模型错在时间线、地点、物品还是证词矛盾。
- 空间记忆研究多用于导航，较少用于侦探叙事推理。

### 讲稿提示

已有研究分别证明了三件事：多步推理很重要，侦探推理很难，结构化空间记忆有帮助。但它们还没有很好地结合起来。因此我们的切入点是，把 test-time reasoning 和结构化时空证据记忆结合，用在侦探推理任务上。

### 图示建议

三列对比表：

| 方向 | 代表工作 | 局限 |
|---|---|---|
| CoT/Test-Time | ToT, s1, AGRV | 多想但不一定记得准 |
| Detective QA | MuSR, DetectBench, DetectiveQA | 缺少细粒度错误分析 |
| Spatial Memory | Tag Map, Cog-GA | 多用于导航，少用于叙事推理 |

## Slide 4 - 研究假设与方法框架

### 标题

核心假设：结构化证据记忆可以减少无效推理

### 页面要点

**研究假设**

如果将侦探故事中的人物、时间、地点、物品、事件和证词矛盾结构化保存，LLM 会比普通 CoT 更稳定，尤其在长文本和复杂线索中更不容易混淆。

**方法框架**

1. 输入侦探故事文本。
2. 抽取事件、人物、地点、时间、物品、证词。
3. 构建 Spatio-Temporal Evidence Graph。
4. 模型在推理时查询证据图。
5. 输出答案、关键证据和推理解释。

### 讲稿提示

我们不是让模型无限制地生成更长 CoT，而是希望给它一个外部结构化记忆。模型可以先把故事整理成证据图，再围绕证据图进行查询和推理。这样既可以提升准确率，也方便分析模型到底错在哪里。

### 图示建议

流程图：

`Story Text -> Event Extraction -> Evidence Graph -> LLM Reasoning -> Answer + Evidence`

证据图节点示例：

- Person: suspect, victim, witness
- Time: 8 PM, before dinner, after the call
- Location: kitchen, study room, hallway
- Object: knife, letter, phone
- Event: entered, left, saw, moved, killed
- Conflict: testimony conflict, alibi conflict

## Slide 5 - 实验设计

### 标题

实验设计：比较不同 Test-Time Reasoning 策略

### 页面要点

**对比方法**

- Direct Answer：直接回答。
- Standard CoT：普通思维链。
- CoT + Reflection：先推理再自我检查。
- Self-Consistency：多次采样后投票。
- RAG：检索相关文本片段。
- Ours：CoT + Spatio-Temporal Evidence Memory。

**关键变量**

- thinking budget：推理 token 数、采样次数、验证次数。
- evidence structure：是否使用时空证据图。
- task difficulty：短故事、长故事、干扰线索、复杂时间线。

### 讲稿提示

实验不只是比较谁准确率高，还要比较在同样成本下谁更有效。比如有些方法可能靠大量采样提高准确率，但 token 成本很高；我们的目标是看结构化证据记忆能否让模型用更少的无效思考获得更好的推理结果。

### 图示建议

做一个方法对比矩阵：

| 方法 | 是否多步推理 | 是否多采样 | 是否显式证据记忆 | 成本 |
|---|---|---|---|---|
| Direct | 否 | 否 | 否 | 低 |
| CoT | 是 | 否 | 否 | 中 |
| Self-Consistency | 是 | 是 | 否 | 高 |
| RAG | 是 | 可选 | 文本片段 | 中 |
| Ours | 是 | 可选 | 时空证据图 | 中 |

## Slide 6 - 数据集与评估指标

### 标题

数据与评估：从最终答案到细粒度推理能力

### 本地已有数据

- MuSR murder mystery：250 条 murder mystery 样本。
- DetectBench 英文版：train/dev/test/test-hard/test-distract 共约 3926 条 JSONL 记录。
- DetectiveQA：长篇侦探小说问答，可用于小规模定性分析。
- TurnaboutLLM：侦探游戏风格的证据和证词矛盾数据。
- LLM Mysteries：可参考其中 belief graph / mystery-solving 思路。

### 评估指标

- Final Answer Accuracy：最终答案是否正确。
- Evidence Recall：是否找到关键证据。
- Timeline Accuracy：时间线是否正确。
- Location Tracking Accuracy：人物地点移动是否正确。
- Object State Accuracy：物品位置和状态是否正确。
- Contradiction Detection：是否识别证词矛盾。
- Cost-Accuracy Tradeoff：准确率与 token 成本、调用次数的关系。

### 讲稿提示

公开数据集可以用来做 baseline，但它们不一定都有完整的时空状态标注。因此主实验可以结合公开数据和少量可控 synthetic detective cases。synthetic 数据的优点是可以人为控制时间线、地点变化、证词矛盾，并给出清晰 gold label。

### 图示建议

一张数据来源表：

| 数据集 | 用途 | 优势 |
|---|---|---|
| MuSR | murder mystery baseline | 有多步推理结构 |
| DetectBench | evidence discovery | 有 clue graph |
| DetectiveQA | 长上下文案例 | 接近真实侦探小说 |
| Synthetic Cases | 主实验控制变量 | 可标注时空状态 |

## Slide 7 - 预期贡献与研究计划

### 标题

预期贡献与可行性

### 页面要点

**预期贡献**

1. 总结 LLM 在侦探推理中的典型错误类型。
2. 设计一个 Spatio-Temporal Evidence Memory / Graph 方法。
3. 比较不同 test-time reasoning 策略的准确率和成本。
4. 探索 thinking budget 的分配：什么时候继续推理，什么时候停止。

**可行性**

- 不需要训练大模型，主要使用现有 LLM API 和 Python 图结构处理。
- 数据集已经下载到本地，可先做小规模 baseline。
- 方法可以从轻量版本开始：先用规则/LLM 抽取证据，再逐步优化。

**阶段计划**

- 第 1 阶段：阅读论文，整理错误类型和数据格式。
- 第 2 阶段：实现 baseline：Direct、CoT、Reflection、Self-Consistency。
- 第 3 阶段：构建证据图与时空记忆模块。
- 第 4 阶段：实验比较，分析 cost-accuracy tradeoff。
- 第 5 阶段：整理报告和可视化案例。

### 讲稿提示

这个项目的优势是可从轻量实验做起，不依赖个人显卡训练大模型。创新点也比较清楚：不是单纯追求更强模型，而是研究如何在推理阶段组织证据、调用记忆、分配思考成本。

### 图示建议

时间线图：

`Paper Review -> Baselines -> Evidence Graph -> Experiments -> Report`

## 推荐 PPT 视觉风格

- 主色：深蓝、灰白、少量橙色强调。
- 图示风格：流程图、对比表、证据图节点。
- 避免大段文字，每页 3-5 个 bullet。
- 每页底部可放一句小结，例如：
  - Slide 2：This is a cross-domain reasoning problem.
  - Slide 4：Memory structure matters as much as reasoning length.
  - Slide 6：Evaluation should measure process, not only final answers.

## 可直接给 PPT Agent 的生成指令

请根据以下内容生成一份 6-7 页中文开题报告 PPT，题目为“基于时空证据记忆的大语言模型侦探推理能力提升研究”。PPT 需要突出跨领域结合：大语言模型推理、Chain-of-Thought / Test-Time Improvement、侦探叙事推理、时空信息理解、图结构证据记忆。整体风格学术、清晰、简洁，适合暑期科研开题汇报。

每页要求：

1. 标题页：题目、研究方向、核心问题。
2. 研究背景：LLM 在侦探推理中的困难，包括时间线、地点、物品、证词矛盾。
3. 跨领域结合：展示 LLM reasoning、detective narrative、spatio-temporal memory、evidence graph 的融合。
4. 相关研究与不足：包含 CoT/Test-Time、侦探 benchmark、空间记忆三类工作。
5. 方法框架：Story Text -> Event Extraction -> Spatio-Temporal Evidence Graph -> LLM Reasoning -> Answer + Evidence。
6. 实验设计与数据：MuSR、DetectBench、DetectiveQA、TurnaboutLLM、synthetic cases；比较 Direct、CoT、Reflection、Self-Consistency、RAG、Ours。
7. 预期贡献与计划：错误分析、证据图方法、cost-accuracy tradeoff、thinking budget 分配、研究时间线。

请减少文字堆积，多用流程图、对比表和中心辐射图。视觉上使用深蓝、灰白和橙色强调。每页中文为主，保留必要英文术语。

## 参考论文与本地文件

### CoT / Test-Time Improvement

- Tree of Thoughts: Deliberate Problem Solving with Large Language Models  
  本地文件：`papers/2305.10601_Tree_of_Thoughts.pdf`

- s1: Simple test-time scaling  
  本地文件：`papers/2025.emnlp-main.1025_s1_Simple_Test_Time_Scaling.pdf`

- Adaptive Generate-Rank-Verify: Inference-Time Search with Costly Verification  
  本地文件：`papers/2605.17609_Adaptive_Generate_Rank_Verify.pdf`

### Detective / Narrative Reasoning

- MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning  
  本地文件：`papers/2310.16049_MuSR_Multistep_Soft_Reasoning.pdf`

- DetectBench: Can Large Language Model Detect and Piece Together Implicit Evidence?  
  本地文件：`papers/2406.12641_DetectBench.pdf`

- DetectiveQA: Evaluating Long-Context Reasoning on Detective Novels  
  本地文件：`papers/2409.02465_DetectiveQA.pdf`

### Spatial Memory / Cognitive Map

- Tag Map: A Text-Based Map for Spatial Reasoning and Navigation with Large Language Models  
  本地文件：`papers/2409.15451_Tag_Map_Text_Based_Map_for_LLMs.pdf`

- Cog-GA: A Large Language Models-based Generative Agent for Vision-Language Navigation in Continuous Environments  
  本地文件：`papers/2409.02522_Cog_GA_Cognitive_Map_Generative_Agent.pdf`

- MSNav: Dynamic Memory and Spatial Reasoning  
  本地文件：`papers/2508.16654_MSNav_Dynamic_Memory_Spatial_Reasoning.pdf`

- Coherent Spatial Memory via Graph Rectification  
  本地文件：`papers/2510.04195_Coherent_Spatial_Memory_Graph_Rectification.pdf`
