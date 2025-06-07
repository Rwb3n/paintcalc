import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, Literal, List, Union, Any # Added Any for quote_room/job return dicts
from enum import Enum
import uuid # For RoomInput ID generation later

# --- DATA STRUCTURES (NEW) ---
class PaintSurface(Enum):
    WALLS_STANDARD = 'walls_standard'
    WALLS_DURABLE = 'walls_durable'
    CEILING = 'ceiling'
    WOODWORK = 'woodwork'
    DOOR_FRAME = 'door_frame'
    WINDOW_FRAME = 'window_frame'
    RADIATOR = 'radiator'
    OTHER = 'other'

@dataclass
class MaterialRate:
  surfaceType: PaintSurface
  coveragePerLitre: float
  costPerLitre: float

@dataclass
class LabourRate:
  task: str
  unit: Literal['sqm', 'm', 'item', 'hour']
  hoursPerUnitPerCoat: float

@dataclass
class PresetConfig:
  materialRates: Dict[PaintSurface, MaterialRate]
  labourRates: Dict[str, LabourRate]
  miscCosts: Dict[str, float]
  markupPercent: float
  vatApplicable: bool
  materialContingencyPercent: float
  labourContingencyPercent: float
  defaultTeamSize: int
  hourlyChargeRate: float

@dataclass
class RoomInput:
  id: str = field(default_factory=lambda: str(uuid.uuid4()))
  name: str = "New Room"
  wallArea: float = 0.0
  ceilingArea: float = 0.0
  woodworkLength: float = 0.0
  doorCount: int = 0
  windowCount: int = 0
  coatsWalls: int = 2
  coatsCeiling: int = 1
  coatsWoodwork: int = 1
  coatsDoors: int = 2
  coatsWindows: int = 2
  paintChoiceWalls: PaintSurface = PaintSurface.WALLS_STANDARD
  paintChoiceCeiling: PaintSurface = PaintSurface.CEILING
  paintChoiceWoodwork: PaintSurface = PaintSurface.WOODWORK
  heavyPrep: bool = False
  wallpaperArea: float = 0.0
  removeWallpaperArea: float = 0.0
  notes: str = ""

# --- CORE CALCULATION FUNCTIONS ---
def litres_needed(area_or_length: float, coats: int, coverage_per_litre: float) -> float:
    if coverage_per_litre == 0: return 0.0
    return (area_or_length * coats) / coverage_per_litre

def material_cost_for_doors_windows(count: int, coats: int, cost_per_item_per_coat: float) -> float:
    return float(count * coats * cost_per_item_per_coat)

