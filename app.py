
import streamlit as st
import pandas as pd

# --- Simple constants for demo (ft³ CH4 per cow per day) ---
# Bakersfield value is based on EPA digester data you extracted.
# Pullman & Lynden are scaled down to represent colder / milder climates.
LOCATION_FACTORS = {
    "Pullman": {"climate": "Cold", "ft3_per_cow": 25},       # colder NW
    "Lynden": {"climate": "Mild", "ft3_per_cow": 30},        # coastal WA
    "Bakersfield": {"climate": "Warm", "ft3_per_cow": 37},   # CA EPA data
}

# Climate multipliers for the line chart (relative to "Mild")
CLIMATE_MULTIPLIER = {
    "Cold": 0.7,
    "Mild": 1.0,
    "Warm": 1.3,
}

# Rough conversion factors (demo only)
ELECTRICITY_PER_FT3 = 0.1      # kWh per ft³ CH4 (very approximate)
CO2EQ_PER_FT3_KG = 0.52        # kg CO2-eq per ft³ CH4 (approx)
CAR_CO2_PER_YEAR_KG = 4600     # one passenger car per year (EPA-style)

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

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="GHG Lagoon Mini-Demo", layout="wide")

st.title("GHG Lagoon Mini-Demo")
st.write(
    "Play with herd size and location to see how a covered lagoon could "
    "change methane emissions. This is a simplified preview of my full "
    "kinetic + LSTM + Spiking Neural Network model."
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
    location = st.selectbox("Location", list(LOCATION_FACTORS.keys()), index=list(LOCATION_FACTORS.keys()).index(default_location))
    mode = st.selectbox("Prediction mode", ["day", "month", "year"])

    run_button = st.button("Predict methane")

with right_col:
    if run_button:
        methane_ft3 = predict_methane_ft3(cows, location, mode)

        # Big headline numbers
        st.subheader("Predicted methane emission")
        st.metric(
            label=f"Methane emission ({mode})",
            value=f"{methane_ft3:,.0f} ft³"
        )

        # Model accuracy (from your validation plot)
        st.metric(
            label="Model accuracy (validation)",
            value="≈93%",
            delta="R² ≈ 0.95, MAPE ≈ 6.8%"
        )

        # Electricity and cars equivalent
        kwh = methane_ft3 * ELECTRICITY_PER_FT3
        co2eq_kg = methane_ft3 * CO2EQ_PER_FT3_KG

        if mode == "year":
            car_equiv = co2eq_kg / CAR_CO2_PER_YEAR_KG
        else:
            # Convert to annual car equivalents just for intuition
            car_equiv = (co2eq_kg * (365 if mode == "day" else 12)) / CAR_CO2_PER_YEAR_KG

        st.write(
            f"**Energy equivalent:** ~{kwh:,.0f} kWh "
            f" &nbsp; | &nbsp; **Climate impact:** ~{car_equiv:,.1f} car-equivalents"
        )

        # Climate scenario line chart
        st.markdown("#### How would climate change methane?")
        scenario_values = climate_scenarios(cows, location, mode)
        df = pd.DataFrame(
            {"Methane (ft³)": scenario_values}
        )
        st.line_chart(df)

        st.caption(
            "Demo model only. The full system uses experimental data, lagoon "
            "kinetics (first-order + Arrhenius), and a hybrid LSTM + Spiking "
            "Neural Network to refine these predictions."
        )
    else:
        st.info("Choose a preset or adjust the sliders, then click **Predict methane**.")
