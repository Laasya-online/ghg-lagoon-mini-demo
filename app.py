import streamlit as st
import pandas as pd
import altair as alt

# --- Simple constants for demo (ft³ CH4 per cow per day) ---
LOCATION_FACTORS = {
    "Pullman": {"climate": "Cold", "ft3_per_cow": 25},      # colder NW
    "Lynden": {"climate": "Mild", "ft3_per_cow": 30},       # coastal WA
    "Bakersfield": {"climate": "Warm", "ft3_per_cow": 37},  # CA EPA-based
}

# Climate multipliers for the climate chart (relative to "Mild")
CLIMATE_MULTIPLIER = {
    "Cold": 0.7,
    "Mild": 1.0,
    "Warm": 1.3,
}

# Rough conversion factors (demo only)
ELECTRICITY_PER_FT3 = 0.1       # kWh per ft³ CH4
CO2EQ_PER_FT3_KG = 0.52         # kg CO2-eq per ft³ CH4
CAR_CO2_PER_YEAR_KG = 4600      # kg CO2-eq per car per year (approx)


def predict_methane_ft3(cows: int, location: str, mode: str) -> float:
    """Very simple demo model: ft³ CH4 per selected time unit."""
    base_ft3_per_cow_day = LOCATION_FACTORS[location]["ft3_per_cow"]
    daily = base_ft3_per_cow_day * cows

    if mode == "day":
        factor = 1
    elif mode == "month":
        factor = 30
    else:  # "year"
        factor = 365

    return daily * factor


def climate_scenarios(cows: int, base_location: str, mode: str):
    """Return methane for the same farm under Cold/Mild/Warm climates."""
    base_ft3_per_cow_day = LOCATION_FACTORS[base_location]["ft3_per_cow"]
    values = {}
    for climate, mult in CLIMATE_MULTIPLIER.items():
        daily = base_ft3_per_cow_day * mult * cows

        if mode == "day":
            factor = 1
        elif mode == "month":
            factor = 30
        else:
            factor = 365

        values[climate] = daily * factor

    return values


# ----------------- Page config + STYLING -----------------
st.set_page_config(page_title="GHG Lagoon Mini-Demo", layout="wide")

# Light nature-style background + dark text so everything is visible
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(135deg, #f2fff6 0%, #f0f8ff 40%, #ffffff 100%);
        background-attachment: fixed;
        background-size: cover;
    }

    /* Make all main text dark and readable */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        color: #123b2f;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, li, span, div {
        color: #123b2f;
    }

    /* Header transparent */
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.0);
    }

    /* Optional: softer sidebar background if you use sidebar later */
    [data-testid="stSidebar"] {
        background-color: #f6fff9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- UI -----------------
st.title("GHG Lagoon Mini-Demo")
st.write(
    "Play with herd size and location to see how a covered lagoon could change methane emissions. "
    "This is a simplified preview of the full kinetic + LSTM + Spiking Neural Network methane model."
)

# Preset buttons
preset = st.radio(
    "Quick presets:",
    ["Custom", "Small WA Dairy (Pullman)", "Medium WA Dairy (Lynden)", "Large CA Dairy (Bakersfield)"],
    horizontal=True,
)

if preset == "Small WA Dairy (Pullman)":
    default_cows = 500
    default_location = "Pullman"
elif preset == "Medium WA Dairy (Lynden)":
    default_cows = 2000
    default_location = "Lynden"
elif preset == "Large CA Dairy (Bakersfield)":
    default_cows = 15500
    default_location = "Bakersfield"
else:
    default_cows = 1000
    default_location = "Lynden"

# Layout: inputs on the left, outputs on the right
left_col, right_col = st.columns([1, 2])

with left_col:
    cows = st.slider("Number of cows", min_value=100, max_value=20000, value=default_cows, step=100)

    location_list = list(LOCATION_FACTORS.keys())
    location_index = location_list.index(default_location)
    location = st.selectbox("Location", location_list, index=location_index)

    mode = st.selectbox("Prediction mode", ["day", "month", "year"])

    run_button = st.button("Predict methane")

with right_col:
    if run_button:
        methane_ft3 = predict_methane_ft3(cows, location, mode)

        # -------- TOP: CARDS WITH MAIN METRICS --------
        st.subheader("Predicted methane emission")

        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                label=f"Methane emission ({mode})",
                value=f"{methane_ft3:,.0f} ft³",
            )
        with m2:
            st.metric(
                label="Model accuracy (full version)",
                value="≈93%",
                delta="R² ≈ 0.95, MAPE ≈ 6.8%",
            )

        # -------- CONVERSION: kWh & cars --------
        kwh = methane_ft3 * ELECTRICITY_PER_FT3
        co2eq_kg = methane_ft3 * CO2EQ_PER_FT3_KG

        if mode == "year":
            car_equiv = co2eq_kg / CAR_CO2_PER_YEAR_KG
        elif mode == "month":
            car_equiv = (co2eq_kg * 12) / CAR_CO2_PER_YEAR_KG  # annualised intuiti*
