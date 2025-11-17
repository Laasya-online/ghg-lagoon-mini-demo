# GHG Lagoon Mini-Demo

This is a small interactive demo of my **GHG mitigation model** for covered dairy manure lagoons.  
It lets users explore how **herd size** and **location** affect methane emissions and shows a preview of what the full application can do.

> ⚠️ This is a **simplified prototype** for a symposium poster demo.  
> The real system uses lab + field data, first-order + Arrhenius kinetics, and a hybrid LSTM + Spiking Neural Network.

---

## Features

- Adjust **number of cows** (100–20,000)
- Choose **location**: Pullman, Lynden, Bakersfield
- Select **time horizon**: day, month, year
- View:
  - Predicted methane emission (ft³)
  - Approx. energy (kWh) and CO₂-equivalent “car” impact
  - Simple climate scenario chart (Cold / Mild / Warm)

---

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ghg-lagoon-mini-demo.git
cd ghg-lagoon-mini-demo

# 2. Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py
