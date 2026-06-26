# 已收集论文概述

## 研究主线

目前找到的论文可以分成三组：

1. **CoT / Test-Time Improvement**：研究模型在推理阶段如何多想、搜索、验证和控制 thinking budget。
2. **侦探 / 叙事推理 Benchmark**：证明侦探推理是一个困难任务，涉及长上下文、隐含证据、多步推理和证词整合。
3. **空间记忆 / Cognitive Map / 图结构记忆**：研究 LLM 或智能体如何用结构化地图、动态记忆、拓扑图来理解空间关系。

我们的选题正好可以放在三者交叉处：

> 用结构化的时空证据记忆，改进 LLM 在侦探叙事中的 test-time reasoning。

## 总览表

| 方向 | 论文 | 核心作用 |
|---|---|---|
| Test-Time Reasoning | Tree of Thoughts | 多路径搜索式推理 baseline |
| Test-Time Reasoning | s1: Simple test-time scaling | thinking budget / budget forcing 的重要参考 |
| Test-Time Reasoning | Adaptive Generate-Rank-Verify | 成本敏感的生成-排序-验证框架 |
| 侦探推理 | MuSR | murder mystery 多步软推理 benchmark |
| 侦探推理 | DetectBench | 隐含证据发现与多跳推理 benchmark |
| 侦探推理 | DetectiveQA | 长篇侦探小说长上下文推理 benchmark |
| 空间记忆 | Tag Map | 用文本地图帮助 LLM 空间推理 |
| 空间记忆 | Cog-GA | cognitive map + LLM agent 导航 |
| 空间记忆 | From Text to Space | 研究 LLM 是否能从文本形成空间表征 |
| 空间记忆 | Can LLMs Learn to Map the World | 从局部描述整合全局空间地图 |
| 空间记忆 | MSNav | 动态记忆 + 空间推理模块 |
| 空间记忆 | Spatial Memory Graph Rectification | 增量图构建与图修复 |
| 空间记忆 | RAGNav | RAG + 拓扑图 + 语义记忆 |
| 空间记忆 | LASAR | latent cognitive map 支持时空推理 |
| 时空记忆 Agent | STMA | dynamic KG + planner-critic 的时空记忆框架 |

## 一、CoT / Test-Time Improvement

### 1. Tree of Thoughts: Deliberate Problem Solving with Large Language Models

**它解决什么问题**

普通 Chain-of-Thought 是一条线性推理路径。如果前面一步想错，后面容易一路错下去。Tree of Thoughts 提出让模型同时探索多个中间想法，并进行自我评估、回溯和搜索。

**核心方法**

- 把推理过程拆成多个 thought。
- 每一步生成多个候选 thought。
- 对候选进行评分或投票。
- 用 BFS / DFS 等搜索策略选择后续路径。

**和我们课题的关系**

侦探推理天然需要比较多个嫌疑人和多条解释路径。ToT 可以作为 baseline：让模型对不同嫌疑人分别生成推理路径，再比较哪条更合理。

**局限**

ToT 提升的是搜索结构，但它没有专门解决证据记忆问题。侦探故事中最难的往往不是“想得不够多”，而是时间线、地点、证词和物品状态被混淆。

### 2. s1: Simple test-time scaling

**它解决什么问题**

这篇论文研究如何用很简单的方式实现 test-time scaling，也就是在测试阶段通过增加推理计算来提升模型表现。

**核心方法**

- 构造一个小规模高质量推理数据集 s1K。
- 提出 budget forcing：控制模型在测试时的思考长度。
- 可以强制模型停止，也可以通过追加类似 “Wait” 的方式让模型继续思考。

**和我们课题的关系**

这篇直接对应我们的问题：模型什么时候应该继续想，什么时候应该停止。我们可以把侦探推理中的 thinking budget 具体化，例如：

- 继续抽取证据；
- 继续检查时间线；
- 继续验证嫌疑人；
- 停止并输出答案。

**局限**

s1 主要关注通用推理能力，并不关心侦探故事中的结构化证据、空间关系和证词矛盾。

### 3. Adaptive Generate-Rank-Verify: Inference-Time Search with Costly Verification

**它解决什么问题**

很多任务中，生成候选答案便宜，但验证答案很贵。论文把这个问题形式化为成本敏感的 inference-time search。

**核心方法**

- Generate：生成多个候选答案。
- Rank：用较便宜的信号给候选排序。
- Verify：只对有希望的候选进行昂贵验证。
- 根据当前信息动态决定是否继续采样或验证。

**和我们课题的关系**

侦探推理也可以设计成类似流程：

- Generate：生成可能凶手或解释路径。
- Rank：根据证据覆盖率、矛盾数量、时间线一致性排序。
- Verify：对最可能的解释进行证据图检查。

