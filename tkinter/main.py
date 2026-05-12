import tkinter as tk
import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from utils import get_file_labels, get_filename, get_similarity_metric_options, get_feature_type_options
from confgen import confgen
from tkinter import filedialog, messagebox

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = "#F0F2F5"
CARD     = "#FFFFFF"
PRIMARY  = "#4361EE"
PRIMARY_H= "#3A52D4"
TEXT     = "#1D2939"
SUBTEXT  = "#667085"
BORDER   = "#D0D5DD"
SEL_BG   = "#C7D2FE"
SEL_FG   = "#1E3A8A"
SUCCESS  = "#059669"

MAC = sys.platform == "darwin"
F_TITLE = ("SF Pro Display", 18, "bold") if MAC else ("Segoe UI", 18, "bold")
F_H2    = ("SF Pro Text",   11, "bold") if MAC else ("Segoe UI", 11, "bold")
F_BODY  = ("SF Pro Text",   11)         if MAC else ("Segoe UI", 11)
F_SMALL = ("SF Pro Text",   10)         if MAC else ("Segoe UI", 10)
F_MONO  = ("Menlo",         10)         if MAC else ("Consolas", 10)
F_BTN   = ("SF Pro Text",   12, "bold") if MAC else ("Segoe UI", 12, "bold")

file_path = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
def make_card(parent, title):
    """White bordered section card with a section title."""
    outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    inner = tk.Frame(outer, bg=CARD, padx=20, pady=16)
    inner.pack(fill="both", expand=True)
    lbl_row = tk.Frame(inner, bg=CARD)
    lbl_row.pack(fill="x", pady=(0, 12))
    tk.Label(lbl_row, text=title, font=F_H2, fg=SUBTEXT, bg=CARD).pack(side="left")
    sep = tk.Frame(lbl_row, bg=BORDER, height=1)
    sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=5)
    return outer, inner

def make_listbox(parent, **kw):
    """Listbox with an attached scrollbar."""
    frame = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    lb = tk.Listbox(
        frame,
        yscrollcommand=sb.set,
        font=F_BODY, bg="#F8FAFC", fg=TEXT,
        selectbackground=SEL_BG, selectforeground=SEL_FG,
        relief="flat", bd=0,
        highlightthickness=0,
        activestyle="none",
        **kw,
    )
    sb.config(command=lb.yview)
    lb.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame, lb

def make_button(parent, text, command):
    """Frame+Label button that shows correct bg color on macOS."""
    outer = tk.Frame(parent, bg=PRIMARY, cursor="hand2")
    inner = tk.Label(
        outer, text=text, font=F_BTN, fg="white", bg=PRIMARY,
        padx=24, pady=10, cursor="hand2",
    )
    inner.pack()

    def on_enter(e):
        outer.config(bg=PRIMARY_H)
        inner.config(bg=PRIMARY_H)
    def on_leave(e):
        outer.config(bg=PRIMARY)
        inner.config(bg=PRIMARY)
    def on_click(e):
        command()

    for widget in (outer, inner):
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)

    return outer

# ── Business logic ────────────────────────────────────────────────────────────
def upload_file():
    global file_path
    fp = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("CSV Files", "*.csv")],
    )
    if not fp:
        return
    file_path = fp
    cols = get_file_labels(file_path)

    listbox.delete(0, tk.END)
    listbox2.delete(0, tk.END)
    for col in cols:
        listbox.insert(tk.END, col)
        listbox2.insert(tk.END, col)

    listbox3.delete(0, tk.END)
    for m in get_similarity_metric_options():
        listbox3.insert(tk.END, m)

    listbox5.delete(0, tk.END)
    for f in get_feature_type_options():
        listbox5.insert(tk.END, f)

    label_file.config(text=get_filename(file_path), fg=TEXT)
    file_status.config(text="File loaded successfully", fg=SUCCESS)

