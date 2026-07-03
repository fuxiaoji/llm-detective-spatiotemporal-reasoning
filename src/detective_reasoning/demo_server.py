from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .registry import (
    list_dataset_specs,
    list_method_specs,
    list_skill_specs,
    load_registered_dataset,
)
from .runner import RunConfig, run_samples


MODEL_PRESETS = [
    {
        "id": "deepseek-v4-flash",
        "label": "DeepSeek V4 Flash",
        "provider": "openai",
        "model": "deepseek-v4-flash",
        "base_url": "https://api.deepseek.com",
        "thinking": "disabled",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "deepseek-v4-flash-thinking",
        "label": "DeepSeek V4 Flash Thinking",
        "provider": "openai",
        "model": "deepseek-v4-flash",
        "base_url": "https://api.deepseek.com",
        "thinking": "enabled",
        "reasoning_effort": "high",
        "max_tokens": "4096",
    },
    {
        "id": "deepseek-v4-pro",
        "label": "DeepSeek V4 Pro",
        "provider": "openai",
        "model": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com",
        "thinking": "disabled",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "deepseek-v4-pro-thinking",
        "label": "DeepSeek V4 Pro Thinking",
        "provider": "openai",
        "model": "deepseek-v4-pro",
        "base_url": "https://api.deepseek.com",
        "thinking": "enabled",
        "reasoning_effort": "high",
        "max_tokens": "4096",
    },
    {
        "id": "gpt-4o-mini",
        "label": "OpenAI GPT-4o mini",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "gpt-4.1-mini",
        "label": "OpenAI GPT-4.1 mini",
        "provider": "openai",
        "model": "gpt-4.1-mini",
        "base_url": "https://api.openai.com/v1",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "qwen-plus",
        "label": "Qwen Plus",
        "provider": "openai",
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "moonshot-v1-8k",
        "label": "Moonshot v1 8k",
        "provider": "openai",
        "model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "mock",
        "label": "Local Mock",
        "provider": "mock",
        "model": "mock",
        "base_url": "",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "800",
    },
    {
        "id": "deepseek-chat-legacy",
        "label": "Legacy deepseek-chat",
        "provider": "openai",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "1200",
    },
    {
        "id": "deepseek-reasoner-legacy",
        "label": "Legacy deepseek-reasoner",
        "provider": "openai",
        "model": "deepseek-reasoner",
        "base_url": "https://api.deepseek.com",
        "thinking": "",
        "reasoning_effort": "",
        "max_tokens": "4096",
    },
]