这可以成为我们研究 thinking budget 的理论支撑。

**局限**

论文偏理论和一般推理任务，没有直接处理自然语言故事中的时空证据结构。

## 二、侦探 / 叙事推理 Benchmark

### 4. MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning

**它解决什么问题**

MuSR 认为现有 benchmark 很多只测逻辑推理或简单常识，无法同时测试自然语言理解、常识和多步推理。它构造了自然语言叙事形式的多步软推理任务。

**核心内容**

- 包含三个任务：Murder Mystery、Object Placements、Team Allocation。
- Murder Mystery 要判断谁最可能是凶手。
- Object Placements 涉及物品位置和空间/物理推理。
- 数据生成时有底层 reasoning tree。

**关键数据**

- GPT-4 + CoT+ 在 Murder Mystery 上为 80.4%，人类为 94.1%。
- GPT-4 + CoT+ 在 Object Placements 上为 60.9%，人类为 95.0%。

**和我们课题的关系**

MuSR 是我们最适合做 baseline 的数据集之一。它已经包含 murder mystery，而且有多步推理结构。Object Placements 也很适合支撑我们对空间/物品状态追踪的关注。

**局限**

MuSR 的故事相对短，主要评估最终选择题结果。它没有专门提供完整的时空证据图标注。

### 5. DetectBench: Can Large Language Model Detect and Piece Together Implicit Evidence?

**它解决什么问题**

DetectBench 关注一个关键问题：模型做错题，可能不是因为不会推理，而是因为没有找到隐含证据。

**核心内容**

- 数据包含 3,928 道多选题。
- 每题平均约 994 tokens。
- 每题平均有 4.55 条隐含证据。
- 通常需要 7.62 个逻辑跳跃才能得到正确答案。
- 论文提出 Detective Reasoning Prompt 和相关 fine-tuning 方法。

**关键数据**

- GPT4-Turbo 平均 evidence detection RougeL-F 只有 44.4。
- Test-Hard 中 GPT4 Naive 的 evidence detection 为 31.4，correct answering 为 29.6。

**和我们课题的关系**

DetectBench 非常适合证明“证据发现”是侦探推理的瓶颈。我们的方法可以把隐含证据抽取出来，放入 evidence graph，再让模型基于图推理。

**局限**

DetectBench 更重视 evidence detection 和多跳推理，但不一定细分时间线、空间位置、物品状态等结构。

### 6. DetectiveQA: Evaluating Long-Context Reasoning on Detective Novels

**它解决什么问题**

DetectiveQA 用真实侦探小说测试长上下文叙事推理，关注模型能否在很长文本中找到证据并还原推理链。

**核心内容**

- 包含 1200 个人工标注问题。
- 覆盖中英文侦探小说。
- 平均上下文长度超过 100k tokens，论文报告平均约 118k tokens。
- 每个答案配有 reference reasoning steps。
- 提出 step-wise reasoning metric，不只看最终答案，还看推理过程是否覆盖关键步骤。

**关键数据**

- 每个答案平均涉及 8.48 个 reference reasoning steps。
- GPT-4-1106 answer accuracy 为 73.99，但 reasoning score 只有 27.43。
- Claude3-Opus answer accuracy 为 81.95，但 reasoning score 为 37.33。

**和我们课题的关系**

DetectiveQA 支持我们强调“只看最终答案不够”。侦探推理需要评价证据链和推理过程。我们可以借鉴它的 step-wise reasoning metric，设计自己的证据图覆盖率、时间线准确率、矛盾识别率。

**局限**

长篇小说数据处理成本较高，不适合作为暑期项目一开始的大规模主实验。更适合做小规模定性案例。

## 三、空间记忆 / Cognitive Map / 图结构记忆

### 7. Tag Map: A Text-Based Map for Spatial Reasoning and Navigation with Large Language Models

**它解决什么问题**

机器人或智能体要用 LLM 做导航规划时，需要给模型可理解的场景上下文。传统 embedding map 不容易直接给 LLM 解释，因此论文提出显式 text-based map。

**核心方法**

- 把场景中的物体、位置、语义信息组织成文本地图。
- LLM 可以查询地图并进行导航规划。
- 强调 open-vocabulary 场景理解。

**和我们课题的关系**

我们可以借鉴“文本地图”的思想，把侦探故事中的场景转成文本化 evidence map。例如：

- 谁在厨房；
- 刀在哪里；
- 证人何时看到嫌疑人；
- 某个物品是否被移动。

**局限**

它主要用于机器人导航，不直接处理叙事时间线和证词矛盾。

### 8. Cog-GA: Cognitive Map Generative Agent

**它解决什么问题**

