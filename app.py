
import streamlit as st
import pandas as pd

def get_csi_percentages(csi_score):
    if csi_score >= 901:
        return 0.74, 0.35
    elif 801 <= csi_score <= 900:
        return 0.51, 0.24
    elif 701 <= csi_score <= 800:
        return 0.32, 0.19
    else:
        return 0.14, 0.16

def simulate_profitability(csi_score, initial_customers, service_profit_per_year,
                           ownership_years, warranty_years, vehicle_sale_profit,
                           start_year=2026, end_year=2040):
    years = list(range(start_year, end_year + 1))
    service_customers = {year: 0 for year in years}
    repeat_customers = {year: 0 for year in years}
    total_profit = {year: 0 for year in years}

    customer_waves = [{"year": 2025, "count": initial_customers}]
    service_return_pct, repeat_purchase_pct = get_csi_percentages(csi_score)

    for year in years:
        new_waves = []
        for wave in customer_waves:
            age = year - wave["year"]
            if 1 <= age <= warranty_years:
                service = wave["count"] * service_return_pct
                if service >= 0.5:
                    service_customers[year] += service
            if age == ownership_years:
                repeats = wave["count"] * repeat_purchase_pct
                if repeats >= 0.5:
                    repeat_customers[year] += repeats
                    new_waves.append({"year": year, "count": repeats})
        customer_waves.extend(new_waves)
        total_profit[year] = (
            round(service_customers[year]) * service_profit_per_year +
            round(repeat_customers[year]) * vehicle_sale_profit
        )

    df = pd.DataFrame({
        "Year": years,
        "Service Customers": [round(service_customers[y]) for y in years],
        "Repeat Purchases": [round(repeat_customers[y]) for y in years],
        "Total Profit": [round(total_profit[y]) for y in years]
    })

    totals = {
        "Year": "Total",
        "Service Customers": df["Service Customers"].sum(),
        "Repeat Purchases": df["Repeat Purchases"].sum(),
        "Total Profit": df["Total Profit"].sum()
    }
    df = pd.concat([pd.DataFrame([totals]), df], ignore_index=True)

    df["Service Customers"] = df["Service Customers"].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
    df["Repeat Purchases"] = df["Repeat Purchases"].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)
    df["Total Profit"] = df["Total Profit"].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)

    return df

st.title("CSI Profitability Simulator")

csi_score = st.slider("CSI Score (0 to 1000)", 0, 1000, 870)
initial_customers = st.number_input("Sample Size (Volvo Selekt Sales)", min_value=1, value=100)
service_profit = st.number_input("Service Profit per Year per Customer", min_value=0, value=350)
ownership_duration = st.number_input("Ownership Duration (Years)", min_value=1, value=2)
warranty_duration = st.number_input("Volvo Selekt Warranty (Years)", min_value=1, value=3)
vehicle_profit = st.number_input("Vehicle Sale Profit", min_value=0, value=1225)

if st.button("Run Simulation"):
    results = simulate_profitability(
        csi_score,
        initial_customers,
        service_profit,
        ownership_duration,
        warranty_duration,
        vehicle_profit
    )
    st.subheader("Results")
    st.dataframe(results)
    csv = results.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "csi_profitability_results.csv", "text/csv")
