#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简易出图 HTTP 服务，供扣子/飞书「发送 HTTP 请求」节点调用。

启动:
  pip install flask pillow
  python3 briefing/server.py

接口:
  POST /render
  Body: 日销售简报 JSON（与 data.example.json 同结构）
        或 { "report_type": "daily_sales_briefing", "data": { ... } }
  返回: image/png
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file

from render_pillow import render

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"ok": True, "templates": ["daily_sales_briefing"]})


@app.post("/render")
def render_api():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "JSON body required"}), 400

    report_type = payload.get("report_type", "daily_sales_briefing")
    data = payload.get("data", payload)

    if report_type != "daily_sales_briefing":
        return jsonify({
            "error": f"unsupported report_type: {report_type}",
            "supported": ["daily_sales_briefing"],
        }), 400

    required = ["meta", "headline", "kpis", "section_01", "section_02", "section_03", "section_04"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": "missing fields", "missing": missing}), 400

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "briefing.png"
        render(data, out)
        return send_file(out, mimetype="image/png", download_name="briefing.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8787)
