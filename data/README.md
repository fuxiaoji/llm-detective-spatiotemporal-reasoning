# Data

This folder is for datasets used by the project.

## Target data sources

## Current local status

Downloaded and usable:

- `MuSR/`
  - Main file: `MuSR/datasets/murder_mystery.json`
  - Checked: 250 murder mystery samples.
- `DetectBench/`
  - Main files: `DetectBench/DetectBench_eng_v1.3/*.jsonl`
  - Checked: train/dev/test/test-hard/test-distract JSONL files exist.
- `DetectiveQA/`
  - Repository downloaded. The repo mostly contains scripts and benchmark access utilities.
- `llm-mysteries/`
  - Repository downloaded. Useful as a reference implementation for mystery-solving and belief graph ideas.
- `TurnaboutLLM/`
  - Zip downloaded at `repo_zips/TurnaboutLLM.zip`.
  - Partially extracted. Core files `TurnaboutLLM/data/AA_integrated_dataset.json` and `TurnaboutLLM/data/DR_integrate_dataset.json` exist.
  - Some Chinese Ace Attorney files failed to extract because of filename encoding issues; use the zip directly or unzip with GUI/encoding-aware tooling if needed.

Original zip archives are kept in `repo_zips/`.

### 1. MuSR

- Paper: `../papers/2310.16049_MuSR_Multistep_Soft_Reasoning.pdf`
- HuggingFace: `TAUR-Lab/MuSR`
- GitHub: `https://github.com/Zayne-sprague/MuSR`
- Use: first public benchmark for murder mystery style multi-step reasoning.

### 2. DetectBench

- Paper: `../papers/2406.12641_DetectBench.pdf`
- GitHub: `https://github.com/MikeGu721/DetectBench`
- ACL data zip: `https://aclanthology.org/2024.findings-emnlp.11.data.zip`
- Use: implicit evidence detection and multi-hop detective reasoning.

### 3. DetectiveQA

- Paper: `../papers/2409.02465_DetectiveQA.pdf`
- GitHub: `https://github.com/Phospheneser/DetectiveQA`
- Use: long-context detective novel QA; best for small qualitative case studies.

### 4. TurnaboutLLM

- Paper page: `https://aclanthology.org/2025.emnlp-main.101/`
- GitHub: `https://github.com/zharry29/turnabout_llm`
- Use: contradiction detection from detective-game style evidence and testimony.

### 5. LLM Mysteries

- GitHub: `https://github.com/metareflection/llm-mysteries`
- Use: supplementary reference for LLM mystery-solving experiments.

## Suggested usage

Use public datasets for initial baselines, but create a controlled synthetic dataset for the main contribution.

Recommended experimental split:

- MuSR murder mystery: public baseline
- DetectBench: evidence discovery baseline
- Synthetic dynamic detective cases: main controlled evaluation
- DetectiveQA: small long-context qualitative analysis

## Why synthetic data is needed

The proposed project needs gold labels for:

- timeline state
- person location
- object location
- testimony contradiction
- alibi validity
- final culprit

Most public detective datasets only label final answers or evidence spans, not full spatio-temporal state graphs.