Vision-Language Navigation 需要智能体在 3D 环境中根据自然语言指令导航。Cog-GA 尝试让 LLM agent 构建类似人类的 cognitive map。

**核心方法**

- 构建融合时间、空间、语义元素的 cognitive map。
- 用 waypoint prediction 优化探索路径。
- 把场景描述分为 what 和 where 两个通道。

**和我们课题的关系**

对我们最有价值的是 cognitive map 的结构思想：记忆不只是文本摘要，而是包含时间、地点和语义关系的动态结构。

**局限**

需要视觉/导航环境，工程复杂度高。我们的暑期项目更适合做文本版 cognitive map。

### 9. From Text to Space: Mapping Abstract Spatial Models in LLMs during a Grid-World Navigation Task

**它解决什么问题**

这篇研究 LLM 是否能从文本描述中形成空间表征，以及不同文本编码格式如何影响空间导航表现。

**核心方法**

- 用 grid-world navigation 测试模型。
- 比较不同空间表示方式。
- 发现笛卡尔坐标等表示更利于模型决策。
- 通过 probing 分析模型内部是否存在与空间位置相关的单元。

**和我们课题的关系**

它支持一个关键判断：空间信息的表示方式会显著影响 LLM 表现。我们在侦探推理中也可以比较不同证据表示：

- 原始文本；
- 事件列表；
- 时间线表格；
- 人物-地点图；
- 完整时空证据图。

**局限**

grid-world 比侦探小说简单，空间结构更规则，不能直接代表复杂叙事推理。

### 10. Can LLMs Learn to Map the World from Local Descriptions?

**它解决什么问题**

这篇问：LLM 能否从局部、相对的位置描述中，整合出一致的全局空间认知？

**核心方法**

- 用模拟城市环境。
- 测试空间感知：从局部关系推断全局布局。
- 测试空间导航：从路径轨迹学习道路连接，并规划新路线。

**和我们课题的关系**

侦探故事也常常只给局部线索，比如“嫌疑人从书房出来”“证人在走廊听到声音”。我们的任务是让模型把这些局部描述整合成全局案件状态。

**局限**

它关注空间关系，不关注人物动机、证词可信度和案件推理。

### 11. MSNav: Zero-Shot Vision-and-Language Navigation with Dynamic Memory and LLM Spatial Reasoning

**它解决什么问题**

LLM 导航容易出现空间推理弱、跨模态 grounding 弱、长程任务记忆过载等问题。MSNav 提出动态记忆和空间推理模块来增强导航。

**核心方法**

- Memory Module：动态地图记忆，通过节点剪枝减少记忆过载。
- Spatial Module：专门处理空间推理。
- Navigation Module：完成具体行动决策。

**和我们课题的关系**

“动态记忆 + 节点剪枝”很有启发。侦探故事中的证据也会很多，我们需要决定哪些证据保留、哪些暂时忽略，以及如何避免上下文爆炸。

**局限**

论文涉及视觉导航和微调模型，计算资源需求较高。我们更适合借鉴思想，做轻量文本图模块。

### 12. Constructing Coherent Spatial Memory in LLM Agents through Graph Rectification

**它解决什么问题**

LLM agent 在增量构建地图时容易产生结构不一致，比如边连错、位置冲突、路径矛盾。论文提出图修复机制，让空间记忆更一致。

**核心方法**

- 增量构建导航图。
- 用版本控制记录图变化。
- 用 Edge Impact Score 判断哪些边更值得修复。
- 检测、定位、修正图结构矛盾。

**和我们课题的关系**

这篇非常贴近我们的证据图想法。侦探故事中的证据图也会出现冲突：

- 同一时间一个人出现在两个地点；
- 证词和物理证据矛盾；
- 物品状态前后不一致。

我们可以把“graph rectification”改造成“evidence graph consistency checking”。

**局限**

它主要修复空间导航图，而不是案件证据图。我们需要扩展到时间、人物、证词和物品状态。

### 13. RAGNav: Retrieval-Augmented Topological Reasoning Framework for Multi-Goal VLN

**它解决什么问题**

普通 RAG 在空间任务中容易 hallucination 和 planning drift，因为检索到的是语义文本片段，不一定包含明确拓扑结构。RAGNav 把语义检索和拓扑地图结合起来。

**核心方法**

- Dual-Basis Memory：
  - 低层 topological map 保存物理连接；
  - 高层 semantic forest 保存语义层级。
- Anchor-guided retrieval。
- Topological neighbor score propagation。

**和我们课题的关系**

这篇可以支持我们的一个观点：普通 RAG 不够，侦探推理也需要结构化检索。我们可以设计：

- 低层：事件/时间/地点图；
- 高层：动机、证词、嫌疑人解释树。

**局限**