def quote_room(room: RoomInput, cfg: PresetConfig) -> Dict[str, Any]:
    m_rates = cfg.materialRates; l_rates = cfg.labourRates; misc_costs = cfg.miscCosts
    wall_paint_cost = 0.0
    if room.wallArea > 0 and room.coatsWalls > 0 and room.paintChoiceWalls in m_rates:
        wall_material_rate = m_rates[room.paintChoiceWalls]
        wall_paint_cost = litres_needed(room.wallArea, room.coatsWalls, wall_material_rate.coveragePerLitre) * wall_material_rate.costPerLitre
    ceiling_paint_cost = 0.0
    if room.ceilingArea > 0 and room.coatsCeiling > 0 and room.paintChoiceCeiling in m_rates:
        ceiling_material_rate = m_rates[room.paintChoiceCeiling]
        ceiling_paint_cost = litres_needed(room.ceilingArea, room.coatsCeiling, ceiling_material_rate.coveragePerLitre) * ceiling_material_rate.costPerLitre
    wood_paint_cost = 0.0
    if room.woodworkLength > 0 and room.coatsWoodwork > 0 and room.paintChoiceWoodwork in m_rates:
        wood_material_rate = m_rates[room.paintChoiceWoodwork]
        wood_paint_cost = litres_needed(room.woodworkLength, room.coatsWoodwork, wood_material_rate.coveragePerLitre) * wood_material_rate.costPerLitre
    door_mat_cost = 0.0
    if room.doorCount > 0 and room.coatsDoors > 0:
        door_mat_cost = material_cost_for_doors_windows(room.doorCount, room.coatsDoors, misc_costs.get('door_material_cost_per_item_per_coat', 0.0))
    window_mat_cost = 0.0
    if room.windowCount > 0 and room.coatsWindows > 0:
        window_mat_cost = material_cost_for_doors_windows(room.windowCount, room.coatsWindows, misc_costs.get('window_material_cost_per_item_per_coat', 0.0))
    prep_material_rate_key = 'prep_materials_cost_per_sqm_heavy' if room.heavyPrep else 'prep_materials_cost_per_sqm_general'
    prep_mat_cost = (room.wallArea + room.ceilingArea) * misc_costs.get(prep_material_rate_key, 0.0)
    base_materials_cost = wall_paint_cost + ceiling_paint_cost + wood_paint_cost + door_mat_cost + window_mat_cost + misc_costs.get('sundries_per_room_fixed', 0.0) + prep_mat_cost
    buffered_materials_cost = base_materials_cost * (1 + cfg.materialContingencyPercent / 100)
    hours = 0.0
    if room.wallArea > 0 and room.coatsWalls > 0 and 'paint_walls' in l_rates: hours += room.wallArea * room.coatsWalls * l_rates['paint_walls'].hoursPerUnitPerCoat
    if room.ceilingArea > 0 and room.coatsCeiling > 0 and 'paint_ceiling' in l_rates: hours += room.ceilingArea * room.coatsCeiling * l_rates['paint_ceiling'].hoursPerUnitPerCoat
    if room.woodworkLength > 0 and room.coatsWoodwork > 0 and 'paint_woodwork' in l_rates: hours += room.woodworkLength * room.coatsWoodwork * l_rates['paint_woodwork'].hoursPerUnitPerCoat
    if room.doorCount > 0 and room.coatsDoors > 0 and 'paint_door_item' in l_rates: hours += room.doorCount * room.coatsDoors * l_rates['paint_door_item'].hoursPerUnitPerCoat
    if room.windowCount > 0 and room.coatsWindows > 0 and 'paint_window_item' in l_rates: hours += room.windowCount * room.coatsWindows * l_rates['paint_window_item'].hoursPerUnitPerCoat
    if room.removeWallpaperArea > 0 and 'wallpaper_removal_sqm' in l_rates: hours += room.removeWallpaperArea * l_rates['wallpaper_removal_sqm'].hoursPerUnitPerCoat
    prep_labour_rate_key = 'prep_sqm_heavy' if room.heavyPrep else 'prep_sqm_general'
    if (room.wallArea + room.ceilingArea > 0) and prep_labour_rate_key in l_rates: hours += (room.wallArea + room.ceilingArea) * l_rates[prep_labour_rate_key].hoursPerUnitPerCoat
    buffered_hours = hours * (1 + cfg.labourContingencyPercent / 100)
    total_labour_cost = buffered_hours * cfg.hourlyChargeRate
    return {"roomId": room.id, "roomName": room.name, "materialsCost": round(buffered_materials_cost, 2), "labourCost": round(total_labour_cost, 2), "totalCost": round(buffered_materials_cost + total_labour_cost, 2)}

def quote_job(rooms: List[RoomInput], cfg: PresetConfig, add_ons: Dict[str, float] = None) -> Dict[str, Any]:
    if add_ons is None: add_ons = {}
    room_breakdowns = [quote_room(r, cfg) for r in rooms]
    total_materials_cost = sum(r['materialsCost'] for r in room_breakdowns)
    total_labour_cost = sum(r['labourCost'] for r in room_breakdowns)
    total_add_ons_cost = sum(float(v) for v in add_ons.values() if isinstance(v, (int, float)))
    sub_total_before_markup = total_materials_cost + total_labour_cost + total_add_ons_cost
    markup_amount = sub_total_before_markup * (cfg.markupPercent / 100)
    total_before_vat = sub_total_before_markup + markup_amount
    vat_amount = 0.0; VAT_RATE = 0.20
    if cfg.vatApplicable: vat_amount = total_before_vat * VAT_RATE
    grand_total = total_before_vat + vat_amount
    return {
        "roomBreakdowns": room_breakdowns,
        "totalMaterialsCost": round(total_materials_cost, 2),
        "totalLabourCost": round(total_labour_cost, 2),
        "totalAddOnsCost": round(total_add_ons_cost, 2),
        "subTotalBeforeMarkup": round(sub_total_before_markup, 2),
        "markupAmount": round(markup_amount, 2),
        "totalBeforeVAT": round(total_before_vat, 2),
        "vatAmount": round(vat_amount, 2),
        "grandTotal": round(grand_total, 2)
    }

