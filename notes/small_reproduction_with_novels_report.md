# Small Reproduction Report with DetectiveQA Novel Context

Generated on 2026-07-03  
Experiment directory: `runs/small_repro_with_novels_20260703/`  
This report supersedes the earlier DetectiveQA annotation-only smoke test.

## 1. What changed

The earlier DetectiveQA run only used annotation files: questions, options, gold answers, and human reasoning. That was useful for testing loaders and evaluators, but it was not a real long-context detective reading test.

This run downloads the novel text needed by the first 10 English human-annotated DetectiveQA samples and updates the loader:

- Local novel files:
  - `data/DetectiveQA/hf_dataset/novel_data_en/117-阳光下的罪恶-阿加莎克里斯蒂.txt`
  - `data/DetectiveQA/hf_dataset/novel_data_en/118-顺水推舟-阿加莎克里斯蒂.txt`
- Code path: `src/detective_reasoning/datasets.py`
- Loading rule: find the novel by `novel_id`, then include paragraphs up to the question's `answer_position`.
- Context cap: keep the final 24,000 characters to avoid excessive API context size.
- Metadata saved per sample: `context_status`, `novel_text_path`, `answer_position`, `paragraphs_used`, `context_chars`, and `truncated_from_tail`.

This is still not a full paper-level reproduction: each condition uses only 10 samples, and DetectiveQA is truncated to 24,000 characters. However, it is now a real context-based smoke test rather than annotation-only evaluation.

## 2. Experimental Setup

Each dataset was evaluated with 10 samples, two models, and two conditions:

- Datasets:
  - MuSR `murder_mystery`
  - DetectBench `test-hard`
  - DetectiveQA `en_human`
  - TurnaboutLLM `AA`
- Models:
  - DeepSeek V4 Flash: `deepseek-v4-flash`
  - MiniMax: `MiniMax-M3`
- Conditions:
  - `baseline_direct`: direct answer prompting.
  - `paper_skill`: a task-specific prompt/skill inspired by the relevant paper.
- Saved outputs:
  - `manifest.json`
  - `predictions.jsonl`
  - `summary.csv`
  - `runs/small_repro_with_novels_20260703/experiment_index.json`

## 3. Results

| Dataset | Model | Condition | Skill | Correct | Accuracy | Total tokens | Run ID |
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

## 4. Main Observations

On MuSR, `musr_cot_plus` improved both models: DeepSeek went from 50% to 80%, and MiniMax went from 70% to 90%. This supports the usefulness of explicitly organizing suspects, motives, evidence, timelines, and final consistency checks in short mystery reasoning.

On DetectBench, DeepSeek improved from 80% to 90%, while MiniMax dropped from 80% to 70%. This suggests that a longer or more structured prompt can help one model but distract another. Future experiments should use ablations rather than treating one large skill as a single black box.

On DetectiveQA, the model now receives novel context. DeepSeek scored 100% in both conditions, and MiniMax improved from 90% to 100% with the stepwise skill. Because this uses only 10 samples from two novels, it should be treated as a successful data-path and long-context smoke test, not as a strong benchmark result.

On TurnaboutLLM, all conditions scored 0%. The runs did not fail; predictions were parsed. The issue is that this task requires exact evidence-testimony pair selection, and the current prompt/evaluator setup does not yet reproduce the paper's action space and candidate-pair constraints. Turnabout should be handled separately before being used as a main benchmark.

## 5. Implications for the Research Proposal

A stronger research question is not simply "does a skill improve accuracy?" A more interesting and feasible question is:

**When does an external structured memory or evidence bank improve detective reasoning, and when does it introduce noise?**

Candidate modules:

- `evidence_card`: extract characters, places, times, events, and physical clues.
- `timeline_memory`: organize events chronologically.
- `contradiction_check`: compare testimony and evidence for conflicts.
- `answer_verifier`: check whether the final answer is supported by evidence.
- `retrieval_context`: retrieve relevant novel passages instead of fixed tail truncation.

For the first formal experiments, MuSR and DetectBench are the best main benchmarks. DetectiveQA should be used as a second-stage long-context case study. TurnaboutLLM is valuable but needs a dedicated candidate-pair interface first.

## 6. Recommended Next Steps

1. Add retrieval-based DetectiveQA context selection instead of fixed 24,000-character tail truncation.
2. Run ablations on MuSR and DetectBench: baseline, CoT, evidence card, timeline, contradiction check, and verifier.
3. Scale from 10 samples to 50 samples or full splits once the method is stable.
4. Rebuild TurnaboutLLM as a candidate-pair selection task before using it in the main comparison.
5. Expose DetectiveQA context metadata in the GUI, including whether novel text was loaded, which novel was used, and how much context was truncated.
