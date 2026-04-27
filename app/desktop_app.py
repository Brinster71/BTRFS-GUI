"""Desktop BTRFS administration interface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from app.operations import OPERATIONS, Operation, run_operation


class DesktopBtrfsAdmin(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BTRFS Admin Console")
        self.geometry("1120x760")

        self.operation = OPERATIONS[0]
        self.entries: dict[str, ttk.Entry] = {}
        self.allow_execute = tk.BooleanVar(value=False)

        self._build()

    def _build(self) -> None:
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            outer,
            text="BTRFS Administrative Tools",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor=tk.W, pady=(0, 8))

        paned = ttk.PanedWindow(outer, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=1)
        paned.add(right, weight=2)

        ttk.Label(left, text="Operations", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        self.op_list = tk.Listbox(left, exportselection=False)
        for op in OPERATIONS:
            suffix = " [destructive]" if op.destructive else ""
            self.op_list.insert(tk.END, f"{op.title}{suffix}")
        self.op_list.bind("<<ListboxSelect>>", self._choose_operation)
        self.op_list.pack(fill=tk.BOTH, expand=True)

        self.form_frame = ttk.Frame(right)
        self.form_frame.pack(fill=tk.X)

        self.desc = ttk.Label(right, text="", wraplength=650)
        self.desc.pack(anchor=tk.W, pady=(0, 8))

        ttk.Checkbutton(
            right,
            text="Execute command (unchecked = dry run)",
            variable=self.allow_execute,
        ).pack(anchor=tk.W, pady=(0, 8))

        ttk.Button(right, text="Run", command=self._run).pack(anchor=tk.W, pady=(0, 8))

        self.output = ScrolledText(right, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

        self.op_list.selection_set(0)
        self._refresh_form()

    def _choose_operation(self, _event: object | None = None) -> None:
        sel = self.op_list.curselection()
        if not sel:
            return
        self.operation = OPERATIONS[sel[0]]
        self._refresh_form()

    def _refresh_form(self) -> None:
        for child in self.form_frame.winfo_children():
            child.destroy()
        self.entries = {}

        self.desc.configure(
            text=f"{self.operation.command_family}: {self.operation.description}"
        )

        for idx, field in enumerate(self.operation.fields):
            ttk.Label(self.form_frame, text=field.label).grid(row=idx, column=0, sticky=tk.W, pady=4)
            entry = ttk.Entry(self.form_frame, width=72)
            entry.grid(row=idx, column=1, sticky=tk.EW, pady=4)
            if field.placeholder:
                entry.insert(0, field.placeholder)
            self.entries[field.key] = entry

    def _run(self) -> None:
        params = {key: entry.get() for key, entry in self.entries.items()}
        try:
            result = run_operation(self.operation, params, dry_run=not self.allow_execute.get())
        except ValueError as exc:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, f"Validation error: {exc}")
            return

        lines = [
            f"Operation: {self.operation.title}",
            f"Command: {result.command}",
            f"Return code: {result.returncode}",
            "",
            "STDOUT:",
            result.stdout,
            "",
            "STDERR:",
            result.stderr,
        ]
        if result.blocked:
            lines.insert(3, f"Blocked: {result.block_reason}")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "\n".join(lines))


def main() -> None:
    app = DesktopBtrfsAdmin()
    app.mainloop()


if __name__ == "__main__":
    main()
