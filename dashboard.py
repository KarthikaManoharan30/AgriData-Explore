import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="ICRISAT Full Dashboard", layout="wide")
st.title("🌾 ICRISAT Agricultural Dashboard 🌱")

# 👇 Add logo below the title
st.image("evolution-of-agri-banner.jpg", caption="Agriculture", use_container_width=True)  



# ------------------------
# DATABASE CONNECTION
# ------------------------
@st.cache_resource
def get_engine():
    user = "postgres"
    password = "Regular30"
    host = "localhost"
    port = "5432"
    db = "agriculture_data"
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

engine = get_engine()

# ------------------------
# MODE SELECTOR
# ------------------------
mode = st.sidebar.radio("Choose Mode", ["📁 CSV Explorer", "📊 SQL Explorer"])

# ============================================================================================
# SECTION 1: CSV EXPLORER (LOCAL FILE ANALYSIS)
# ============================================================================================
if mode == "📁 CSV Explorer":
    st.header("📁 CSV Visual & EDA Explorer")

    # Load and clean CSV
    @st.cache_data
    def load_clean_data():
        df = pd.read_csv(r'D:\Projects\Agriproj\ICRISAT-District Level Data - ICRISAT-District Level Data.csv')

        df.replace(-1, np.nan, inplace=True)
        df = df.fillna(df.mean(numeric_only=True))
        df.columns = (
            df.columns.str.strip().str.lower()
            .str.replace(' ', '_')
            .str.replace(r'\(.*?\)', '', regex=True)
            .str.replace(r'1000_ha|1000_tons|kg_per_ha', '', regex=True)
            .str.replace(r'[^a-z0-9_]', '', regex=True)
            .str.replace(r'__+', '_', regex=True)
            .str.strip('_')
        )
        df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
        return df

    df = load_clean_data()

    st.subheader("🔍 Preview Cleaned Data")
    st.dataframe(df)

    st.subheader("📈 Histogram by Crop")
    crop = st.selectbox("Select Crop", ['rice', 'wheat', 'maize', 'oilseeds', 'sugarcane', 'cotton'])

    def plot_crop_histograms(crop):
        fig, axs = plt.subplots(1, 3, figsize=(18, 4))
        for i, metric in enumerate(['production', 'yield', 'area']):
            column = f"{crop}_{metric}"
            if column in df.columns:
                axs[i].hist(df[column].dropna(), bins=50, color=['lightgreen', 'lightblue', 'orange'][i], edgecolor='black')
                axs[i].set_title(f"{crop.capitalize()} {metric.capitalize()} Distribution")
                axs[i].set_xlabel(metric.capitalize())
                axs[i].set_ylabel("Frequency")
        st.pyplot(fig)

    plot_crop_histograms(crop)

    st.subheader("🔗 Correlation Heatmap")
    with st.expander("🌡️ Crop Correlation Heatmap"):
        crop_cols = [
            'rice_production', 'wheat_production', 'maize_production', 'chickpea_production' ,
            'groundnut_production', 'pulses_production', 'barley_production',
            'oilseeds_production', 'sugarcane_production', 'millets_production',
            'cotton_production', 'sunflower_production', 'safflower_production', 'soybean_production', 'sorghum_production'
        ]
        available_cols = [col for col in crop_cols if col in df.columns]
        corr_data = df[available_cols].corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_data, annot=True, cmap='YlGnBu', fmt=".2f", linewidths=0.5, ax=ax)
        st.pyplot(fig)