def get_selected_PK():
    primary_keys = [listbox.get(i) for i in listbox.curselection()]
    feature_col  = listbox2.get(listbox2.curselection()[0]) if listbox2.curselection() else ""
    similarity   = listbox3.get(listbox3.curselection()[0]) if listbox3.curselection() else ""
    feature_type = listbox5.get(listbox5.curselection()[0]) if listbox5.curselection() else ""
    threshold    = entry6.get().strip() or "NULL"

    if not primary_keys or not feature_col or not similarity or not feature_type:
        messagebox.showwarning(
            "Incomplete Selection",
            "Please make sure you have selected:\n"
            "  \u2022 One or more Primary Keys\n"
            "  \u2022 A Feature Column\n"
            "  \u2022 A Similarity Metric\n"
            "  \u2022 A Feature Type",
        )
        return

    def adv(e): v = e.get().strip(); return v if v else "NULL"

    layer_name  = feature_col.lower().replace(" ", "_")
    output_path = confgen(
        file_path, layer_name, primary_keys, feature_col, feature_type, similarity, threshold,
        range_val=adv(entry_range),
        multi_range=adv(entry_multi_range),
        num_segments=adv(entry_segments),
        longitude_col=adv(entry_lon),
        latitude_col=adv(entry_lat),
        date_metric=adv(entry_date_metric),
        date_format=adv(entry_date_fmt),
        time_format=adv(entry_time_fmt),
    )

    with open(output_path) as f:
        content = f.read()
    preview_text.config(state=tk.NORMAL)
    preview_text.delete(1.0, tk.END)
    preview_text.insert(tk.END, content)
    preview_text.config(state=tk.DISABLED)

    cal_gen_script = os.path.join(
        os.path.dirname(__file__), '..', 'main', 'cal_gen_mod_change_directory.py'
    )
    result = subprocess.run([sys.executable, cal_gen_script, output_path], capture_output=True, text=True)

    if result.returncode == 0:
        messagebox.showinfo("Success", f"Network layer created.\nConfig saved to:\n{output_path}")
    else:
        messagebox.showerror("Error", f"Layer generation failed:\n{result.stderr}")

# ── Root window ───────────────────────────────────────────────────────────────
# Must be set before Tk() so Windows groups the taskbar entry under our app ID
if sys.platform == "win32":
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MLNCreator.MLNLayerCreator")

root = tk.Tk()
root.title("MLN Layer Creator")
root.configure(bg=BG)
root.geometry("1040x820")
root.minsize(860, 680)

_ico_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "MLNC_LOGO-export.ico")
if sys.platform == "win32":
    import ctypes
    _ico_path_abs = os.path.abspath(_ico_path)
    # Title bar icon via tkinter (reliable for ICON_SMALL)
    root.iconbitmap(_ico_path_abs)
    # Taskbar icon via WM_SETICON using the real HWND from tkinter
    root.update_idletasks()
    _hwnd = ctypes.windll.user32.GetAncestor(root.winfo_id(), 2)  # GA_ROOT = 2
    _LR_LOADFROMFILE = 0x00000010
    _IMAGE_ICON = 1
    _big = ctypes.windll.user32.LoadImageW(None, _ico_path_abs, _IMAGE_ICON, 0, 0, _LR_LOADFROMFILE)
    ctypes.windll.user32.SendMessageW(_hwnd, 0x0080, 1, _big)  # WM_SETICON, ICON_BIG
else:
    _icon_img = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), "assets", "icons", "MLNC_LOGO-export.png"))
    root.iconphoto(True, _icon_img)

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=PRIMARY, height=64)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(header, text="MLN Layer Creator", font=F_TITLE, fg="white", bg=PRIMARY).pack(side="left", padx=24, pady=16)
tk.Label(header, text="Multi-Layer Network Creation Tool",
         font=F_SMALL, fg="#A5B4FC", bg=PRIMARY).pack(side="left", pady=22)

