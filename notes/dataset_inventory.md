# Detective Reasoning Dataset Inventory

Updated: 2026-06-26

## Summary

This note inventories the detective-reasoning datasets relevant to the current project:

> External structured evidence memory / skill-assisted test-time reasoning for LLM detective tasks.

Scope is limited to detective and narrative reasoning resources:

- MuSR
- DetectBench
- DetectiveQA
- TurnaboutLLM
- LLM Mysteries

Spatial navigation and embodied-memory datasets are intentionally excluded from this first pass.

## Overview

| Paper / Project | Dataset | Open? | Local status | Recommended use |
|---|---|---:|---|---|
| MuSR | MuSR murder mystery / object placements / team allocation | Yes | Downloaded and readable | Main baseline for murder mystery accuracy |
| DetectBench | DetectBench English v1.3 | Yes | Downloaded and readable | Main baseline for implicit evidence discovery |
| DetectiveQA | DetectiveQA annotations | Yes, HuggingFace | Annotation JSON downloaded; full novel text not present in downloaded files | Long-context qualitative case study after text availability is resolved |
| TurnaboutLLM | Ace Attorney + Danganronpa contradiction dataset | Yes | Core JSON readable; source/eval scripts restored from zip | Contradiction / testimony-evidence conflict experiments |
| LLM Mysteries | Mystery-solving reference code + small task data | Yes | Repo downloaded and readable | Reference implementation for belief graph / evidence graph demo |

## 1. MuSR

### Source

- Paper: `papers/2310.16049_MuSR_Multistep_Soft_Reasoning.pdf`
- GitHub: `https://github.com/Zayne-sprague/MuSR`
- Local repo: `data/MuSR/`

### Local data files

| File | Count | Role |
|---|---:|---|
| `data/MuSR/datasets/murder_mystery.json` | 250 | Main detective baseline |
| `data/MuSR/datasets/object_placements.json` | 64 | Spatial / object tracking baseline |
| `data/MuSR/datasets/team_allocation.json` | 250 | Social reasoning baseline |

### Schema

Top-level file structure:

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

Unified mapping:

| Unified field | Source |
|---|---|
| `id` | generated from file name + index |
| `context` | `context` |
| `question` | `questions[0].question` |
| `options` | `questions[0].choices` |
| `answer` | `questions[0].answer` |
| `evidence` | not directly annotated; can derive from `intermediate_trees` |
| `reasoning` | `intermediate_trees`, `intermediate_data` |
| `metadata` | domain name, original index |

### Sample preview

From `murder_mystery.json`:

```text
Context: In an adrenaline inducing bungee jumping site, Mack's thrill-seeking adventure came to a gruesome end by a nunchaku...
Question: Who is the most likely murderer?
Choices: ["Mackenzie", "Ana"]
Answer index: 0
```

### Usefulness

| Evaluation target | Fit |
|---|---|
| Final answer accuracy | Strong |
| Evidence coverage | Medium; requires intermediate tree processing |
| Reasoning step evaluation | Medium |
| Contradiction detection | Weak |
| Long-context case study | Weak; stories are shorter than novel-length contexts |

### Recommendation

Use MuSR murder mystery as the **first main benchmark**. It is small, clean, already local, and directly measures culprit selection. It is ideal for comparing Direct, CoT, Reflection, Self-Consistency, and lightweight evidence cards.

## 2. DetectBench

### Source

- Paper: `papers/2406.12641_DetectBench.pdf`
- GitHub: `https://github.com/MikeGu721/DetectBench`
- ACL data zip: `https://aclanthology.org/2024.findings-emnlp.11.data.zip`
- Local repo/data: `data/DetectBench/`

### Local data files

| File | Count | Notes |
|---|---:|---|
| `data/DetectBench/DetectBench_eng_v1.3/train.jsonl` | 367 | Train split |
| `data/DetectBench/DetectBench_eng_v1.3/dev.jsonl` | 1764 | Dev split |
| `data/DetectBench/DetectBench_eng_v1.3/test.jsonl` | 1196 | Normal test |
| `data/DetectBench/DetectBench_eng_v1.3/test-hard.jsonl` | 300 | Hard split: more evidence and reasoning jumps |
| `data/DetectBench/DetectBench_eng_v1.3/test-distract.jsonl` | 300 | Distractor / long-context split |

### Schema

Most splits:

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

`test-distract.jsonl` differs:

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

Unified mapping:

