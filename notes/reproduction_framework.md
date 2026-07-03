# Reproduction Framework

This project now includes a modular, dependency-free framework for reproducing
detective-reasoning baselines, testing plug-in style skills, and saving
auditable experiment traces.

## Entry Points

List supported datasets:

```bash
python3 -m src.detective_reasoning.cli list-datasets
```

List supported methods and skills:

```bash
python3 -m src.detective_reasoning.cli list-methods
python3 -m src.detective_reasoning.cli list-skills
```

Peek at normalized samples:

```bash
python3 -m src.detective_reasoning.cli peek --dataset musr --split murder_mystery --limit 2
python3 -m src.detective_reasoning.cli peek --dataset detectbench --split test-hard --limit 2
```

Run a batch evaluation with the mock model:

```bash
python3 -m src.detective_reasoning.cli eval \
  --dataset musr \
  --split murder_mystery \
  --method cot \
  --skills dummy_skill \
  --provider mock \
  --model mock \
  --limit 10
```

Run an OpenAI-compatible model:

```bash
OPENAI_API_KEY=... python3 -m src.detective_reasoning.cli eval \
  --dataset detectbench \
  --split test-hard \
  --method evidence_card \
  --skills external_evidence_bank,structured_memory_stub \
  --provider openai \
  --model gpt-4o-mini \
  --limit 20
```

Start the local demo:

```bash
python3 -m src.detective_reasoning.demo_server
```

Then open:

```text
http://127.0.0.1:8765
```

## Supported Datasets

- MuSR: `murder_mystery`, `object_placements`, `team_allocation`
- DetectBench: `train`, `dev`, `test`, `test-hard`, `test-distract`
- DetectiveQA annotations: `en_human`, `en_ai`, `zh_human`, `zh_ai`
- TurnaboutLLM: `AA`, `DR`

## Supported Methods

- `direct`
- `cot`
- `reflection`
- `evidence_card`
- `critic_checklist`

## Supported Skills

- `dummy_skill`: no-op registry test skill.
- `external_evidence_bank`: attaches available structured evidence and reasoning annotations.
- `structured_memory_stub`: asks the model to build a temporary timeline/location/entity memory.

New skills should be registered in `src/detective_reasoning/registry.py`.

## Saved Runs

Both GUI single-question tests and CLI batch evaluations write:

- `manifest.json`: run config, run id, timestamp, and summary.
- `predictions.jsonl`: one record per sample, including prompt, visible model output, tool traces, prediction, gold answer, correctness, parse error, and token usage.
- `summary.csv`: accuracy, parse errors, and token usage.

Default output directory:

```text
runs/<run_id>/
```

This directory is git-ignored. Saved reasoning contains only model-visible
outputs and tool traces; hidden model reasoning is not captured.

## GUI

The local browser GUI supports dataset/split selection, sample browsing, model
selection, method selection, skill selection, and run saving. Start it with:

```bash
python3 -m src.detective_reasoning.demo_server
```