# ── Tab bar ───────────────────────────────────────────────────────────────────
TAB_BG      = "#E8EAED"
TAB_ACTIVE  = CARD
TAB_FG      = SUBTEXT
TAB_FG_ACT  = PRIMARY

tabbar = tk.Frame(root, bg=TAB_BG, height=40)
tabbar.pack(fill="x")
tabbar.pack_propagate(False)

tab_content = tk.Frame(root, bg=BG)
tab_content.pack(fill="both", expand=True)

tab1_frame = tk.Frame(tab_content, bg=BG)
tab2_frame = tk.Frame(tab_content, bg=BG)
tab1_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
tab2_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

_active_indicator = {}  # holds indicator bar frames

def show_tab(n):
    if n == 1:
        tab1_frame.lift()
    else:
        tab2_frame.lift()
    for idx, (btn, lbl, bar) in _active_indicator.items():
        active = (idx == n)
        btn.config(bg=TAB_ACTIVE if active else TAB_BG)
        lbl.config(bg=TAB_ACTIVE if active else TAB_BG,
                   fg=TAB_FG_ACT if active else TAB_FG,
                   font=(F_H2[0], F_H2[1], "bold") if active else F_H2)
        bar.config(bg=PRIMARY if active else TAB_BG)

def _make_tab(text, n):
    btn = tk.Frame(tabbar, bg=TAB_BG, cursor="hand2")
    btn.pack(side="left")
    lbl = tk.Label(btn, text=text, font=F_H2, fg=TAB_FG, bg=TAB_BG,
                   padx=20, pady=10, cursor="hand2")
    lbl.pack()
    bar = tk.Frame(btn, bg=TAB_BG, height=3)
    bar.pack(fill="x")
    cmd = lambda _n=n: show_tab(_n)
    btn.bind("<Button-1>", lambda e, _n=n: show_tab(_n))
    lbl.bind("<Button-1>", lambda e, _n=n: show_tab(_n))
    _active_indicator[n] = (btn, lbl, bar)

_make_tab("Intra-layer Network Creator", 1)
_make_tab("Inter-layer Network Creator with Set Operations", 2)
show_tab(1)

