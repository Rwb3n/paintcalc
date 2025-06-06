import streamlit as st

# Preset Configuration (Example)
preset = {
    "name": "Standard Residential",
    "hourly_rate": 35.0,
    "markup_percent": 20.0,
    "material_contingency": 5.0,
    "labour_contingency": 10.0,
    "vat_applicable": True,
    "vat_rate": 20.0,
    "material": {
        "cost_per_litre": 15.0,
        "coverage_per_litre": 12.0
    },
    "labour_rate_per_sqm": 0.15
}

# Session storage
if "rooms" not in st.session_state:
    st.session_state.rooms = []

# Layout
st.set_page_config(layout="wide")
st.title("🎨 Quote Builder Prototype")

tab1, tab2, tab3 = st.tabs(["Room Details", "Estimates", "Summary"])

# Tab 1: Room Inputs
with tab1:
    st.header("1. Add Room Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Room Name")
    with col2:
        area = st.number_input("Wall Area (sqm)", min_value=0.0, value=20.0)
    with col3:
        coats = st.number_input("Number of Coats", min_value=1, value=2)

    if st.button("➕ Add Room"):
        st.session_state.rooms.append({
            "name": name, "area": area, "coats": coats
        })

    if st.session_state.rooms:
        st.markdown("### 🏠 Rooms Added")
        for r in st.session_state.rooms:
            st.write(f"- {r['name']}: {r['area']} sqm × {r['coats']} coats")

# Tab 2: Calculation
with tab2:
    st.header("2. Labour & Material Estimate")
    total_area = sum(r['area'] * r['coats'] for r in st.session_state.rooms)
    litres = total_area / preset["material"]["coverage_per_litre"]
    material_cost = litres * preset["material"]["cost_per_litre"]
    labour_hours = total_area * preset["labour_rate_per_sqm"]
    labour_cost = labour_hours * preset["hourly_rate"]

    st.metric("Total Paint Needed (litres)", f"{litres:.2f} L")
    st.metric("Material Cost", f"£{material_cost:.2f}")
    st.metric("Labour Hours", f"{labour_hours:.2f}")
    st.metric("Labour Cost", f"£{labour_cost:.2f}")

# Tab 3: Summary
with tab3:
    st.header("3. Final Summary")
    mat_cont = material_cost * preset["material_contingency"] / 100
    lab_cont = labour_cost * preset["labour_contingency"] / 100
    subtotal = material_cost + mat_cont + labour_cost + lab_cont
    markup = subtotal * preset["markup_percent"] / 100
    total = subtotal + markup
    vat = total * preset["vat_rate"] / 100 if preset["vat_applicable"] else 0
    grand_total = total + vat

    st.markdown("### 💰 Totals")
    st.write(f"Material + Contingency: £{material_cost:.2f} + £{mat_cont:.2f}")
    st.write(f"Labour + Contingency: £{labour_cost:.2f} + £{lab_cont:.2f}")
    st.write(f"Markup ({preset['markup_percent']}%): £{markup:.2f}")
    st.write(f"VAT ({preset['vat_rate']}%): £{vat:.2f}")
    st.markdown(f"## ✅ Grand Total: £{grand_total:.2f}")