# --- DEFAULT PRESET CONFIGURATION ---
DEFAULT_PRESET_CONFIG = PresetConfig(
    materialRates={
        PaintSurface.WALLS_STANDARD: MaterialRate(surfaceType=PaintSurface.WALLS_STANDARD, coveragePerLitre=12.0, costPerLitre=1.80),
        PaintSurface.WALLS_DURABLE: MaterialRate(surfaceType=PaintSurface.WALLS_DURABLE, coveragePerLitre=10.0, costPerLitre=2.75),
        PaintSurface.CEILING: MaterialRate(surfaceType=PaintSurface.CEILING, coveragePerLitre=14.0, costPerLitre=1.50),
        PaintSurface.WOODWORK: MaterialRate(surfaceType=PaintSurface.WOODWORK, coveragePerLitre=10.0, costPerLitre=3.50),
        PaintSurface.DOOR_FRAME: MaterialRate(surfaceType=PaintSurface.DOOR_FRAME, coveragePerLitre=10.0, costPerLitre=3.25),
        PaintSurface.WINDOW_FRAME: MaterialRate(surfaceType=PaintSurface.WINDOW_FRAME, coveragePerLitre=10.0, costPerLitre=3.25),
        PaintSurface.RADIATOR: MaterialRate(surfaceType=PaintSurface.RADIATOR, coveragePerLitre=8.0, costPerLitre=4.50),
        PaintSurface.OTHER: MaterialRate(surfaceType=PaintSurface.OTHER, coveragePerLitre=10.0, costPerLitre=2.00),
    },
    labourRates={
        'paint_walls': LabourRate(task='Paint Walls', unit='sqm', hoursPerUnitPerCoat=0.12),
        'paint_ceiling': LabourRate(task='Paint Ceiling', unit='sqm', hoursPerUnitPerCoat=0.15),
        'paint_woodwork': LabourRate(task='Paint Woodwork (skirting, etc.)', unit='m', hoursPerUnitPerCoat=0.20),
        'paint_door_item': LabourRate(task='Paint Door (per item, both sides)', unit='item', hoursPerUnitPerCoat=1.5),
        'paint_window_item': LabourRate(task='Paint Window (per item)', unit='item', hoursPerUnitPerCoat=1.25),
        'prep_sqm_general': LabourRate(task='General Prep (walls/ceiling)', unit='sqm', hoursPerUnitPerCoat=0.05),
        'prep_sqm_heavy': LabourRate(task='Heavy Prep (walls/ceiling)', unit='sqm', hoursPerUnitPerCoat=0.20),
        'wallpaper_removal_sqm': LabourRate(task='Wallpaper Removal', unit='sqm', hoursPerUnitPerCoat=0.33),
    },
    miscCosts={
        'sundries_per_room_fixed': 15.00,
        'door_material_cost_per_item_per_coat': 5.00,
        'window_material_cost_per_item_per_coat': 3.50,
        'prep_materials_cost_per_sqm_general': 0.50,
        'prep_materials_cost_per_sqm_heavy': 1.75,
        'waste_disposal_fixed': 25.00,
    },
    markupPercent=25.0,
    vatApplicable=True,
    materialContingencyPercent=10.0,
    labourContingencyPercent=10.0,
    defaultTeamSize=2,
    hourlyChargeRate=45.0
)

# --- SESSION STATE ---
if "rooms" not in st.session_state:
    st.session_state.rooms: List[RoomInput] = []
if "current_preset" not in st.session_state:
    st.session_state.current_preset: PresetConfig = DEFAULT_PRESET_CONFIG

# --- UI CODE ---
st.set_page_config(layout="wide")
st.title("🎨 New Quote Builder Prototype")
st.caption(f"Using default preset: Hourly Rate £{st.session_state.current_preset.hourlyChargeRate}, Markup {st.session_state.current_preset.markupPercent}%")


# Helper function for selectbox formatting
def format_paint_surface_option(option_value: str) -> str:
    return option_value.replace('_', ' ').title()

# Section for Adding Rooms
st.header("1. Add Room Details")
st.caption("Fill in the details for each room you want to include in the quote.")