# ============================================================================================
# SECTION 2: SQL QUERY EXPLORER
# ============================================================================================
elif mode == "📊 SQL Explorer":
    st.header("📊 SQL Query Explorer")

    queries = {
        "1. Year-wise Rice Production (Top 3 States)": """
            with top_states as (
                select state_name
                from agriculture_data
                group by state_name 
                order by sum(rice_production) desc
                limit 3
            )
            select year, state_name, sum(rice_production) as total_rice_production
            from agriculture_data
            where state_name in (select state_name from top_states)
            group by year, state_name
            order by year, total_rice_production desc
        """,

        "2. Top 5 Districts by Wheat Yield Increase": """
            with last_five_years as (
                select distinct year from agriculture_data order by year desc limit 5
            ),
            year_range as (
                select max(year) as latest_year, min(year) as earliest_year from last_five_years
            ),
            district_yields as (
                select dist_name, year, avg(wheat_yield) as avg_yield
                from agriculture_data
                where year in (select latest_year from year_range) or year in (select earliest_year from year_range)
                group by dist_name, year
            ),
            yield_comparison as (
                select dist_name,
                max(case when year = (select latest_year from year_range) then avg_yield end) as yield_now,
                max(case when year = (select earliest_year from year_range) then avg_yield end) as yield_before
                from district_yields
                group by dist_name
            )
            select dist_name, yield_before, yield_now,
            yield_now - yield_before as yield_increase
            from yield_comparison
            where yield_now is not null and yield_before is not null
            order by yield_increase desc
            limit 5
        """,

        "3. Oilseed Production Growth (5 Years)": """
            with recent_years as (
                select distinct year from agriculture_data order by year desc limit 5
            ),
            oilseed_summary as (
                select state_name, year, sum(oilseeds_production) as total_production
                from agriculture_data
                where year in (select year from recent_years)
                group by state_name, year
            ),
            pivoted as (
                select state_name,
                max(case when year = (select min(year) from recent_years) then total_production end) as production_start,
                max(case when year = (select max(year) from recent_years) then total_production end) as production_end
                from oilseed_summary
                group by state_name
            )
            select state_name, production_start, production_end,
            round((((production_end - production_start) / production_start) * 100)::numeric, 2) as growth_rate_percent
            from pivoted
            where production_start is not null and production_end is not null and production_start <> 0
            order by growth_rate_percent desc
            limit 5
        """,

        "4. Rice Area vs Production Correlation (District-wise)": """
            select
                dist_name, state_name,
                (
                    (count(*) * sum(rice_production * rice_area) - sum(rice_production) * sum(rice_area)) /
                    (sqrt(count(*) * sum(rice_production * rice_production) - power(sum(rice_production), 2)) *
                     sqrt(count(*) * sum(rice_area * rice_area) - power(sum(rice_area), 2)))
                ) as rice_corr
            from agriculture_data
            where rice_production is not null and rice_area is not null
            group by dist_name, state_name
            having
                sqrt(count(*) * sum(rice_production * rice_production) - power(sum(rice_production), 2)) <> 0 and
                sqrt(count(*) * sum(rice_area * rice_area) - power(sum(rice_area), 2)) <> 0
        """,

        "5. Cotton Production Trend (Top 5 States)": """
            with total_cotton as (
                select state_name, sum(cotton_production) as total
                from agriculture_data
                group by state_name
                order by total desc
                limit 5
            ),
            cotton_trend as (
                select year, state_name, sum(cotton_production) as yearly_production
                from agriculture_data
                where state_name in (select state_name from total_cotton)
                group by year, state_name
            )
            select * from cotton_trend order by year, state_name
        """,

        "6. Top Groundnut Districts (2017)": """
            SELECT dist_name, state_name, groundnut_production
            FROM agriculture_data
            WHERE year = 2017
            ORDER BY groundnut_production DESC
            LIMIT 7
        """,

        "7. Annual Maize Yield": """
            select year, round(avg(maize_yield)::numeric, 2) as avg_maize_yield
            from agriculture_data
            group by year
            order by year
        """,

        "8. Oilseeds Area by State": """
            select state_name, round(sum(oilseeds_area)::numeric,2) as total_oilseeds_area
            from agriculture_data
            group by state_name
            order by total_oilseeds_area desc
        """,

        "9. Highest Rice Yield (Districts)": """
            select dist_name, state_name, max(rice_yield) as max_rice_yield
            from agriculture_data
            group by dist_name, state_name
            order by max_rice_yield desc
            limit 5
        """,

        "10. Wheat vs Rice Production (Top 5 States)": """
            with top_states as (
                select state_name, sum(wheat_production + rice_production) as total_production
                from agriculture_data
                group by state_name
                order by total_production desc
                limit 5
            )
            select year, state_name,
            round(sum(wheat_production)::numeric, 2) as total_wheat,
            round(sum(rice_production)::numeric, 2) as total_rice
            from agriculture_data
            where state_name in (select state_name from top_states)
            group by year, state_name
            order by year, state_name
        """
    }

    selected_query = st.selectbox("📌 Select a SQL Query", list(queries.keys()))

    query = queries[selected_query]
    try:
        df_sql = pd.read_sql(query, engine)
        st.dataframe(df_sql)

        # Auto visualizations
        if "year" in df_sql.columns:
            line_cols = [col for col in df_sql.columns if col not in ['year', 'state_name']]
            if "state_name" in df_sql.columns and line_cols:
                for col in line_cols:
                    fig = px.line(df_sql, x="year", y=col, color="state_name", title=f"{col} over Years")
                    st.plotly_chart(fig, use_container_width=True)
            elif line_cols:
                fig = px.line(df_sql, x="year", y=line_cols[0], title=f"{line_cols[0]} over Years")
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error running query: {e}")
