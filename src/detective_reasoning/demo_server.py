from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .datasets import load_dataset, list_dataset_specs
from .evaluation import run_method
from .models import ModelConfig, make_model_client


def _page(body: str) -> bytes:
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Detective Reasoning Demo</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; line-height: 1.5; }}
    textarea {{ width: 100%; height: 220px; }}
    pre {{ white-space: pre-wrap; background: #f6f8fa; padding: 12px; border-radius: 8px; }}
    select, input {{ margin: 4px; }}
  </style>
</head>
<body>
{body}
</body>
</html>""".encode("utf-8")


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        dataset = qs.get("dataset", ["musr"])[0]
        split = qs.get("split", ["murder_mystery"])[0]
        method = qs.get("method", ["direct"])[0]
        provider = qs.get("provider", ["mock"])[0]
        model = qs.get("model", ["mock"])[0]
        index = int(qs.get("index", ["0"])[0] or 0)
        samples = load_dataset(dataset, split, limit=max(index + 1, 1))
        sample = samples[min(index, len(samples) - 1)]
        result_html = ""
        if qs.get("run", ["0"])[0] == "1":
            client = make_model_client(ModelConfig(provider=provider, model=model))
            pred = run_method(sample, method, client, model)
            result_html = f"""
            <h2>Result</h2>
            <p><b>Prediction:</b> {html.escape(str(pred.prediction))}</p>
            <p><b>Gold:</b> {html.escape(str(pred.gold))}</p>
            <p><b>Correct:</b> {pred.correct}</p>
            <h3>Raw Output</h3><pre>{html.escape(pred.raw_output)}</pre>
            <h3>Prompt</h3><pre>{html.escape(pred.prompt)}</pre>
            """
        dataset_options = "\n".join(
            f"<option value='{s['name']}|{s['split']}'>{html.escape(s['description'])}</option>"
            for s in list_dataset_specs()
        )
        body = f"""
        <h1>Detective Reasoning Demo</h1>
        <form>
          <label>Dataset / split:
            <select name="dataset_split" onchange="const [d,s]=this.value.split('|'); dataset.value=d; split.value=s;">
              {dataset_options}
            </select>
          </label>
          <input type="hidden" name="dataset" id="dataset" value="{html.escape(dataset)}">
          <input type="hidden" name="split" id="split" value="{html.escape(split)}">
          <label>Index <input name="index" value="{index}" size="4"></label>
          <label>Method
            <select name="method">
              {''.join(f'<option {("selected" if m == method else "")}>{m}</option>' for m in ["direct","cot","reflection","evidence_card","critic_checklist"])}
            </select>
          </label>
          <label>Provider <input name="provider" value="{html.escape(provider)}" size="8"></label>
          <label>Model <input name="model" value="{html.escape(model)}" size="18"></label>
          <button name="run" value="0">Load sample</button>
          <button name="run" value="1">Run</button>
        </form>
        <h2>Sample</h2>
        <p><b>ID:</b> {html.escape(sample.id)}</p>
        <p><b>Question:</b> {html.escape(sample.question)}</p>
        <h3>Options</h3><pre>{html.escape(json.dumps(sample.options, ensure_ascii=False, indent=2))}</pre>
        <h3>Context</h3><pre>{html.escape((sample.context or '')[:5000])}</pre>
        <h3>Gold / Evidence</h3><pre>{html.escape(json.dumps({'answer': sample.answer, 'evidence': sample.evidence, 'reasoning': sample.reasoning}, ensure_ascii=False, indent=2)[:5000])}</pre>
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