# ── Scrollable canvas (Tab 1) ─────────────────────────────────────────────────
canvas  = tk.Canvas(tab1_frame, bg=BG, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

body = tk.Frame(canvas, bg=BG)
body_id = canvas.create_window((0, 0), window=body, anchor="nw")

def _resize(e):  canvas.itemconfig(body_id, width=e.width)
def _scroll(e):  canvas.configure(scrollregion=canvas.bbox("all"))
canvas.bind("<Configure>", _resize)
body.bind("<Configure>", _scroll)

def _mousewheel(e):
    widget = e.widget
    # Let Listbox and Text widgets handle their own scrolling
    if isinstance(widget, (tk.Listbox, tk.Text)):
        return
    delta = -1 * e.delta if MAC else int(-1 * e.delta / 120)
    canvas.yview_scroll(delta, "units")
canvas.bind_all("<MouseWheel>", _mousewheel)

PAD = dict(padx=24, pady=8)

# ── Step 1 — Data Source ──────────────────────────────────────────────────────
card1_outer, card1 = make_card(body, "STEP 1 — DATA SOURCE")
card1_outer.pack(fill="x", **PAD)

row1 = tk.Frame(card1, bg=CARD)
row1.pack(fill="x")

btn_upload = make_button(row1, "Browse CSV\u2026", upload_file)
btn_upload.pack(side="left")

file_info = tk.Frame(row1, bg=CARD)
file_info.pack(side="left", padx=16)

label_file   = tk.Label(file_info, text="No file selected", font=F_BODY, fg=SUBTEXT, bg=CARD, anchor="w")
label_file.pack(anchor="w")
file_status  = tk.Label(file_info, text="", font=F_SMALL, fg=SUBTEXT, bg=CARD, anchor="w")
file_status.pack(anchor="w")

# ── Step 2 — Layer Configuration ─────────────────────────────────────────────
card2_outer, card2 = make_card(body, "STEP 2 — FEATURE EXTRACTION")
card2_outer.pack(fill="x", **PAD)

# 4-column grid for the listboxes
grid = tk.Frame(card2, bg=CARD)
grid.pack(fill="x")
for col_idx, weight in enumerate([1, 1, 1, 1]):
    grid.columnconfigure(col_idx, weight=weight, minsize=180)

def col_header(text, col, hint=""):
    tk.Label(grid, text=text, font=F_H2, fg=TEXT, bg=CARD, anchor="w").grid(
        row=0, column=col, sticky="w", padx=(0, 12), pady=(0, 2))
    tk.Label(grid, text=hint, font=F_SMALL, fg=SUBTEXT, bg=CARD, anchor="w").grid(
        row=1, column=col, sticky="w", padx=(0, 12), pady=(0, 6))

col_header("Primary Key",     0, "Node identifiers (multi-select)")
col_header("Feature Column",  1, "Edge attribute column")
col_header("Similarity Metric", 2, "Edge generation method")
col_header("Feature Type",    3, "Data type of the feature")

pk_frame, listbox  = make_listbox(grid, selectmode=tk.MULTIPLE, exportselection=False, height=7, width=20)
fc_frame, listbox2 = make_listbox(grid, selectmode=tk.SINGLE,   exportselection=False, height=7, width=20)
sm_frame, listbox3 = make_listbox(grid, selectmode=tk.SINGLE,   exportselection=False, height=7, width=18)
ft_frame, listbox5 = make_listbox(grid, selectmode=tk.SINGLE,   exportselection=False, height=7, width=18)

pk_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 12), pady=(0, 16))
fc_frame.grid(row=2, column=1, sticky="nsew", padx=(0, 12), pady=(0, 16))
sm_frame.grid(row=2, column=2, sticky="nsew", padx=(0, 12), pady=(0, 16))
ft_frame.grid(row=2, column=3, sticky="nsew",               pady=(0, 16))

# ── Step 3 — Contextual Options (dynamic) ────────────────────────────────────
card3_outer, card3 = make_card(body, "STEP 3 — ADDITIONAL OPTIONS")
card3_outer.pack(fill="x", **PAD)

adv_prompt = tk.Label(
    card3, text="Select a Feature Type above to see relevant options.",
    font=F_SMALL, fg=SUBTEXT, bg=CARD, pady=6,
)
adv_prompt.pack(anchor="w")

adv_container = tk.Frame(card3, bg=CARD)
# packed / forgotten dynamically

def _make_adv_field(label, hint, placeholder="NULL"):
    frame = tk.Frame(adv_container, bg=CARD, padx=0, pady=0)
    tk.Label(frame, text=label, font=F_H2, fg=TEXT, bg=CARD, anchor="w").pack(anchor="w")
    tk.Label(frame, text=hint,  font=F_SMALL, fg=SUBTEXT, bg=CARD, anchor="w").pack(anchor="w")
    e = tk.Entry(
        frame, font=F_BODY, fg=TEXT, bg="#F8FAFC",
        relief="flat", bd=0,
        highlightthickness=1, highlightbackground=BORDER, highlightcolor=PRIMARY,
        width=36,
    )
    e.insert(0, placeholder)
    e.pack(anchor="w", ipady=5, pady=(4, 0))
    return frame, e

