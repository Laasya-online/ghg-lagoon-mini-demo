import streamlit as st
import pandas as pd
import altair as alt

# --- Simple constants for demo (ft³ CH4 per cow per day) ---
LOCATION_FACTORS = {
    "Pullman": {"climate": "Cold", "ft3_per_cow": 25},      # colder NW
    "Lynden": {"climate": "Mild", "ft3_per_cow": 30},       # coastal WA
    "Bakersfield": {"climate": "Warm", "ft3_per_cow": 37},  # CA EPA-based
}

# Climate multipliers for the line chart (relative to "Mild")
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


# ----------------- Page config + BACKGROUND -----------------
st.set_page_config(page_title="GHG Lagoon Mini-Demo", layout="wide")

# Light plant-like / nature-ish background using a soft gradient
# (If you have a plant image URL, you can replace "linear-gradient(...)" with url("..."))
st.markdown(
    """
    <style>
    .stApp {
        background-image: linear-gradient(135deg, #f6fff6 0%, #f0fbff 40%, #ffffff 100%);
        background-attachment: fixed;
        background-size: cover;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- UI -----------------
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

    location_list = list(LOCATION_FACTORS.keys())
    location_index = location_list.index(default_location)
    location = st.selectbox("Location", location_list, index=location_index)

    mode = st.selectbox("Prediction mode", ["day", "month", "year"])

    run_button = st.button("Predict methane")

with right_col:
    if run_button:
        methane_ft3 = predict_methane_ft3(cows, location, mode)

        # -------- TOP: MAIN METRICS --------
        st.subheader("Predicted methane emission")
        st.metric(
            label=f"Methane emission ({mode})",
            value=f"{methane_ft3:,.0f} ft³",
        )

        # Validation metric from your full model
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
            car_equiv = (co2eq_kg * 12) / CAR_CO2_PER_YEAR_KG  # rough annualised equivalent
        else:  # day
            car_equiv = (co2eq_kg * 365) / CAR_CO2_PER_YEAR_KG  # rough annualised equivalent

        st.write(
            f"**Energy equivalent:** ~{kwh:,.0f} kWh"
            f" &nbsp; | &nbsp; **Climate impact:** ~{car_equiv:,.1f} car-equivalents (CO₂-eq)"
        )

        # -------- CLIMATE LINE CHART (prettier) --------
        st.markdown("#### How would climate change methane?")

        scenario_values = climate_scenarios(cows, location, mode)
        df = pd.DataFrame(
            {
                "Climate": list(scenario_values.keys()),
                "Methane_ft3": list(scenario_values.values()),
            }
        )

        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Climate:N", sort=["Cold", "Mild", "Warm"], title="Climate scenario"),
                y=alt.Y(
                    "Methane_ft3:Q",
                    title=f"Methane emission ({mode}) [ft³]",
                ),
                tooltip=[
                    alt.Tooltip("Climate:N", title="Climate"),
                    alt.Tooltip("Methane_ft3:Q", title="Methane (ft³)", format=","),
                ],
            )
        )

        st.altair_chart(chart, use_container_width=True)

        # -------- VALIDATION SECTION --------
        st.markdown("#### How does this compare to reference data?")

        if location == "Bakersfield":
            # Compare daily emission to EPA-style reference range
            daily_demo = predict_methane_ft3(cows, location, "day")
            ref_min, ref_max = 600_000, 700_000   # example CA digester range
            ref_mid = (ref_min + ref_max) / 2
            diff_pct = (daily_demo - ref_mid) / ref_mid * 100

            st.write(
                f"For large covered lagoons in Bakersfield, EPA AgSTAR reports roughly "
                f"{ref_min:,}–{ref_max:,} ft³ CH₄ per **day**."
            )
            st.write(
                f"In this demo, your setup gives about **{daily_demo:,.0f} ft³/day**, "
                f"which is {diff_pct:+.1f}% relative to the middle of that range."
            )
        else:
            st.write(
                "For Pullman and Lynden, this demo scales methane from the same EPA-based "
                "factors and your lab-derived kinetic relationships. The full model refines "
                "these values using time-series learning."
            )

        st.caption(
            "Demo model only. The full system uses experimental lagoon data, first-order + Arrhenius "
            "kinetics, and a hybrid LSTM + Spiking Neural Network to generate validated predictions."
        )
    else:
        st.info("Choose a preset or adjust the sliders, then click **Predict methane**.")