它是导航任务，不是文本侦探推理；但结构化 RAG 的思想很适合迁移。

### 14. LASAR: Towards Spatio-temporal Reasoning with Latent Cognitive Map

**它解决什么问题**

Embodied AI 中，智能体是否真的形成了空间结构模型很难验证。LASAR 提出 latent cognitive map，让模型在观察历史和当前状态之间形成结构化时空表示。

**核心方法**

- 构建动态 cognitive map。
- 用时空对比学习增强空间逻辑。
- 提出 MindCraft，把导航行动和推理问题结合。

**和我们课题的关系**

LASAR 是“时空认知地图”方向最接近我们宏观想法的论文之一。它说明空间/时间记忆可以不是简单文本摘要，而是模型推理的结构基础。

**局限**

LASAR 涉及模型训练和视觉环境，个人算力不太适合完整复现。我们可以做轻量工程版：外部 evidence graph + LLM 查询，而不是训练 latent map。

### 15. STMA: A Spatio-Temporal Memory Agent for Long-Horizon Embodied Task Planning

**它解决什么问题**

STMA 研究 LLM agent 在动态环境中的长程任务规划。作者认为现有 LLM agent 的主要问题是：长期记忆不足，且缺少显式时空关系建模能力。

**核心方法**

- Temporal memory：保存历史 action-observation，并总结成 temporal belief。
- Spatial memory：用 dynamic knowledge graph 保存空间关系。
- Retrieve algorithm：先语义筛选相关节点，再做 K-hop 子图扩展。
- Relation aggregator：把 triples 转成更适合 LLM 阅读的自然语言 spatial belief。
- Planner-critic：planner 生成多步计划，critic 在执行前检查行动是否符合当前时空状态。

**关键结果**

在 TextWorld cooking tasks 上，STMA 相比最佳 baseline：

- GPT-4o：Success Rate 平均提升 12.5%，Average Score 平均提升 11.15%。
- Qwen2.5-72b-instruct：Success Rate 平均提升 31.25%，Average Score 平均提升 24.7%。

消融实验显示：

- 去掉 spatio-temporal memory 后任务完成率为 0。
- 去掉 spatial memory、summarizer、relation aggregator、critic 都会造成不同程度下降。
- 作者还指出，错误的 spatial belief 可能误导模型，因此结构化记忆必须保证质量。

**和我们课题的关系**

STMA 是目前最直接支持我们方法框架的论文之一。它的任务是 embodied planning，但结构可以迁移到侦探推理：

- temporal memory -> 案件时间线 / 证词顺序；
- dynamic KG spatial memory -> 人物-地点-物品-事件证据图；
- relation aggregator -> 证据摘要 / 嫌疑人证据卡片；
- planner -> 生成嫌疑人解释；
- critic -> 检查解释是否违反时间线、地点、物品状态或证词矛盾。

**局限**

STMA 不处理侦探叙事和证据推理。它主要在 TextWorld cooking task 中评估 success rate 和 average score，而我们的任务需要评估最终答案、证据覆盖、时间线准确率、矛盾识别和 cost-accuracy tradeoff。

## 对我们选题的直接启发

### 1. 研究空白

目前已有工作分别研究了：

- 如何让 LLM 在测试时多想；
- 如何评估侦探推理；
- 如何构建空间/时空记忆。

但较少有工作把三者结合起来，专门研究：

> 在侦探叙事中，结构化时空证据记忆能否提升 LLM 的 test-time reasoning 效果？

### 2. 可行的研究方案

我们不需要训练大模型，可以做一个轻量 pipeline：

1. 输入侦探故事。
2. 抽取人物、时间、地点、物品、事件、证词。
3. 构建 evidence graph。
4. 让 LLM 基于图进行推理。
5. 和 Direct、CoT、Reflection、Self-Consistency、RAG 比较。

### 3. 推荐主实验

优先用：

- MuSR murder mystery：做基础准确率实验。
- DetectBench：做证据发现和 clue graph 对比。
- 少量 synthetic detective cases：做时间线、地点、物品状态、证词矛盾的细粒度标注。

DetectiveQA 可以作为后期定性案例，不建议一开始大规模做。

### 4. 可能的创新点

1. 从“让模型多想”转向“让模型结构化地想”。
2. 把 spatial memory / cognitive map 从导航迁移到侦探叙事推理。
3. 设计细粒度评估指标：时间线准确率、地点追踪、物品状态、证词矛盾、证据覆盖率。
4. 分析 thinking budget：不同推理阶段该花多少 token。

### 5. 开题报告中可以这样总结

本课题不是单纯研究 LLM 能否回答侦探题，而是研究在复杂叙事推理中，LLM 应该如何组织证据、维护时空状态，并在有限 test-time compute 下做出更可靠的决策。