with st.form(key='add_room_form', clear_on_submit=True):
    st.subheader("General Room Information")
    name = st.text_input("Room Name", value="Living Room", help="E.g., Living Room, Master Bedroom")
    notes = st.text_area("Notes for this room (e.g., specific instructions, paint colours if known)", height=100)

    st.markdown("---")
    st.subheader("Surface Areas & Counts")
    col1, col2, col3 = st.columns(3)
    with col1:
        wallArea = st.number_input("Wall Area (sqm)", min_value=0.0, value=20.0, step=0.5, help="Total paintable wall area.")
        coatsWalls = st.number_input("Coats for Walls", min_value=1, value=2, step=1)
    with col2:
        ceilingArea = st.number_input("Ceiling Area (sqm)", min_value=0.0, value=10.0, step=0.5, help="Total paintable ceiling area.")
        coatsCeiling = st.number_input("Coats for Ceiling", min_value=1, value=1, step=1)
    with col3:
        woodworkLength = st.number_input("Woodwork Length (m)", min_value=0.0, value=15.0, step=0.5, help="Total length of skirting, architraves, etc.")
        coatsWoodwork = st.number_input("Coats for Woodwork", min_value=1, value=1, step=1)

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        doorCount = st.number_input("Number of Doors", min_value=0, value=1, step=1, help="Count each door (both sides typically).")
        coatsDoors = st.number_input("Coats for Doors", min_value=1, value=2, step=1)
    with dcol2:
        windowCount = st.number_input("Number of Windows", min_value=0, value=1, step=1, help="Count each window.")
        coatsWindows = st.number_input("Coats for Windows", min_value=1, value=2, step=1)

    st.markdown("---")
    st.subheader("Paint Choices")
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        paint_options_walls = [ps.value for ps in PaintSurface if "WALL" in ps.name or ps == PaintSurface.OTHER]
        paintChoiceWalls_str = st.selectbox("Paint Type for Walls", options=paint_options_walls,
                                            index=0, format_func=format_paint_surface_option)
    with pcol2:
        paint_options_ceiling = [ps.value for ps in PaintSurface if "CEILING" in ps.name or ps == PaintSurface.WALLS_STANDARD or ps == PaintSurface.OTHER]
        paintChoiceCeiling_str = st.selectbox("Paint Type for Ceiling", options=paint_options_ceiling,
                                              index=0, format_func=format_paint_surface_option)
    with pcol3:
        paint_options_woodwork = [ps.value for ps in PaintSurface if "WOODWORK" in ps.name or "FRAME" in ps.name or ps == PaintSurface.OTHER]
        paintChoiceWoodwork_str = st.selectbox("Paint Type for Woodwork", options=paint_options_woodwork,
                                               index=0, format_func=format_paint_surface_option)

    st.markdown("---")
    st.subheader("Preparation & Wallpaper")
    prep_col1, prep_col2 = st.columns(2)
    with prep_col1:
        heavyPrep = st.checkbox("Heavy Preparation Required for room (walls/ceilings)?", help="Check if surfaces need significant filling, sanding, or stain blocking.")
    with prep_col2:
        removeWallpaperArea = st.number_input("Wallpaper Area to Remove (sqm)", min_value=0.0, value=0.0, step=0.5, help="Area of wallpaper to be stripped.")

    st.markdown("---") # Visual separator before the button
    submit_button = st.form_submit_button(label='➕ Add Room to Quote')

if submit_button:
    new_room = RoomInput(
        name=name,
        wallArea=wallArea,
        ceilingArea=ceilingArea,
        woodworkLength=woodworkLength,
        doorCount=doorCount,
        windowCount=windowCount,
        coatsWalls=coatsWalls,
        coatsCeiling=coatsCeiling,
        coatsWoodwork=coatsWoodwork,
        coatsDoors=coatsDoors,
        coatsWindows=coatsWindows,
        paintChoiceWalls=PaintSurface(paintChoiceWalls_str),
        paintChoiceCeiling=PaintSurface(paintChoiceCeiling_str),
        paintChoiceWoodwork=PaintSurface(paintChoiceWoodwork_str),
        heavyPrep=heavyPrep,
        wallpaperArea=0.0,
        removeWallpaperArea=removeWallpaperArea,
        notes=notes
    )
    st.session_state.rooms.append(new_room)
    st.success(f"Room '{new_room.name}' added to quote!")

st.markdown("---") # Separator after the form section

