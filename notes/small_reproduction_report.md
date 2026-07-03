# Small-Scale Reproduction Report: Detective Reasoning Skills

Date: 2026-07-03  
Run directory: `runs/small_repro_20260703/`  
Sample size: first 10 samples per dataset  
Models: DeepSeek V4 Flash and MiniMax-M3  

## Goal

This is not a full paper reproduction. It is a small-scale feasibility reproduction to test whether:

1. The current GUI / CLI / run-saving pipeline works with real APIs.
2. Paper-inspired prompt skills can improve final-answer accuracy on small samples.
3. The datasets are suitable for larger baseline reproduction.

API keys were used only as temporary runtime inputs and were not saved to code, reports, or run files.

## Setup

| Dataset | Split | N | Baseline | Paper Skill | Source Idea |
|---|---|---:|---|---|---|
| MuSR | `murder_mystery` | 10 | `direct` | `musr_cot_plus` | MuSR CoT+: compare means, motive, opportunity, and evidence by candidate |
| DetectBench | `test-hard` | 10 | `direct` | `detectbench_detective_prompt` | DetectBench detective reasoning: detect implicit evidence, then connect multi-hop clues |
| DetectiveQA | `en_human` | 10 | `direct` | `detectiveqa_stepwise_reasoning` | DetectiveQA step-wise reasoning: answer through ordered evidence steps |
| TurnaboutLLM | `AA` | 10 | `direct` | `turnabout_contradiction_matrix` | TurnaboutLLM contradiction pair search over temporal, spatial, causal, and physical conflicts |

## Results

| Dataset | Model | Baseline | Paper Skill | Delta | Run IDs |
|---|---|---:|---:|---:|---|
| MuSR murder mystery | DeepSeek V4 Flash | 50.0% | 80.0% | +30.0% | `run_20260703T135121Z_420b97e7` / `run_20260703T135211Z_1dbc12bf` |
| MuSR murder mystery | MiniMax-M3 | 60.0% | 90.0% | +30.0% | `run_20260703T135314Z_d6ebf6a2` / `run_20260703T135342Z_d2f88dd6` |
| DetectBench test-hard | DeepSeek V4 Flash | 70.0% | 90.0% | +20.0% | `run_20260703T135448Z_0f973995` / `run_20260703T135509Z_05a63500` |
| DetectBench test-hard | MiniMax-M3 | 90.0% | 90.0% | +0.0% | `run_20260703T135541Z_a950ad13` / `run_20260703T135610Z_6590e685` |
| DetectiveQA en_human | DeepSeek V4 Flash | 90.0% | 100.0% | +10.0% | `run_20260703T135724Z_f8a78415` / `run_20260703T135739Z_c7dbe0de` |
| DetectiveQA en_human | MiniMax-M3 | 90.0% | 100.0% | +10.0% | `run_20260703T135757Z_72c6a9df` / `run_20260703T135831Z_f15577d8` |
| TurnaboutLLM AA | DeepSeek V4 Flash | 0.0% | 0.0% | +0.0% | `run_20260703T135912Z_54897720` / `run_20260703T135930Z_ff61fa31` |
| TurnaboutLLM AA | MiniMax-M3 | 0.0% | 0.0% | +0.0% | `run_20260703T135955Z_3d0d97e6` / `run_20260703T140050Z_970d68f5` |

## Findings

MuSR improved by 30 percentage points for both models, suggesting that explicit candidate-wise reasoning is useful for short murder mystery cases.

DetectBench improved for DeepSeek but not MiniMax. The next full reproduction should evaluate evidence coverage, not only final-answer accuracy.

DetectiveQA improved to 100% for both models, but this result should be interpreted cautiously because the local files contain annotations rather than full novel contexts.

TurnaboutLLM remained at 0% despite valid parse outputs. A common error pattern is pair-order confusion, such as predicting `[15, 5]` when the gold pair is `[5, 15]`. This benchmark needs stronger pair-format control and partial-credit metrics.

## Next Steps

1. Run full MuSR `murder_mystery` with 250 samples.
2. Run full DetectBench `test-hard` with 300 samples.
3. Add evidence coverage evaluation for DetectBench.
4. Add partial metrics for TurnaboutLLM: evidence accuracy, testimony accuracy, pair-order error.
5. Test paper-inspired skills combined with `structured_memory_stub`.

