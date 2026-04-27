"""Flask web interface for BTRFS GUI."""

from __future__ import annotations

from flask import Flask, render_template

from app.catalog import load_catalog, tools_by_category


app = Flask(__name__)


@app.get("/")
def index() -> str:
    catalog = load_catalog()
    grouped = tools_by_category(catalog)
    return render_template(
        "index.html",
        catalog=catalog,
        grouped=grouped,
    )


def main() -> None:
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
