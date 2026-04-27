"""Desktop interface for BTRFS GUI (Tkinter)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser

from app.catalog import load_catalog, tools_by_category, Tool


class DesktopBtrfsGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BTRFS Mission Control")
        self.geometry("1150x760")

        self.catalog = load_catalog()
        self.grouped_tools = tools_by_category(self.catalog)

        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        hero = ttk.Label(
            root,
            text=self.catalog.tagline,
            font=("Segoe UI", 16, "bold"),
        )
        hero.pack(anchor=tk.W, pady=(0, 10))

        splitter = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        splitter.pack(fill=tk.BOTH, expand=True)

        nav_frame = ttk.Frame(splitter, padding=8)
        details_frame = ttk.Frame(splitter, padding=8)
        splitter.add(nav_frame, weight=1)
        splitter.add(details_frame, weight=3)

        ttk.Label(nav_frame, text="Sections", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        self.section_list = tk.Listbox(nav_frame, exportselection=False, height=20)
        for item in self.catalog.navigation:
            self.section_list.insert(tk.END, item["section"])
        self.section_list.bind("<<ListboxSelect>>", self._on_section_selected)
        self.section_list.pack(fill=tk.BOTH, expand=True, pady=(8, 8))

        self.section_text = ScrolledText(nav_frame, wrap=tk.WORD, height=8)
        self.section_text.pack(fill=tk.BOTH, expand=False)

        notebook = ttk.Notebook(details_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        tools_tab = ttk.Frame(notebook)
        btrfs_tab = ttk.Frame(notebook)
        notebook.add(tools_tab, text="Tool Catalog")
        notebook.add(btrfs_tab, text="btrfs-progs Coverage")

        self._build_tool_tab(tools_tab)
        self._build_btrfs_tab(btrfs_tab)

        self.section_list.selection_set(0)
        self._on_section_selected()

    def _build_tool_tab(self, parent: ttk.Frame) -> None:
        split = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        split.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(split, padding=8)
        right = ttk.Frame(split, padding=8)
        split.add(left, weight=1)
        split.add(right, weight=2)

        ttk.Label(left, text="Categories", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.category_list = tk.Listbox(left, exportselection=False)
        for category in self.grouped_tools:
            self.category_list.insert(tk.END, category)
        self.category_list.bind("<<ListboxSelect>>", self._on_category_selected)
        self.category_list.pack(fill=tk.BOTH, expand=True, pady=(6, 8))

        ttk.Label(left, text="Tools", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        self.tool_list = tk.Listbox(left, exportselection=False)
        self.tool_list.bind("<<ListboxSelect>>", self._on_tool_selected)
        self.tool_list.pack(fill=tk.BOTH, expand=True)

        self.tool_detail = ScrolledText(right, wrap=tk.WORD)
        self.tool_detail.pack(fill=tk.BOTH, expand=True)

        self.open_repo_btn = ttk.Button(right, text="Open Repository", command=self._open_repo)
        self.open_repo_btn.pack(anchor=tk.E, pady=(8, 0))

        self.selected_tool: Tool | None = None

        self.category_list.selection_set(0)
        self._on_category_selected()

    def _build_btrfs_tab(self, parent: ttk.Frame) -> None:
        text = ScrolledText(parent, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        lines: list[str] = [
            "btrfs-progs functional coverage represented in this GUI:\n",
        ]
        for area in self.catalog.functional_areas:
            lines.append(f"• {area.name}")
            for command in area.commands:
                lines.append(f"   - {command}")
            lines.append("")
        lines.append("Design note: each command family maps to dedicated UI workflows and context help.")
        text.insert(tk.END, "\n".join(lines))
        text.configure(state=tk.DISABLED)

    def _on_section_selected(self, _event: object | None = None) -> None:
        selection = self.section_list.curselection()
        if not selection:
            return
        idx = selection[0]
        section = self.catalog.navigation[idx]
        self.section_text.delete("1.0", tk.END)
        self.section_text.insert(tk.END, f"{section['section']}\n\n{section['description']}")

    def _on_category_selected(self, _event: object | None = None) -> None:
        selection = self.category_list.curselection()
        if not selection:
            return
        category = self.category_list.get(selection[0])
        self.tool_list.delete(0, tk.END)
        for tool in self.grouped_tools[category]:
            self.tool_list.insert(tk.END, tool.name)
        if self.tool_list.size() > 0:
            self.tool_list.selection_set(0)
            self._on_tool_selected()

    def _on_tool_selected(self, _event: object | None = None) -> None:
        category_sel = self.category_list.curselection()
        tool_sel = self.tool_list.curselection()
        if not category_sel or not tool_sel:
            return
        category = self.category_list.get(category_sel[0])
        tool = self.grouped_tools[category][tool_sel[0]]
        self.selected_tool = tool

        lines = [
            f"Name: {tool.name}",
            f"Category: {tool.category}",
            f"Kind: {tool.kind}",
            f"Repository: {tool.repo}",
            f"Docs: {tool.docs}",
            "",
            "Suggested interaction patterns:",
        ]
        lines.extend([f"  - {hint}" for hint in tool.interface_hints])

        self.tool_detail.delete("1.0", tk.END)
        self.tool_detail.insert(tk.END, "\n".join(lines))

    def _open_repo(self) -> None:
        if self.selected_tool is not None:
            webbrowser.open(self.selected_tool.repo)


def main() -> None:
    app = DesktopBtrfsGui()
    app.mainloop()


if __name__ == "__main__":
    main()
