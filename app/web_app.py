"""Flask web interface for BTRFS administration operations."""

from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from app.operations import OPERATIONS, get_operation, run_operation


app = Flask(__name__)


@app.get("/")
def index() -> str:
    return render_template("index.html", operations=OPERATIONS, selected=OPERATIONS[0], result=None, values={})


@app.post("/run")
def run() -> str:
    key = request.form.get("operation", "")
    operation = get_operation(key)
    values: dict[str, str] = {field.key: request.form.get(field.key, "") for field in operation.fields}
    dry_run = request.form.get("dry_run", "on") == "on"

    try:
        result = run_operation(operation, values, dry_run=dry_run)
    except ValueError as exc:
        return render_template(
            "index.html",
            operations=OPERATIONS,
            selected=operation,
            result={"command": "", "returncode": 2, "stdout": "", "stderr": str(exc), "blocked": False},
            values=values,
        )

    return render_template(
        "index.html",
        operations=OPERATIONS,
        selected=operation,
        result=result,
        values=values,
    )


@app.get("/healthz")
def healthz() -> str:
    return "ok"


def main() -> None:
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
