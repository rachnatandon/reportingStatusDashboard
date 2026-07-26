import streamlit as st
import csv
import zipfile
import re
import html
from io import BytesIO
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta

st.set_page_config(page_title="Labs Tracker", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --ink: #16232E;
        --muted: #5B6B7A;
        --line: #DCE3EA;
        --surface: #FFFFFF;
        --canvas: #F4F7FA;
        --primary: #0B5FA5;
        --primary-dark: #084677;
        --teal: #0E8F8F;
        --good: #1B8A5A;
        --warn: #B4770E;
        --danger: #B23A48;
        --good-bg: rgba(27, 138, 90, 0.12);
        --danger-bg: rgba(178, 58, 72, 0.12);
        --shadow: rgba(22, 35, 46, 0.05);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --ink: #E7ECF1;
            --muted: #93A1AF;
            --line: #2A3441;
            --surface: #161C24;
            --canvas: #0E1319;
            --primary: #5AA9E6;
            --primary-dark: #7DBDEF;
            --teal: #4FCFCF;
            --good: #46CC8D;
            --warn: #E3AC4D;
            --danger: #E58A93;
            --good-bg: rgba(70, 204, 141, 0.16);
            --danger-bg: rgba(229, 138, 147, 0.16);
            --shadow: rgba(0, 0, 0, 0.25);
        }
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
    .stApp { background: var(--canvas); }

    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.01em; color: var(--ink); }
    h1 { font-weight: 800 !important; }
    h2 { font-weight: 700 !important; }

    .lt-eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        color: var(--teal);
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .lt-hero-title { font-size: 2.1rem; margin: 0 0 0.15rem 0; }
    .lt-hero-sub { color: var(--muted); font-size: 0.98rem; margin-bottom: 0.4rem; }
    .lt-hairline { border: none; border-top: 1px solid var(--line); margin: 1.6rem 0; }

    .lt-step-tag {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        background: var(--primary);
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 0.5rem;
    }

    .lt-stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }
    .lt-stat {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        box-shadow: 0 1px 2px var(--shadow);
    }
    .lt-stat-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.25rem;
    }
    .lt-stat-value {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 1.7rem;
        color: var(--ink);
    }
    .lt-stat-good { color: var(--good); }
    .lt-stat-warn { color: var(--warn); }
    .lt-stat-danger { color: var(--danger); }

    div[data-testid="stFileUploaderDropzone"] {
        background: var(--surface);
        border: 1.5px dashed var(--line);
        border-radius: 10px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border-radius: 12px;
        border: 1px solid var(--line) !important;
        padding: 1.1rem 1.4rem;
    }

    .lt-cal-wrap {
        overflow-x: auto;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--surface);
    }
    .lt-cal-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.85rem;
    }
    .lt-cal-table th, .lt-cal-table td {
        border: 1px solid var(--line);
        padding: 8px 14px;
        text-align: center;
        white-space: nowrap;
    }
    .lt-cal-table th {
        background: var(--canvas);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--muted);
        font-weight: 500;
    }
    .lt-cal-table td.lt-cal-label {
        text-align: left;
        font-weight: 600;
        color: var(--ink);
    }
    .lt-cal-table td.lt-cal-id {
        text-align: left;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: var(--muted);
    }
    .lt-cal-good {
        background: var(--good-bg);
        color: var(--good);
        font-weight: 700;
    }
    .lt-cal-bad {
        background: var(--danger-bg);
        color: var(--danger);
        font-weight: 700;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 7px;
        font-weight: 600;
        border: 1px solid var(--primary);
    }
    .stDownloadButton > button {
        background: var(--primary);
        color: #fff;
    }
    .stDownloadButton > button:hover {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
        color: #fff;
    }

    .lt-legend {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 0.35rem 0 0.75rem 0;
    }
    .lt-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: var(--muted);
    }
    .lt-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .lt-dot-good { background: var(--good); }
    .lt-dot-danger { background: var(--danger); }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .lt-footer {
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.78rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="lt-eyebrow">LAB COMPLIANCE DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<h1 class="lt-hero-title">Labs Tracker</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="lt-hero-sub">Cross-reference lab reporting activity against your master registry, '
    'by HFR ID.</div>',
    unsafe_allow_html=True,
)

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"main": MAIN_NS}

