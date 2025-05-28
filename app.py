import streamlit as st
import pandas as pd

st.title("Painting & Decorating Cost Quote Calculator")

# Job Details
st.header("Job Details")
walls_qty = st.number_input("Walls area (m²)", min_value=0.0, value=0.0, step=0.1)
ceilings_qty = st.number_input("Ceilings area (m²)", min_value=0.0, value=0.0, step=0.1)
skirting_qty = st.number_input("Skirting length (m)", min_value=0.0, value=0.0, step=0.1)
doors_qty = st.number_input("Number of doors", min_value=0, value=0, step=1)
windows_qty = st.number_input("Number of windows", min_value=0, value=0, step=1)
wallpaper_jobs = st.number_input("Number of wallpaper removal jobs", min_value=0, value=0, step=1)
general_labour_jobs = st.number_input("General labour jobs (flat fee)", min_value=0, value=1, step=1)
primer_area = st.number_input("Primer area (m²)", min_value=0.0, value=0.0, step=0.1)
include_prep = st.checkbox("Include surface prep & filler", value=True)
visits = st.number_input("Number of visits (materials)", min_value=0, value=1, step=1)

# Rates
st.header("Rates (Editable)")
walls_rate = st.number_input("Rate - Walls (£/m²)", min_value=0.0, value=5.0, step=0.1)
ceilings_rate = st.number_input("Rate - Ceilings (£/m²)", min_value=0.0, value=5.0, step=0.1)
skirting_rate = st.number_input("Rate - Skirting (£/m)", min_value=0.0, value=5.0, step=0.1)
doors_rate = st.number_input("Rate - Doors (£ each)", min_value=0.0, value=25.0, step=0.1)
windows_rate = st.number_input("Rate - Windows (£ each)", min_value=0.0, value=25.0, step=0.1)
wallpaper_rate = st.number_input("Rate - Wallpaper removal (£/job)", min_value=0.0, value=250.0, step=1.0)
wallpaper_min_fee = st.number_input("Min fee - Wallpaper removal (£)", min_value=0.0, value=250.0, step=1.0)
general_labour_rate = st.number_input("Rate - General labour (£/job)", min_value=0.0, value=250.0, step=1.0)
primer_rate = st.number_input("Rate - Primer (£/m²)", min_value=0.0, value=2.0, step=0.1)
prep_rate = st.number_input("Rate - Surface prep & filler (flat)", min_value=0.0, value=100.0, step=1.0)
materials_base = st.number_input("Materials base rate (£)", min_value=0.0, value=150.0, step=1.0)
materials_extra = st.number_input("Materials extra visit rate (£)", min_value=0.0, value=30.0, step=1.0)

# Calculations
walls_total = walls_qty * walls_rate
ceilings_total = ceilings_qty * ceilings_rate
skirting_total = skirting_qty * skirting_rate
doors_total = doors_qty * doors_rate
windows_total = windows_qty * windows_rate
wallpaper_total = wallpaper_jobs * max(wallpaper_rate, wallpaper_min_fee)
general_labour_total = general_labour_jobs * general_labour_rate
primer_total = primer_area * primer_rate
prep_total = prep_rate if include_prep and general_labour_jobs > 0 else 0
materials_total = materials_base + max(0, (visits - 1) * materials_extra) if visits > 0 else 0

# Display Breakdown
items = [
    ("Walls", walls_qty, "m²", walls_rate, walls_total),
    ("Ceilings", ceilings_qty, "m²", ceilings_rate, ceilings_total),
    ("Skirting", skirting_qty, "m", skirting_rate, skirting_total),
    ("Doors", doors_qty, "each", doors_rate, doors_total),
    ("Windows", windows_qty, "each", windows_rate, windows_total),
    ("Wallpaper Removal", wallpaper_jobs, "job", f"min £{wallpaper_min_fee}", wallpaper_total),
    ("General Labour", general_labour_jobs, "job", general_labour_rate, general_labour_total),
    ("Primer Application", primer_area, "m²", primer_rate, primer_total),
    ("Surface Prep & Filler", 1 if include_prep else 0, "job", prep_rate, prep_total),
    ("Materials & Setup", visits, "visits", f"base £{materials_base} + £{materials_extra}/extra", materials_total),
]

df = pd.DataFrame(items, columns=["Item", "Quantity", "Unit", "Rate", "Total (£)"])
st.table(df)

subtotal = sum([row[4] for row in items])
vat = subtotal * 0.2
total = subtotal + vat

st.markdown(f"**Subtotal:** £{subtotal:,.2f}")
st.markdown(f"**VAT (20%):** £{vat:,.2f}")
st.markdown(f"**Total:** £{total:,.2f}")