_adv = {
    "THRESHOLD":    _make_adv_field("THRESHOLD",
                        "Numeric value for edge connection; IDs are connected if their similarity is less than this value."),
    "RANGE":        _make_adv_field("RANGE",
                        "Interval(s) that connect IDs whose feature value falls inside, e.g. [1,4] or (5,7]."),
    "MULTI_RANGE":  _make_adv_field("MULTI_RANGE",
                        "Multiple ranges separated by -, e.g. [1,2]-[3,4]-[5,6]."),
    "SEGMENTS":     _make_adv_field("NUMBER_OF_EQUI_SIZED_SEGMENTS",
                        "Number of equal-size segments the range is divided into, e.g. 5."),
    "LON":          _make_adv_field("LONGITUDE_FEATURE_COLUMN",
                        "Name of the CSV column containing longitude values."),
    "LAT":          _make_adv_field("LATITUDE_FEATURE_COLUMN",
                        "Name of the CSV column containing latitude values."),
    "DATE_METRIC":  _make_adv_field("DATE_METRIC",
                        "Granularity for date comparison: DAY, MONTH, or YEAR."),
    "DATE_FORMAT":  _make_adv_field("DATE_FORMAT",
                        "Format of the date values, e.g. dd-mm-yyyy or mm-dd-yyyy."),
    "TIME_FORMAT":  _make_adv_field("TIME_FORMAT",
                        "Format of the time values, e.g. hh:mm."),
}

# Named entry references used by get_selected_PK
entry6            = _adv["THRESHOLD"][1]
entry_range       = _adv["RANGE"][1]
entry_multi_range = _adv["MULTI_RANGE"][1]
entry_segments    = _adv["SEGMENTS"][1]
entry_lon         = _adv["LON"][1]
entry_lat         = _adv["LAT"][1]
entry_date_metric = _adv["DATE_METRIC"][1]
entry_date_fmt    = _adv["DATE_FORMAT"][1]
entry_time_fmt    = _adv["TIME_FORMAT"][1]

# feature type → ordered list of field keys to show
_FT_FIELDS = {
    "NOMINAL":    ["THRESHOLD"],
    "NUMERIC":    ["THRESHOLD", "RANGE", "MULTI_RANGE", "SEGMENTS"],
    "GEOGRAPHIC": ["THRESHOLD", "LON", "LAT"],
    "TIME":       ["THRESHOLD", "TIME_FORMAT"],
    "DATE":       ["THRESHOLD", "DATE_FORMAT", "DATE_METRIC"],
    "SET":        ["THRESHOLD"],
    "TEXT":       ["THRESHOLD"],
}

_NO_OPTS_TYPES = {"No additional options required for this feature type."}

def on_feature_type_select(event=None):
    sel = listbox5.curselection()
    if not sel:
        return
    ft = listbox5.get(sel[0])
    keys = _FT_FIELDS.get(ft, ["THRESHOLD"])

    # hide all field frames first
    for frame, _ in _adv.values():
        frame.pack_forget()

    adv_prompt.pack_forget()
    adv_container.pack(fill="x")
    for key in keys:
        _adv[key][0].pack(anchor="w", fill="x", pady=(0, 14))

listbox5.bind("<<ListboxSelect>>", on_feature_type_select)

# ── Step 4 — Config Preview ───────────────────────────────────────────────────
card3_outer, card3 = make_card(body, "STEP 4 — GENERATED CONFIG PREVIEW")
card3_outer.pack(fill="x", **PAD)

preview_text = tk.Text(
    card3,
    font=F_MONO, bg="#1E1E2E", fg="#CDD6F4",
    insertbackground="white", relief="flat", bd=0,
    padx=14, pady=10, height=20, state=tk.DISABLED,
    highlightthickness=0,
)
preview_text.pack(fill="both", expand=True)

# ── Action button ─────────────────────────────────────────────────────────────
btn_frame = tk.Frame(body, bg=BG)
btn_frame.pack(pady=(8, 28))
btn_create = make_button(btn_frame, "Create Network Layer  \u2192", get_selected_PK)
btn_create.pack()

def _bind_scroll_to_all(widget):
    if not isinstance(widget, (tk.Listbox, tk.Text)):
        widget.bind("<MouseWheel>", _mousewheel)
    for child in widget.winfo_children():
        _bind_scroll_to_all(child)

_bind_scroll_to_all(body)

root.mainloop()