MASTER_HEADER_ROW = 6
CSV_HEADER_ROW_INDEX = 9  # 0-based -> row 10

DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%m/%d/%y",
    "%d/%m/%y",
]

# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def parse_date(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def find_column_index(header, target_name):
    for i, col_name in enumerate(header):
        if (col_name or "").strip().lower() == target_name.strip().lower():
            return i
    return None


def or_default(value, default):
    value = (value or "").strip()
    return value if value else default


# ---------------------------------------------------------------------------
# Minimal XLSX reader/writer (stdlib only: zipfile + xml.etree.ElementTree)
# ---------------------------------------------------------------------------


def col_to_index(col_letters):
    idx = 0
    for ch in col_letters:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1  # zero-based


def index_to_col(idx):
    idx += 1
    letters = ""
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def split_cell_ref(ref):
    m = re.match(r"([A-Za-z]+)(\d+)", ref)
    return m.group(1), int(m.group(2))


def get_shared_strings(z):
    try:
        data = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(data)
    strings = []
    for si in root.findall("main:si", NS):
        texts = si.findall(".//main:t", NS)
        strings.append("".join(t.text or "" for t in texts))
    return strings


def get_first_sheet_path(z):
    workbook_xml = z.read("xl/workbook.xml")
    wb_root = ET.fromstring(workbook_xml)
    sheets = wb_root.find("main:sheets", NS)
    first_sheet = sheets.find("main:sheet", NS)
    rid = first_sheet.get(f"{{{REL_NS}}}id")
    rels_xml = z.read("xl/_rels/workbook.xml.rels")
    rels_root = ET.fromstring(rels_xml)
    for rel in rels_root:
        if rel.get("Id") == rid:
            target = rel.get("Target")
            if not target.startswith("xl/"):
                target = "xl/" + target
            return target
    raise ValueError("Could not resolve the first worksheet inside the .xlsx file.")


def parse_sheet_rows(z, sheet_path, shared_strings):
    data = z.read(sheet_path)
    root = ET.fromstring(data)
    sheet_data = root.find("main:sheetData", NS)
    rows = {}
    max_row = 0
    for row_el in sheet_data.findall("main:row", NS):
        r = int(row_el.get("r"))
        max_row = max(max_row, r)
        row_vals = {}
        for c_el in row_el.findall("main:c", NS):
            ref = c_el.get("r")
            col_letters, _ = split_cell_ref(ref)
            col_idx = col_to_index(col_letters)
            cell_type = c_el.get("t")
            value = ""
            if cell_type == "s":
                v_el = c_el.find("main:v", NS)
                if v_el is not None and v_el.text is not None:
                    value = shared_strings[int(v_el.text)]
            elif cell_type == "inlineStr":
                is_el = c_el.find("main:is", NS)
                if is_el is not None:
                    t_el = is_el.find("main:t", NS)
                    value = t_el.text if t_el is not None and t_el.text else ""
            else:
                v_el = c_el.find("main:v", NS)
                value = v_el.text if v_el is not None and v_el.text is not None else ""
            row_vals[col_idx] = value
        rows[r] = row_vals
    return rows, max_row


