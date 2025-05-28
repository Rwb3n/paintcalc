import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trade Quote Wizard", layout="wide")
st.title("🏗️ Trade Quote Wizard: Painting & Decorating")

# 1. Scope Selector
mode = st.selectbox(
    "What are you quoting?",
    ["Paint Only", "Strip Only", "Full Package"],
    help="Choose 'Paint Only' for painting tasks, 'Strip Only' for wallpaper removal, or 'Full Package' for both."
)

# 2. Core Inputs
with st.expander("📐 Surface Areas", expanded=True if mode != "Strip Only" else False):
    walls = st.number_input("Walls (m²)", min_value=0.0, step=0.1, value=0.0)
    ceilings = st.number_input("Ceilings (m²)", min_value=0.0, step=0.1, value=0.0)
    skirting = st.number_input("Skirting (m)", min_value=0.0, step=0.1, value=0.0)

with st.expander("🚪 Doors & Windows", expanded=True):
    doors = st.number_input("Doors (#)", min_value=0, step=1, value=0)
    windows = st.number_input("Windows (#)", min_value=0, step=1, value=0)

# 3. Extras based on mode
if mode in ["Strip Only", "Full Package"]:
    wallpaper_jobs = st.number_input(
        "Wallpaper Removal Jobs (#)", min_value=0, step=1, value=0,
        help="Number of separate wallpaper removal tasks (rooms or visits)."
    )
else:
    wallpaper_jobs = 0

# 4. Advanced Settings
with st.expander("⚙️ Advanced Settings", expanded=False):
    st.markdown("**Rates & Flags**")
    walls_rate = st.number_input("Walls Rate (£/m²)", min_value=0.0, value=5.0, step=0.1)
    ceilings_rate = st.number_input("Ceilings Rate (£/m²)", min_value=0.0, value=5.0, step=0.1)
    skirting_rate = st.number_input("Skirting Rate (£/m)", min_value=0.0, value=5.0, step=0.1)
    doors_rate = st.number_input("Doors Rate (£ each)", min_value=0.0, value=25.0, step=0.1)
    windows_rate = st.number_input("Windows Rate (£ each)", min_value=0.0, value=25.0, step=0.1)
    wallpaper_rate = st.number_input("Wallpaper Rate (£/job)", min_value=0.0, value=250.0, step=1.0)
    wallpaper_min_fee = st.number_input("Wallpaper Min Fee (£)", min_value=0.0, value=250.0, step=1.0)
    general_labour_rate = st.number_input("General Labour (£/job)", min_value=0.0, value=250.0, step=1.0)
    primer_area = st.number_input("Primer Area (m²)", min_value=0.0, step=0.1, value=0.0)
    primer_rate = st.number_input("Primer Rate (£/m²)", min_value=0.0, value=2.0, step=0.1)
    include_prep = st.checkbox("Include Surface Prep & Filler", value=True)
    prep_rate = st.number_input("Prep & Filler (£ flat)", min_value=0.0, value=100.0, step=1.0)
    visits = st.number_input("Visits for Materials", min_value=1, step=1, value=1)
    materials_base = st.number_input("Materials Base (£)", min_value=0.0, value=150.0, step=1.0)
    materials_extra = st.number_input("Materials Extra (£/extra visit)", min_value=0.0, value=30.0, step=1.0)

# 5. Rate Defaults if not in advanced
if 'walls_rate' not in locals(): walls_rate = 5.0
if 'ceilings_rate' not in locals(): ceilings_rate = 5.0
if 'skirting_rate' not in locals(): skirting_rate = 5.0
if 'doors_rate' not in locals(): doors_rate = 25.0
if 'windows_rate' not in locals(): windows_rate = 25.0
if 'wallpaper_rate' not in locals(): wallpaper_rate = 250.0
if 'wallpaper_min_fee' not in locals(): wallpaper_min_fee = wallpaper_rate
if 'general_labour_rate' not in locals(): general_labour_rate = 250.0
if 'primer_area' not in locals(): primer_area = 0.0
if 'primer_rate' not in locals(): primer_rate = 2.0
if 'include_prep' not in locals(): include_prep = True
if 'prep_rate' not in locals(): prep_rate = 100.0
if 'visits' not in locals(): visits = 1
if 'materials_base' not in locals(): materials_base = 150.0
if 'materials_extra' not in locals(): materials_extra = 30.0

# 6. Calculations
walls_total = walls * walls_rate
ceilings_total = ceilings * ceilings_rate
skirting_total = skirting * skirting_rate
doors_total = doors * doors_rate
windows_total = windows * windows_rate
wallpaper_total = wallpaper_jobs * max(wallpaper_rate, wallpaper_min_fee)
general_labour_total = general_labour_rate if general_labour_rate and (mode=="Full Package" or mode=="Strip Only") else 0
primer_total = primer_area * primer_rate
prep_total = prep_rate if include_prep else 0
materials_total = materials_base + max(0, (visits - 1) * materials_extra)

# 7. Build item list and filter zeros
items = []
def add_item(name, qty, unit, rate, total):
    if total and total > 0:
        items.append((name, qty, unit, rate, total))

add_item("Walls (m²)", walls, "m²", walls_rate, walls_total)
add_item("Ceilings (m²)", ceilings, "m²", ceilings_rate, ceilings_total)
add_item("Skirting (m)", skirting, "m", skirting_rate, skirting_total)
add_item("Doors (#)", doors, "each", doors_rate, doors_total)
add_item("Windows (#)", windows, "each", windows_rate, windows_total)
if wallpaper_jobs > 0:
    add_item("Wallpaper Removal (per job)", wallpaper_jobs, "job", f"min £{wallpaper_min_fee}", wallpaper_total)
add_item("General Labour (Flat Fee)", 1, "job", general_labour_rate, general_labour_total)
if primer_area > 0:
    add_item("Primer Application", primer_area, "m²", primer_rate, primer_total)
if include_prep:
    add_item("Surface Prep & Filler", 1, "job", prep_rate, prep_total)
add_item("Materials & Setup", visits, "visits", f"base £{materials_base} + £{materials_extra}/extra", materials_total)

# Summary
st.header("📝 Quote Summary")
df = pd.DataFrame(items, columns=["Item", "Quantity", "Unit", "Rate", "Total (£)"])
st.table(df)

subtotal = sum([x[4] for x in items])
vat = subtotal * 0.2
total = subtotal + vat
st.markdown(f"**Subtotal:** £{subtotal:,.2f}")
st.markdown(f"**VAT (20%):** £{vat:,.2f}")
st.markdown(f"**Total:** £{total:,.2f}")
