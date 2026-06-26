# LLM Detective Spatio-Temporal Reasoning

Project folder for the summer research idea:

> Test-time compute allocation for detective reasoning with structured spatio-temporal evidence graphs.

## Folder structure

- `papers/`: downloaded related papers.
- `data/`: public datasets and dataset download notes.
- `scripts/`: utility scripts, including dataset download.
- `src/`: project source code.
- `notes/`: reading notes and experiment plans.

## Documentation convention

Project-facing documents should be kept in both English and Chinese when they
are meant to be reused for reports, demos, or research planning. For example:

- English: `notes/dataset_inventory.md`
- Chinese: `notes/dataset_inventory_zh.md`

## Reproduction toolkit

The repository includes a minimal dependency-free toolkit for dataset inspection,
batch baseline reproduction, and an interactive local demo.

List available datasets:

```bash
python3 -m src.detective_reasoning.cli list-datasets
```

Peek at normalized samples:

```bash
python3 -m src.detective_reasoning.cli peek --dataset musr --split murder_mystery --limit 2
python3 -m src.detective_reasoning.cli peek --dataset detectbench --split test-hard --limit 2
```

Run a smoke-test batch evaluation with the mock model:

```bash
python3 -m src.detective_reasoning.cli eval \
  --dataset musr \
  --split murder_mystery \
  --method cot \
  --provider mock \
  --model mock \
  --limit 10
```

Run the local demo:

```bash
python3 -m src.detective_reasoning.demo_server
```

Then open `http://127.0.0.1:8765`.

For a Chinese guide, see `notes/reproduction_framework_zh.md`.

## Current research angle

The core question is not simply whether LLMs can solve detective stories.

Instead:

> When solving detective narratives, how should an LLM allocate test-time reasoning effort across CoT, reflection, self-consistency, retrieval, and structured spatio-temporal evidence memory?

Potential contribution:

1. Analyze where CoT fails in detective reasoning: timeline, location, object state, testimony contradiction, alibi reasoning.
2. Build a spatio-temporal evidence graph skill for structured state tracking.
3. Compare direct answering, CoT, structured CoT, self-consistency, RAG, and skill-assisted reasoning under accuracy-cost trade-offs.

## Next step

Run:

```bash
./scripts/download_data.sh
```

If GitHub or HuggingFace is slow, rerun the script later; it skips existing completed folders.