| Unified field | Source |
|---|---|
| `id` | `id`, or generated for `test-distract` |
| `context` | `context` |
| `question` | `question` |
| `options` | `options` |
| `answer` | `answer` |
| `evidence` | `clue_graph.evidence` or `reasoning_process.evidence` |
| `reasoning` | `clue_graph.multi_hop_reasoning` or `reasoning_process` |
| `metadata` | split name, dataset version |

### Sample preview

From `test-hard.jsonl`:

```text
Question: How can you divide 24 pounds of oil into three equal parts using containers of 5, 11, and 13 pounds?
Answer index: 0
Evidence: 24 jin of oil -> Fill the 13 jin container -> Remaining 11 jin of oil ...
```

### Usefulness

| Evaluation target | Fit |
|---|---|
| Final answer accuracy | Strong |
| Evidence coverage | Strong |
| Reasoning step evaluation | Strong |
| Contradiction detection | Weak to medium |
| Long-context case study | Medium; `test-distract` is long |

### Recommendation

Use DetectBench as the **first evidence-discovery benchmark**. `test-hard.jsonl` is especially useful for testing whether structured evidence cards or critic checklists improve evidence identification and multi-hop reasoning.

## 3. DetectiveQA

### Source

- Paper: `papers/2409.02465_DetectiveQA.pdf`
- GitHub scripts: `https://github.com/Phospheneser/DetectiveQA`
- HuggingFace dataset: `https://huggingface.co/datasets/Phospheneser/DetectiveQA`
- Local repo: `data/DetectiveQA/`
- Local downloaded HF annotations: `data/DetectiveQA/hf_dataset/`

### Local status

The GitHub repo only contained scripts and README files. The HuggingFace dataset is public and not gated. Annotation JSON files were downloaded into:

```text
data/DetectiveQA/hf_dataset/
```

Downloaded annotation counts:

| Folder | Files | Questions | Notes |
|---|---:|---:|---|
| `anno_data_en/AIsup_anno` | 62 | 446 | English AI-supported annotations |
| `anno_data_en/human_anno` | 24 | 154 | English human annotations |
| `anno_data_zh/AIsup_anno` | 62 | 446 | Chinese AI-supported annotations |
| `anno_data_zh/human_anno` | 24 | 154 | Chinese human annotations |

Important caveat:

The downloaded JSON files contain questions, answers, reasoning steps, clue positions, and answer positions, but they do **not** appear to include the full novel text itself. For full long-context model evaluation, the original novel contents must be located or reconstructed through the official scripts / dataset workflow.

### Schema

Each file is a list with one novel-level object:

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

Unified mapping:

| Unified field | Source |
|---|---|
| `id` | novel id + question index |
| `context` | not present in downloaded annotation files |
| `question` | `questions[].question` |
| `options` | `questions[].options` |
| `answer` | `questions[].answer` |
| `evidence` | `questions[].reasoning` + `clue_position` |
| `reasoning` | `questions[].reasoning` |
| `metadata` | language, annotation type, novel id, paragraph count |

### Sample preview

From `anno_data_en/human_anno/117.json`:

```text
Question: Aveline instructed Polo not to tell anyone when she left, which implies that:
Options: A rendezvous / swim at the beach / buy clothes / enjoys being alone
Answer: A
Reasoning: multiple reference steps explaining the hidden relationship and motive for secrecy.
```

### Usefulness

| Evaluation target | Fit |
|---|---|
| Final answer accuracy | Medium; requires context text for real evaluation |
| Evidence coverage | Strong if using reference reasoning annotations |
| Reasoning step evaluation | Strong |
| Contradiction detection | Medium |
| Long-context case study | Strong, after full text is available |

### Recommendation

Use DetectiveQA in **phase 2** as a long-context qualitative case study. It is valuable for step-wise reasoning evaluation, but not ideal for the first batch baseline until full novel contexts are available locally.

## 4. TurnaboutLLM

### Source

- GitHub: `https://github.com/zharry29/turnabout_llm`
- Local repo/data: `data/TurnaboutLLM/`

### Local data files

| File | Count | Role |
|---|---:|---|
| `data/TurnaboutLLM/data/AA_integrated_dataset.json` | 200 | Ace Attorney contradiction examples |
| `data/TurnaboutLLM/data/DR_integrate_dataset.json` | 31 | Danganronpa contradiction examples |
| `data/TurnaboutLLM/source/run_models.py` | exists | Model inference script |
| `data/TurnaboutLLM/source/evaluate.py` | exists | Evaluation script |
| `data/TurnaboutLLM/eval/*_report.json` | 26 reports | Existing model evaluation reports |
| `data/TurnaboutLLM/eval/eval.csv` | exists | Aggregated evaluation table |