# Display Added Rooms & Management
st.header("2. Rooms in Current Quote")
if st.session_state.rooms:
    if st.button("🧹 Clear All Rooms", help="Remove all rooms from the current quote."):
        st.session_state.rooms = []
        st.experimental_rerun() # Rerun to update the list and quote immediately

    for i, room_item in enumerate(st.session_state.rooms):
        with st.expander(f"{i+1}. {room_item.name} (ID: {room_item.id[:8]})"):
            details_cols = st.columns(2)
            with details_cols[0]:
                st.write(f"**Walls**: {room_item.wallArea} sqm, {room_item.coatsWalls} coats ({format_paint_surface_option(room_item.paintChoiceWalls.value)})")
                st.write(f"**Ceiling**: {room_item.ceilingArea} sqm, {room_item.coatsCeiling} coats ({format_paint_surface_option(room_item.paintChoiceCeiling.value)})")
                st.write(f"**Woodwork**: {room_item.woodworkLength}m, {room_item.coatsWoodwork} coats ({format_paint_surface_option(room_item.paintChoiceWoodwork.value)})")
            with details_cols[1]:
                st.write(f"**Doors**: {room_item.doorCount}, {room_item.coatsDoors} coats")
                st.write(f"**Windows**: {room_item.windowCount}, {room_item.coatsWindows} coats")
                st.write(f"**Heavy Prep**: {'Yes' if room_item.heavyPrep else 'No'}")
                if room_item.removeWallpaperArea > 0:
                    st.write(f"**Wallpaper Removal**: {room_item.removeWallpaperArea} sqm")

            if room_item.notes:
                st.markdown("**Notes:**")
                st.info(room_item.notes)

            if st.button(f"❌ Remove Room: {room_item.name}", key=f"remove_room_{room_item.id}", help="Remove this specific room from the quote."):
                st.session_state.rooms.pop(i)
                st.experimental_rerun()
else:
    st.info("No rooms added yet. Add rooms using the form above.")

st.markdown("---") # Separator before the quote summary

# Quote Estimate & Summary Section
st.header("3. Quote Estimate & Summary")

if not st.session_state.rooms:
    st.info("Add rooms to the quote to see the estimate and summary.")
else:
    if st.session_state.current_preset:
        job_quote_details = quote_job(st.session_state.rooms, st.session_state.current_preset)

        st.subheader("A. Room by Room Breakdown")
        if job_quote_details.get("roomBreakdowns"):
            for room_quote in job_quote_details["roomBreakdowns"]:
                with st.expander(f"Room: {room_quote['roomName']} - Total: £{room_quote['totalCost']:.2f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Materials Cost", value=f"£{room_quote['materialsCost']:.2f}")
                    with col2:
                        st.metric(label="Labour Cost", value=f"£{room_quote['labourCost']:.2f}")
                    # st.markdown(f"**Sub-Total for {room_quote['roomName']}: £{room_quote['totalCost']:.2f}**") # Already in expander title
        st.markdown("---")

        st.subheader("B. Overall Job Summary")

        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("Total Materials Cost", f"£{job_quote_details['totalMaterialsCost']:.2f}", help="Includes material contingency.")
            st.metric("Total Labour Cost", f"£{job_quote_details['totalLabourCost']:.2f}", help="Includes labour contingency.")

        with summary_col2:
            if job_quote_details.get('totalAddOnsCost', 0) > 0: # Only show if there are add-ons
                 st.metric("Add-Ons Total", f"£{job_quote_details['totalAddOnsCost']:.2f}")
            st.markdown(f"**Sub-Total (Before Markup): £{job_quote_details['subTotalBeforeMarkup']:.2f}**")
            st.markdown(f"Markup ({st.session_state.current_preset.markupPercent}%): £{job_quote_details['markupAmount']:.2f}")

        with summary_col3:
            st.markdown(f"**Total Before VAT: £{job_quote_details['totalBeforeVAT']:.2f}**")
            if st.session_state.current_preset.vatApplicable:
                st.markdown(f"VAT (20%): £{job_quote_details['vatAmount']:.2f}")
            st.markdown(f"### Grand Total: £{job_quote_details['grandTotal']:.2f}")

    else:
        st.error("Critical Error: No preset configuration loaded. Cannot calculate quote.")

st.markdown("---")
st.caption("End of Quote Builder Prototype.")
# st.markdown("Next steps: Implement preset editing UI.") # Commenting out as this is the last planned step for now.