def _page(body: str) -> bytes:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Detective Reasoning Demo</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 28px; line-height: 1.5; color: #172033; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .card {{ border: 1px solid #d8dee9; border-radius: 12px; padding: 16px; background: #fff; }}
    .muted {{ color: #607086; }}
    .ok {{ color: #087f5b; font-weight: 700; }}
    .bad {{ color: #c92a2a; font-weight: 700; }}
    pre {{ white-space: pre-wrap; background: #f6f8fa; padding: 12px; border-radius: 8px; }}
    select, input {{ margin: 4px; }}
    button {{ margin: 4px; padding: 6px 12px; }}
    label {{ display: inline-block; margin: 4px 8px 4px 0; }}
  </style>
  <script>
    const MODEL_PRESETS = {json.dumps(MODEL_PRESETS)};
    function applyModelPreset() {{
      const presetId = document.getElementById("model-preset").value;
      const preset = MODEL_PRESETS.find((item) => item.id === presetId);
      if (!preset) return;
      document.getElementById("provider-input").value = preset.provider;
      document.getElementById("model-input").value = preset.model;
      document.getElementById("base-url-input").value = preset.base_url;
      document.getElementById("thinking-input").value = preset.thinking || "";
      document.getElementById("reasoning-effort-input").value = preset.reasoning_effort || "";
      document.getElementById("max-tokens-input").value = preset.max_tokens || "1200";
    }}
  </script>
</head>
<body>
{body}
</body>
</html>""".encode("utf-8")


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        self._handle(qs)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8") if length else ""
        qs = parse_qs(body)
        self._handle(qs)

    def _handle(self, qs: dict[str, list[str]]) -> None:
        dataset = qs.get("dataset", ["musr"])[0]
        split = qs.get("split", ["murder_mystery"])[0]
        dataset_split = qs.get("dataset_split", [])
        if dataset_split and "|" in dataset_split[0]:
            dataset, split = dataset_split[0].split("|", 1)
        method = qs.get("method", ["direct"])[0]
        provider = qs.get("provider", ["openai"])[0]
        model = qs.get("model", ["deepseek-v4-flash"])[0]
        base_url = qs.get("base_url", ["https://api.deepseek.com"])[0]
        thinking = qs.get("thinking", ["disabled"])[0]
        reasoning_effort = qs.get("reasoning_effort", [""])[0]
        api_key = qs.get("api_key", [""])[0]
        max_tokens = int(qs.get("max_tokens", ["800"])[0] or 800)
        selected_skills = qs.get("skills", [])
        index = int(qs.get("index", ["0"])[0] or 0)
        load_error = ""
        sample = None
        try:
            samples = load_registered_dataset(dataset, split, limit=max(index + 1, 1))
            sample = samples[min(index, len(samples) - 1)]
        except Exception as e:
            load_error = str(e)
        result_html = ""
        if sample is not None and qs.get("run", ["0"])[0] == "1":
            try:
                artifacts = run_samples(
                    [sample],
                    RunConfig(
                        dataset=dataset,
                        split=split,
                        method=method,
                        skills=selected_skills,
                        provider=provider,
                        model=model,
                        base_url=base_url or None,
                        thinking=thinking or None,
                        reasoning_effort=reasoning_effort or None,
                        api_key=api_key or None,
                        max_tokens=max_tokens,
                        limit=1,
                    ),
                )
                pred = artifacts.predictions[0]
                correct_class = "ok" if pred.correct else "bad"
                reasoning_content = pred.intermediate.get("reasoning_content")
                empty_answer_warning = (
                    '<p class="bad"><b>No final answer content returned.</b> The model produced reasoning_content but no final content. Increase Max tokens, use a non-thinking preset, or ask for a shorter answer.</p>'
                    if reasoning_content and not pred.raw_output
                    else ""
                )
                reasoning_html = (
                    f"<h3>DeepSeek Reasoning Content</h3><pre>{html.escape(reasoning_content)}</pre>"
                    if reasoning_content
                    else '<h3>DeepSeek Reasoning Content</h3><p class="muted">No reasoning_content was returned. For DeepSeek V4, choose a Thinking preset or set Thinking = enabled.</p>'
                )
                result_html = f"""
                <div class="card">
                  <h2>Result</h2>
                  <p><b>Run ID:</b> {html.escape(artifacts.run_id)}</p>
                  <p><b>Saved to:</b> {html.escape(artifacts.run_dir)}</p>
                  <p><b>Model config:</b> provider={html.escape(provider)}, model={html.escape(model)}, thinking={html.escape(thinking or 'provider default')}, reasoning_effort={html.escape(reasoning_effort or 'none')}</p>
                  {empty_answer_warning}
                  <p><b>Prediction:</b> {html.escape(str(pred.prediction))}</p>
                  <p><b>Gold:</b> {html.escape(str(pred.gold))}</p>
                  <p><b>Correct:</b> <span class="{correct_class}">{pred.correct}</span></p>
                  <p><b>Parse error:</b> {html.escape(str(pred.parse_error))}</p>
                  {reasoning_html}
                  <h3>Tool / Skill Trace</h3><pre>{html.escape(json.dumps(pred.intermediate, ensure_ascii=False, indent=2))}</pre>
                  <h3>Visible Model Output</h3><pre>{html.escape(pred.raw_output)}</pre>
                  <h3>Prompt</h3><pre>{html.escape(pred.prompt)}</pre>
                </div>
                """
            except Exception as e:
                result_html = f"""
                <div class="card">
                  <h2>Run error</h2>
                  <pre>{html.escape(str(e))}</pre>
                </div>
                """
        dataset_options = "\n".join(
            (
                f"<option value='{s['name']}|{s['split']}' "
                f"{'selected' if s['name'] == dataset and s['split'] == split else ''}>"
                f"{html.escape(s['description'])}</option>"
            )
            for s in list_dataset_specs()
        )
        method_options = "".join(
            f'<option value="{m["name"]}" {("selected" if m["name"] == method else "")}>'
            f'{html.escape(m["name"])} - {html.escape(m["description"])}</option>'
            for m in list_method_specs()
        )
        skill_options = "".join(
            f'<label><input type="checkbox" name="skills" value="{html.escape(s["name"])}" '
            f'{("checked" if s["name"] in selected_skills else "")}> '
            f'{html.escape(s["name"])}</label>'
            for s in list_skill_specs()
        )
        preset_options = "".join(
            (
                f'<option value="{html.escape(preset["id"])}" '
                f'{"selected" if preset["provider"] == provider and preset["model"] == model and preset["base_url"] == base_url and preset["thinking"] == thinking and preset["reasoning_effort"] == reasoning_effort else ""}>'
                f'{html.escape(preset["label"])}</option>'
            )
            for preset in MODEL_PRESETS
        )
        body = f"""
        <h1>Detective Reasoning Demo</h1>
        <p class="muted">Modular local GUI for dataset browsing, skill-assisted prompting, model calls, and saved run traces.</p>
        <form method="post" action="/">
          <div class="card">
            <label>Dataset / split:
              <select name="dataset_split" onchange="const [d,s]=this.value.split('|'); document.getElementById('dataset-input').value=d; document.getElementById('split-input').value=s;">
                {dataset_options}
              </select>
            </label>
            <input type="hidden" name="dataset" id="dataset-input" value="{html.escape(dataset)}">
            <input type="hidden" name="split" id="split-input" value="{html.escape(split)}">
            <label>Index <input name="index" value="{index}" size="4"></label>
            <label>Method <select name="method">{method_options}</select></label>
            <div><b>Skills:</b> {skill_options}</div>
            <label>Model preset
              <select id="model-preset" onchange="applyModelPreset()">{preset_options}</select>
            </label>
            <label>Provider <input id="provider-input" name="provider" value="{html.escape(provider)}" size="8"></label>
            <label>Model <input id="model-input" name="model" value="{html.escape(model)}" size="22"></label>
            <label>Base URL <input id="base-url-input" name="base_url" value="{html.escape(base_url)}" size="42"></label>
            <label>API key <input type="password" name="api_key" value="" size="42" autocomplete="off" placeholder="Optional; used only for this request"></label>
            <label>Thinking
              <select id="thinking-input" name="thinking">
                <option value="" {"selected" if thinking == "" else ""}>provider default</option>
                <option value="disabled" {"selected" if thinking == "disabled" else ""}>disabled</option>
                <option value="enabled" {"selected" if thinking == "enabled" else ""}>enabled</option>
              </select>
            </label>
            <label>Reasoning effort
              <select id="reasoning-effort-input" name="reasoning_effort">
                <option value="" {"selected" if reasoning_effort == "" else ""}>none</option>
                <option value="high" {"selected" if reasoning_effort == "high" else ""}>high</option>
                <option value="max" {"selected" if reasoning_effort == "max" else ""}>max</option>
              </select>
            </label>
            <label>Max tokens <input id="max-tokens-input" name="max_tokens" value="{max_tokens}" size="5"></label>
            <button name="run" value="0">Load sample</button>
            <button name="run" value="1">Run and save</button>
            <p class="muted">API key can be pasted here for a one-off run or supplied through OPENAI_API_KEY before starting the server. It is not saved to run files.</p>
          </div>
        </form>
        {f'<div class="card"><h2>Load error</h2><pre>{html.escape(load_error)}</pre></div>' if load_error else ''}
        {'' if sample is not None else '<p class="muted">Choose another dataset/split or return to the home URL.</p>'}
        {'' if sample is None else f'''
        <div class="grid">
          <div class="card">
            <h2>Sample</h2>
            <p><b>ID:</b> {html.escape(sample.id)}</p>
            <p><b>Question:</b> {html.escape(sample.question)}</p>
            <h3>Options</h3><pre>{html.escape(json.dumps(sample.options, ensure_ascii=False, indent=2))}</pre>
            <h3>Context</h3><pre>{html.escape((sample.context or '')[:5000])}</pre>
          </div>
          <div class="card">
            <h2>Gold / Evidence</h2>
            <pre>{html.escape(json.dumps({'answer': sample.answer, 'evidence': sample.evidence, 'reasoning': sample.reasoning}, ensure_ascii=False, indent=2)[:5000])}</pre>
          </div>
        </div>
        '''}
        {result_html}
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(_page(body))


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), DemoHandler)
    print("Demo running at http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