def append_rows_to_master(original_bytes, sheet_path, new_rows_cells, max_row):
    """new_rows_cells: list of rows, each row a list of (col_idx, text_value) tuples."""
    z_in = zipfile.ZipFile(BytesIO(original_bytes))
    sheet_xml = z_in.read(sheet_path).decode("utf-8")

    current_row = max_row
    new_rows_xml_parts = []
    for cell_defs in new_rows_cells:
        current_row += 1
        cells_xml = ""
        for col_idx, text_val in sorted(cell_defs, key=lambda x: x[0]):
            col_letter = index_to_col(col_idx)
            safe_text = (text_val or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            cells_xml += f'<c r="{col_letter}{current_row}" t="inlineStr"><is><t>{safe_text}</t></is></c>'
        new_rows_xml_parts.append(f'<row r="{current_row}">{cells_xml}</row>')

    updated_sheet_xml = sheet_xml.replace("</sheetData>", "".join(new_rows_xml_parts) + "</sheetData>")

    def update_dimension(match):
        ref = match.group(1)
        parts = ref.split(":")
        if len(parts) == 2:
            start, end = parts
            end_col, end_row = split_cell_ref(end)
            new_end_row = max(end_row, current_row)
            return f'<dimension ref="{start}:{end_col}{new_end_row}"/>'
        return match.group(0)

    updated_sheet_xml = re.sub(r'<dimension ref="([^"]+)"\s*/>', update_dimension, updated_sheet_xml)

    out_buffer = BytesIO()
    with zipfile.ZipFile(out_buffer, "w", zipfile.ZIP_DEFLATED) as z_out:
        for item in z_in.infolist():
            content = updated_sheet_xml if item.filename == sheet_path else z_in.read(item.filename)
            z_out.writestr(item, content)
    z_in.close()
    out_buffer.seek(0)
    return out_buffer.getvalue()


# ---------------------------------------------------------------------------
# UI: uploads
# ---------------------------------------------------------------------------

upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    with st.container(border=True):
        st.markdown('<span class="lt-step-tag">STEP 01</span>', unsafe_allow_html=True)
        st.markdown("**Master Labs Registry**")
        st.caption(
            "`.xlsx` · headers on row 6 · requires *Lab Name*, *HFR Code*, "
            "*Block Name*, *Category*, *Lab Type*"
        )
        master_file = st.file_uploader(
            "Upload master file", type=["xlsx"], key="master_uploader", label_visibility="collapsed"
        )

with upload_col2:
    with st.container(border=True):
        st.markdown('<span class="lt-step-tag">STEP 02</span>', unsafe_allow_html=True)
        st.markdown("**Lab Report Data**")
        st.caption(
            "`.csv` · headers on row 10 · requires *Lab Name*, *Result Date*, "
            "*HFR ID*, *Lab Block*, *Lab Type*"
        )
        uploaded_file = st.file_uploader(
            "Upload data CSV", type=["csv"], key="csv_uploader", label_visibility="collapsed"
        )

if master_file and uploaded_file:
    # -----------------------------------------------------------------
    # Parse master .xlsx
    # -----------------------------------------------------------------
    master_bytes = master_file.getvalue()
    try:
        z = zipfile.ZipFile(BytesIO(master_bytes))
        shared_strings = get_shared_strings(z)
        sheet_path = get_first_sheet_path(z)
        master_rows, master_max_row = parse_sheet_rows(z, sheet_path, shared_strings)
        z.close()
    except Exception as e:
        st.error(f"Could not read the master .xlsx file: {e}")
        st.stop()

    if MASTER_HEADER_ROW not in master_rows:
        st.error(f"Master file doesn't appear to have data on row {MASTER_HEADER_ROW} (the header row).")
        st.stop()

    master_header = master_rows[MASTER_HEADER_ROW]
    master_cols = {"lab name": None, "hfr code": None, "block name": None, "category": None, "lab type": None}
    for idx, val in master_header.items():
        v = (val or "").strip().lower()
        if v in master_cols:
            master_cols[v] = idx

    missing_master_cols = [
        name.title() if name != "hfr code" else "HFR Code"
        for name, idx in master_cols.items()
        if idx is None
    ]
    if missing_master_cols:
        st.error(
            f"Master file is missing required column(s) on row {MASTER_HEADER_ROW}: "
            f"{', '.join(missing_master_cols)}."
        )
        st.stop()

    master_lab_col = master_cols["lab name"]
    master_hfr_col = master_cols["hfr code"]
    master_block_col = master_cols["block name"]
    master_category_col = master_cols["category"]
    master_labtype_col = master_cols["lab type"]

    master_labs = {}  # hfr_code -> dict of raw fields (may be empty strings)
    for r_num, row_vals in master_rows.items():
        if r_num <= MASTER_HEADER_ROW:
            continue
        hfr_code = str(row_vals.get(master_hfr_col, "")).strip()
        if not hfr_code:
            continue
        master_labs[hfr_code] = {
            "lab_name": str(row_vals.get(master_lab_col, "")).strip(),
            "block_name": str(row_vals.get(master_block_col, "")).strip(),
            "category": str(row_vals.get(master_category_col, "")).strip(),
            "lab_type": str(row_vals.get(master_labtype_col, "")).strip(),
        }

    # -----------------------------------------------------------------
    # Parse data .csv
    # -----------------------------------------------------------------
    text = uploaded_file.getvalue().decode("utf-8-sig", errors="replace")
    lines = text.splitlines()

    if len(lines) <= CSV_HEADER_ROW_INDEX:
        st.error(
            f"The uploaded CSV only has {len(lines)} row(s), "
            f"but headers are expected on row {CSV_HEADER_ROW_INDEX + 1}."
        )
        st.stop()

    csv_rows = list(csv.reader(lines[CSV_HEADER_ROW_INDEX:]))
    csv_header = csv_rows[0]
    csv_data_rows = csv_rows[1:]

    csv_lab_col = find_column_index(csv_header, "Lab Name")
    csv_date_col = find_column_index(csv_header, "Result Date")
    csv_hfr_col = find_column_index(csv_header, "HFR ID")
    csv_block_col = find_column_index(csv_header, "Lab Block")
    csv_labtype_col = find_column_index(csv_header, "Lab Type")

    missing_csv_cols = []
    if csv_lab_col is None:
        missing_csv_cols.append("Lab Name")
    if csv_date_col is None:
        missing_csv_cols.append("Result Date")
    if csv_hfr_col is None:
        missing_csv_cols.append("HFR ID")

    if missing_csv_cols:
        st.error(
            f"CSV file is missing required column(s) on row {CSV_HEADER_ROW_INDEX + 1}: "
            f"{', '.join(missing_csv_cols)}."
        )
        st.stop()

    if csv_block_col is None or csv_labtype_col is None:
        st.info(
            "Note: 'Lab Block' and/or 'Lab Type' column not found in the CSV. "
            "Block Name / Category for labs not in the master file will show as 'No data'."
        )

    csv_groups = {}  # hfr_id -> {"lab_name", "latest_date", "unparsed", "block_name", "category"}
    for row in csv_data_rows:
        if csv_hfr_col >= len(row):
            continue
        hfr_id = row[csv_hfr_col].strip()
        if not hfr_id:
            continue
        lab_name = row[csv_lab_col].strip() if csv_lab_col < len(row) else ""
        date_str = row[csv_date_col] if csv_date_col < len(row) else ""
        block_val = row[csv_block_col].strip() if csv_block_col is not None and csv_block_col < len(row) else ""
        labtype_val = row[csv_labtype_col].strip() if csv_labtype_col is not None and csv_labtype_col < len(row) else ""
        parsed = parse_date(date_str)

        group = csv_groups.setdefault(
            hfr_id,
            {
                "lab_name": "",
                "latest_date": None,
                "unparsed": 0,
                "block_name": "",
                "category": "",
                "dates_present": set(),
            },
        )
        if lab_name:
            group["lab_name"] = lab_name
        if block_val:
            group["block_name"] = block_val
        if labtype_val:
            group["category"] = labtype_val
        if parsed is not None:
            if group["latest_date"] is None or parsed > group["latest_date"]:
                group["latest_date"] = parsed
            group["dates_present"].add(parsed.date())
        else:
            group["unparsed"] += 1

    # -----------------------------------------------------------------
    # Cross-reference master vs. csv, keyed by HFR Code / HFR ID
    # -----------------------------------------------------------------
    table_rows = []

    for hfr_code, info in master_labs.items():
        csv_group = csv_groups.get(hfr_code)
        if csv_group:
            latest = csv_group["latest_date"]
            date_display = latest.strftime("%Y-%m-%d") if latest else "No valid date found"
        else:
            date_display = "No Reports"

        block_name = info["block_name"] or (csv_group["block_name"] if csv_group else "")
        category = info["category"] or (csv_group["category"] if csv_group else "")

        table_rows.append(
            {
                "Lab Name": or_default(info["lab_name"], "No Data"),
                "HFR ID": hfr_code,
                "Latest Result Date": date_display,
                "Block Name": or_default(block_name, "No Data"),
                "Category": or_default(category, "No Data"),
                "Lab Type": or_default(info["lab_type"], "No Data"),
            }
        )

    not_in_master = []
    for hfr_id, group in csv_groups.items():
        if hfr_id not in master_labs:
            latest = group["latest_date"]
            date_display = latest.strftime("%Y-%m-%d") if latest else "No valid date found"
            display_name = f"[NOT IN MASTER FILE] {group['lab_name']}"
            table_rows.append(
                {
                    "Lab Name": display_name,
                    "HFR ID": hfr_id,
                    "Latest Result Date": date_display,
                    "Block Name": or_default(group["block_name"], "No data"),
                    "Category": or_default(group["category"], "No data"),
                    "Lab Type": "No data",
                }
            )
            not_in_master.append({"lab_name": group["lab_name"], "hfr_id": hfr_id, "group": group})

    table_rows.sort(key=lambda x: (x["Lab Name"] or "").lower())

    # -----------------------------------------------------------------
    # Overview metrics
    # -----------------------------------------------------------------
    total_labs = len(table_rows)
    no_reports_count = sum(1 for r in table_rows if r["Latest Result Date"] == "No Reports")
    not_in_master_count = len(not_in_master)
    reported_count = total_labs - no_reports_count - not_in_master_count

    st.markdown('<hr class="lt-hairline"/>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="lt-stat-grid">
            <div class="lt-stat">
                <div class="lt-stat-label">Total Labs Tracked</div>
                <div class="lt-stat-value">{total_labs}</div>
            </div>
            <div class="lt-stat">
                <div class="lt-stat-label">Reported</div>
                <div class="lt-stat-value lt-stat-good">{reported_count}</div>
            </div>
            <div class="lt-stat">
                <div class="lt-stat-label">No Reports</div>
                <div class="lt-stat-value lt-stat-warn">{no_reports_count}</div>
            </div>
            <div class="lt-stat">
                <div class="lt-stat-label">Not In Master</div>
                <div class="lt-stat-value lt-stat-danger">{not_in_master_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # Block attendance checker
    # -----------------------------------------------------------------
    st.markdown('<hr class="lt-hairline"/>', unsafe_allow_html=True)
    st.header("Block Reporting Calendar")
    st.caption("See which labs in a block filed a report on each day of a date range.")

    block_names_available = sorted(
        {r["Block Name"] for r in table_rows if r["Block Name"] not in ("No Data", "No data")}
    )

    if not block_names_available:
        st.info("No labs have a usable Block Name to check attendance for.")
    else:
        attn_col1, attn_col2, attn_col3 = st.columns(3)
        with attn_col1:
            selected_block = st.selectbox("Block Name", block_names_available)
        with attn_col2:
            start_date = st.date_input("Start Date", key="attendance_start")
        with attn_col3:
            end_date = st.date_input("End Date", key="attendance_end")

        if start_date and end_date:
            if start_date > end_date:
                st.error("Start Date must be on or before End Date.")
            else:
                num_days = (end_date - start_date).days + 1
                if num_days > 120:
                    st.warning(
                        f"That's a {num_days}-day range, which will produce a very wide table. "
                        "Consider narrowing it for readability."
                    )

                labs_in_block = [r for r in table_rows if r["Block Name"] == selected_block]

                if not labs_in_block:
                    st.info(f"No labs found for block '{selected_block}'.")
                else:
                    date_list = []
                    d = start_date
                    while d <= end_date:
                        date_list.append(d)
                        d += timedelta(days=1)

                    st.markdown(
                        f"**{selected_block}** &nbsp;·&nbsp; "
                        f"{start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
                    )
                    st.markdown(
                        '<div class="lt-legend">'
                        '<span class="lt-legend-item"><span class="lt-dot lt-dot-good"></span>report filed</span>'
                        '<span class="lt-legend-item"><span class="lt-dot lt-dot-danger"></span>no report</span>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    header_cells = "".join(
                        f"<th>{html.escape(day.strftime('%b %d'))}</th>" for day in date_list
                    )
                    body_rows = []
                    for lab in labs_in_block:
                        hfr_id = lab["HFR ID"]
                        dates_present = csv_groups.get(hfr_id, {}).get("dates_present", set())
                        day_cells = "".join(
                            f'<td class="{"lt-cal-good" if day in dates_present else "lt-cal-bad"}">'
                            f'{"✓" if day in dates_present else "✗"}</td>'
                            for day in date_list
                        )
                        body_rows.append(
                            f"<tr><td class='lt-cal-label'>{html.escape(lab['Lab Name'])}</td>"
                            f"<td class='lt-cal-id'>{html.escape(hfr_id)}</td>{day_cells}</tr>"
                        )

                    calendar_html = f"""
                    <div class="lt-cal-wrap">
                        <table class="lt-cal-table">
                            <thead><tr><th>Lab Name</th><th>HFR ID</th>{header_cells}</tr></thead>
                            <tbody>{''.join(body_rows)}</tbody>
                        </table>
                    </div>
                    """
                    st.markdown(calendar_html, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------
    st.markdown('<hr class="lt-hairline"/>', unsafe_allow_html=True)
    st.header("Lab Report Status")
    st.caption("Filter by Block Name, Category, or Lab Type to narrow the table below.")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    block_options = sorted({r["Block Name"] for r in table_rows})
    category_options = sorted({r["Category"] for r in table_rows})
    labtype_options = sorted({r["Lab Type"] for r in table_rows})

    with filter_col1:
        selected_blocks = st.multiselect("Filter by Block Name", block_options)
    with filter_col2:
        selected_categories = st.multiselect("Filter by Category", category_options)
    with filter_col3:
        selected_labtypes = st.multiselect("Filter by Lab Type", labtype_options)

    filtered_rows = table_rows
    if selected_blocks:
        filtered_rows = [r for r in filtered_rows if r["Block Name"] in selected_blocks]
    if selected_categories:
        filtered_rows = [r for r in filtered_rows if r["Category"] in selected_categories]
    if selected_labtypes:
        filtered_rows = [r for r in filtered_rows if r["Lab Type"] in selected_labtypes]

    st.caption(f"Showing **{len(filtered_rows)}** of **{len(table_rows)}** labs")
    st.dataframe(filtered_rows, use_container_width=True, hide_index=True)

    # Flag unparsed dates
    flagged = {hfr_id: g["unparsed"] for hfr_id, g in csv_groups.items() if g["unparsed"] > 0}
    if flagged:
        with st.expander("Labs with unparseable date entries"):
            st.write(
                "These entries (by HFR ID) had at least one 'Result Date' value that "
                "couldn't be parsed with the supported date formats and was ignored."
            )
            for hfr_id, count in sorted(flagged.items()):
                lab_name = csv_groups[hfr_id]["lab_name"]
                st.write(f"- {lab_name} (HFR ID: {hfr_id}): {count} unparseable entr{'y' if count == 1 else 'ies'}")

    # -----------------------------------------------------------------
    # Labs found in CSV but not in master -> warn + offer updated master
    # -----------------------------------------------------------------
    st.markdown('<hr class="lt-hairline"/>', unsafe_allow_html=True)

    if not_in_master:
        st.warning(f"{len(not_in_master)} lab(s) were found in the CSV but are not in the master file:")
        for entry in not_in_master:
            st.write(f"- **{entry['lab_name']}** · HFR ID `{entry['hfr_id']}`")

        try:
            new_rows_cells = []
            for entry in not_in_master:
                group = entry["group"]
                cells = [
                    (master_lab_col, entry["lab_name"]),
                    (master_hfr_col, entry["hfr_id"]),
                ]
                if group["block_name"]:
                    cells.append((master_block_col, group["block_name"]))
                if group["category"]:
                    cells.append((master_category_col, group["category"]))
                new_rows_cells.append(cells)

            updated_master_bytes = append_rows_to_master(
                master_bytes, sheet_path, new_rows_cells, master_max_row
            )
            st.download_button(
                label="Download Updated Master File",
                data=updated_master_bytes,
                file_name="master_labs_updated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.caption(
                "The updated file adds these labs' Lab Name, HFR Code, Block Name, and Category "
                "(where available from the CSV) to the master sheet. Lab Type is left blank for the new rows."
            )
        except Exception as e:
            st.error(f"Could not generate an updated master file: {e}")
    else:
        st.success("All labs in the CSV are present in the master file.")

    st.markdown(
        '<div class="lt-footer">LABS TRACKER · Matching is performed by HFR ID / HFR Code, not lab name</div>',
        unsafe_allow_html=True,
    )