`source/` and `eval/` were restored from `data/repo_zips/TurnaboutLLM.zip`.

### Schema

Integrated dataset item:

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

Unified mapping:

| Unified field | Source |
|---|---|
| `id` | `source` |
| `context` | `input.summarized_context` or `input.full_input` |
| `question` | generated: find contradictory evidence-testimony pair |
| `options` | implicit Cartesian product of evidences and testimonies |
| `answer` | `output` |
| `evidence` | `input.evidence` |
| `reasoning` | source data / evaluation reports if needed |
| `metadata` | game source, prompt context setting |

### Sample preview

From `AA_integrated_dataset.json`:

```text
Source: 2-4-2_Farewell,_My_Turnabout_1
Evidence: [0] Attorney's Badge ... [1] Maya's Magatama ...
Testimonies: witness statements in indexed form
Output: [[5, 15]]
```

Existing eval summary includes fields such as:

```text
overall_accuracy, overall_evidence_accuracy, overall_testimony_accuracy,
temporal_accuracy, spatial_accuracy, causal_accuracy, physical_accuracy
```

### Usefulness

| Evaluation target | Fit |
|---|---|
| Final answer accuracy | Strong, but answer space is pair selection |
| Evidence coverage | Strong |
| Reasoning step evaluation | Medium |
| Contradiction detection | Strong |
| Long-context case study | Medium |

### Recommendation

Use TurnaboutLLM as a **contradiction-focused auxiliary benchmark**. It is especially relevant for evidence-vs-testimony conflict, temporal contradiction, and spatial contradiction checks.

## 5. LLM Mysteries

### Source

- GitHub: `https://github.com/metareflection/llm-mysteries`
- Local repo: `data/llm-mysteries/`

### Local files of interest

| File | Role |
|---|---|
| `data/llm-mysteries/tiny.json` | Small mystery QA task |
| `data/llm-mysteries/load_musr.py` | MuSR loader reference |
| `data/llm-mysteries/main_musr.py` | MuSR run reference |
| `data/llm-mysteries/main_detect_bench_prompt.py` | DetectBench-style prompt reference |
| `data/llm-mysteries/belief_graph.py` | Belief graph extraction reference |
| `data/llm-mysteries/graph.py` | Evidence graph style reasoning reference |

### Schema / role

`tiny.json` is a BIG-Bench style task descriptor for minute mysteries. It is not as directly useful as MuSR or DetectBench for first-stage reproduction, but the repo contains useful reference code for:

- asking models for incriminating / exonerating evidence,
- building belief graphs,
- using symbolic consistency checks,
- adapting DetectBench prompts.

### Usefulness

| Evaluation target | Fit |
|---|---|
| Final answer accuracy | Medium |
| Evidence coverage | Medium |
| Reasoning step evaluation | Medium |
| Contradiction detection | Medium |
| Long-context case study | Weak |

### Recommendation

Use LLM Mysteries as a **reference implementation**, not as the first main benchmark. It is useful when designing the project demo and evidence graph / belief graph skill.

## First Unified Loader Priority

Recommended order:

1. **MuSR murder mystery**
   - easiest to load,
   - clean multiple-choice culprit prediction,
   - direct baseline target.

2. **DetectBench test-hard / test**
   - strongest evidence discovery labels,
   - useful clue graph,
   - directly supports evidence-card experiments.

3. **TurnaboutLLM**
   - best for contradiction detection,
   - different answer format requiring pair-selection evaluation.

4. **DetectiveQA**
   - valuable but should wait until full novel contexts are locally available.

5. **LLM Mysteries**
   - reference code and demo inspiration.

## Suggested Next Step

Build a unified dataset loader with this minimal sample schema:

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

Start with:

- `load_musr_murder_mystery()`
- `load_detectbench(split="test-hard")`

Then add:

- `load_turnabout(source="AA")`
- `load_detectiveqa_annotations(lang="en", anno="human")`

## Verification Checklist

- MuSR murder mystery readable: yes, 250 samples.
- DetectBench five JSONL splits readable: yes.
- DetectBench Test-Hard readable: yes, 300 samples.
- TurnaboutLLM core JSON readable: yes, 200 AA + 31 DR samples.
- TurnaboutLLM source/eval restored: yes.
- DetectiveQA HuggingFace annotation files downloaded: yes, 172 JSON files.
- DetectiveQA readable sample: yes.
- DetectiveQA full novel context: not present in downloaded annotation files; needs follow-up.

