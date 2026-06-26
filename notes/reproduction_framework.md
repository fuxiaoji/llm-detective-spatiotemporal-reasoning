# Reproduction Framework

This project now includes a minimal, dependency-free framework for reproducing
detective-reasoning baselines and inspecting model behavior.

## Entry Points

List supported datasets:

```bash
python3 -m src.detective_reasoning.cli list-datasets
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

## Output

Batch evaluation writes:

- JSONL with one record per sample
- CSV summary with accuracy, parse errors, and token usage

Default output directory:

```text
outputs/
```

This directory is git-ignored.

