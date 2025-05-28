import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Trade Quote Wizard", layout="wide")

# Inject CSS to adjust sidebar width and font size
st.markdown(
    """
    <style>
    /* 1. Expand sidebar width */
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 650px;  /* adjust width as needed */
    }
    /* 2. Shrink text in sidebar table */
    [data-testid="stSidebar"] .stTable td, 
    [data-testid="stSidebar"] .stTable th {
        font-size: 12px !important;
        padding: 0.25rem 0.5rem !important;
    }
    /* 3. Reduce padding around sidebar content */
    [data-testid="stSidebar"] .css-1oe6wy3 {
        padding: 0.1rem 0.1rem 0.1rem 0.1rem !important;
    }
    </style>
    """, unsafe_allow_html=True
)

st.write("✅ Sidebar CSS injected: wider, smaller text, tighter padding.")

# Title
st.title("🏗️ Trade Quote Wizard: Painting & Decorating")

# Instructions
st.markdown("""
**Tip:** Enter `0` to skip an item.  
Use the form below to get a quick estimate. Totals are always visible on the right.
""")

# 1. Scope Selector
mode = st.selectbox(
    "What are you quoting?",
    ["Paint Only", "Strip Only", "Full Package"],
    help="Choose 'Paint Only' for painting tasks, 'Strip Only' for wallpaper removal, or 'Full Package' for both."
)

# 2. Core Inputs in columns
st.subheader("📐 Surface Areas & Lengths")
col1, col2, col3 = st.columns(3)
with col1:
    walls = st.number_input("Walls area (m²)", min_value=0.0, step=0.1, value=0.0)
with col2:
    ceilings = st.number_input("Ceilings area (m²)", min_value=0.0, step=0.1, value=0.0)
with col3:
    skirting = st.number_input("Skirting length (m)", min_value=0.0, step=0.1, value=0.0)

st.subheader("🚪 Counts")
col4, col5 = st.columns(2)
with col4:
    doors = st.number_input("Doors (#)", min_value=0, step=1, value=0)
with col5:
    windows = st.number_input("Windows (#)", min_value=0, step=1, value=0)

# 3. Extras based on mode
if mode in ["Strip Only", "Full Package"]:
    wallpaper_jobs = st.number_input(
        "Rooms to strip (wallpaper removal) (#)", min_value=0, step=1, value=0,
        help="Number of rooms or visits for wallpaper removal."
    )
else:
    wallpaper_jobs = 0

# 4. Edit Rates Toggle
edit_rates = st.checkbox("🔧 Edit Rates & Advanced Settings", value=False)

# 5. Rates & Advanced
if edit_rates:
    st.subheader("⚙️ Advanced Settings")
    col6, col7, col8 = st.columns(3)
    with col6:
        walls_rate = st.number_input("Walls Rate (£/m²)", min_value=0.0, value=5.0, step=0.1)
        ceilings_rate = st.number_input("Ceilings Rate (£/m²)", min_value=0.0, value=5.0, step=0.1)
        skirting_rate = st.number_input("Skirting Rate (£/m)", min_value=0.0, value=5.0, step=0.1)
    with col7:
        doors_rate = st.number_input("Doors Rate (£ each)", min_value=0.0, value=25.0, step=0.1)
        windows_rate = st.number_input("Windows Rate (£ each)", min_value=0.0, value=25.0, step=0.1)
        wallpaper_rate = st.number_input("Wallpaper Rate (£/job)", min_value=0.0, value=250.0, step=1.0)
        wallpaper_min_fee = st.number_input("Min Fee - Wallpaper (£)", min_value=0.0, value=250.0, step=1.0)
    with col8:
        general_labour_rate = st.number_input("General Labour (£/job)", min_value=0.0, value=250.0, step=1.0)
        primer_rate = st.number_input("Primer Rate (£/m²)", min_value=0.0, value=2.0, step=0.1)
        include_prep = st.checkbox("Include Prep & Filler", value=True)
        prep_rate = st.number_input("Prep & Filler (£ flat)", min_value=0.0, value=100.0, step=1.0)
        visits = st.number_input("Visits for Materials", min_value=1, step=1, value=1)
        materials_base = st.number_input("Materials Base (£)", min_value=0.0, value=150.0, step=1.0)
        materials_extra = st.number_input("Materials Extra (£/extra visit)", min_value=0.0, value=30.0, step=1.0)
else:
    # Defaults
    walls_rate, ceilings_rate, skirting_rate = 5.0, 5.0, 5.0
    doors_rate, windows_rate = 25.0, 25.0
    wallpaper_rate, wallpaper_min_fee = 250.0, 250.0
    general_labour_rate = 250.0
    primer_rate = 2.0
    include_prep, prep_rate = True, 100.0
    visits, materials_base, materials_extra = 1, 150.0, 30.0

# 6. Calculations
walls_total = walls * walls_rate
ceilings_total = ceilings * ceilings_rate
skirting_total = skirting * skirting_rate
doors_total = doors * doors_rate
windows_total = windows * windows_rate
wallpaper_total = wallpaper_jobs * max(wallpaper_rate, wallpaper_min_fee)
general_labour_total = general_labour_rate if mode in ["Strip Only", "Full Package"] else 0
primer_total = walls * primer_rate if walls > 0 else 0
prep_total = prep_rate if include_prep else 0
materials_total = materials_base + max(0, (visits - 1) * materials_extra)

# 7. Build and display summary in sidebar (sticky)
st.sidebar.header("📝 Quote Summary")
items = []
def add_item(name, qty, unit, rate, total):
    if total > 0:
        items.append((name, qty, unit, rate, total))

add_item("Walls", walls, "m²", walls_rate, walls_total)
add_item("Ceilings", ceilings, "m²", ceilings_rate, ceilings_total)
add_item("Skirting", skirting, "m", skirting_rate, skirting_total)
add_item("Doors", doors, "#", doors_rate, doors_total)
add_item("Windows", windows, "#", windows_rate, windows_total)
if wallpaper_jobs > 0:
    add_item("Wallpaper Removal", wallpaper_jobs, "job", f"min £{wallpaper_min_fee}", wallpaper_total)
if mode in ["Strip Only", "Full Package"]:
    add_item("General Labour (Flat Fee)", 1, "job", general_labour_rate, general_labour_total)
add_item("Primer Application", walls, "m²", primer_rate, primer_total)
if include_prep:
    add_item("Surface Prep & Filler", 1, "job", prep_rate, prep_total)
add_item("Materials & Setup", visits, "visits", f"base £{materials_base} + £{materials_extra}/extra", materials_total)

df = pd.DataFrame(items, columns=["Item", "Quantity", "Unit", "Rate", "Total (£)"])
st.sidebar.table(df)

subtotal = df["Total (£)"].sum()
vat = subtotal * 0.2
total = subtotal + vat
st.sidebar.markdown(f"**Subtotal:** £{subtotal:,.2f}")
st.sidebar.markdown(f"**VAT (20%):** £{vat:,.2f}")
st.sidebar.markdown(f"**Total:** £{total:,.2f}")

