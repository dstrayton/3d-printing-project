import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Additive Manufacturing Performance Dashboard",
    page_icon="🖨️",
    layout="wide",
)

# --- LOAD AND CLEAN DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("3D Printing Data.csv")
    df = df[~df["Printer Type"].str.contains("open", case=False, na=False)]
    df = df[~df["Material"].str.contains("rPET", case=False, na=False)]
    df = df[~df["Material"].str.contains("PLA-transparent", case=False, na=False)]
    df = df.drop(columns=["Width (mm)", "Thickness (mm)", "Printer Type"], errors="ignore")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load '3D Printing Data.csv'. Please ensure the file is in the working directory. Error: {e}")
    st.stop()

# --- MAIN PAGE HEADER ---
st.title("🖨️ Additive Manufacturing Performance Dashboard")
st.markdown("""
This interactive dashboard explores how **material types**, **infill density**, and **print speed**
impact the mechanical strength and surface quality of FDM 3D-printed parts. Designed for 3D printing
professionals and hobbyists, it answers the questions:
* **Which materials produce the best surface finish and which are the strongest?**
* **Does higher infill consistently improve strength?**
* **How does print speed affect part performance?**

These questions are answered using data collected from the following source: [Mendeley Data](https://data.mendeley.com/datasets/zd6td6svd6/2). Data was collected on 8 different 3D printer materials (PLA+, PLA, PLA phosphor, PLA-CF, PETG, PP, TPU, ABS), 3 different infill densities (20%, 50%, 80%), and 3 different print speeds (30 mm/s, 50 mm/s, 70 mm/s). Evidence answering the above questions is displayed using the following quantitative analysis.
""")

st.markdown("---")

# --- QUANTITATIVE PERFORMANCE ANALYSIS SECTION ---
st.header("📊 Quantitative Performance Analysis")

st.markdown("### Dataset Filters")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    all_materials = sorted(df["Material"].unique().tolist())
    selected_materials = st.multiselect("Select Materials:", options=all_materials, default=all_materials)

with col_f2:
    all_infill = sorted(df["Infill Density (%)"].unique().tolist())
    selected_infill = st.multiselect("Select Infill Density (%):", options=all_infill, default=all_infill)

with col_f3:
    all_speed = sorted(df["Speed (mm/s)"].unique().tolist())
    selected_speed = st.multiselect("Select Print Speed (mm/s):", options=all_speed, default=all_speed)

filtered_df = df[
    df["Material"].isin(selected_materials) &
    df["Infill Density (%)"].isin(selected_infill) &
    df["Speed (mm/s)"].isin(selected_speed)
]

st.markdown("---")

if filtered_df.empty:
    st.warning("⚠️ **No data matches your current filter combination.** Please broaden your selections above to view visualizations and metrics.")
else:
    tab1, tab2, tab3 = st.tabs(["Material Strength and Finish", "Infill Density Impact", "Print Speed Effects"])

    with tab1:
        st.subheader("Which Materials Produce the Best Surface Finish and Which are the Strongest?")
        st.markdown("*Note: Visualizations below update with filters, reflecting the active subset.*")
        material_group = filtered_df.groupby("Material")[["Roughness AVG", "Peak Load (N)"]].mean().reset_index()

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            fig_rough = px.bar(material_group, x="Material", y="Roughness AVG", title="Mean Surface Roughness (Lower is Smoother)", color="Material", height=420)
            fig_rough.update_traces(width=0.6)
            fig_rough.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_rough, use_container_width=True)

        with col_v2:
            fig_load = px.bar(material_group, x="Material", y="Peak Load (N)", title="Mean Peak Load (Higher is Stronger)", color="Material", height=420)
            fig_load.update_traces(width=0.6)
            fig_load.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_load, use_container_width=True)

        st.info("**Key Conclusion:** TPU achieves the smoothest surface finish (lowest roughness average), while PETG demonstrates the highest mechanical strength under peak load conditions.")

    with tab2:
        st.subheader("Does Increasing Infill Density Improve Strength?")
        infill_group = filtered_df.groupby("Infill Density (%)")[["Peak Load (N)", "Peak Stress (kPa)"]].mean().reset_index()

        col_i1, col_i2 = st.columns(2)
        with col_i1:
            fig_infill_load = px.line(infill_group, x="Infill Density (%)", y="Peak Load (N)", markers=True, title="Peak Load vs. Infill Density (%)", height=420)
            st.plotly_chart(fig_infill_load, use_container_width=True)

        with col_i2:
            fig_infill_stress = px.line(infill_group, x="Infill Density (%)", y="Peak Stress (kPa)", markers=True, title="Peak Stress vs. Infill Density (%)", height=420)
            st.plotly_chart(fig_infill_stress, use_container_width=True)

        st.info("**Key Conclusion:** There is a clear upward trend in both peak load and peak stress as infill density increases from 20% to 80%, confirming that higher infill yields stronger parts.")

    with tab3:
        st.subheader("How Does Print Speed Affect Part Performance?")
        speed_group = filtered_df.groupby("Speed (mm/s)")[["Roughness AVG", "Peak Load (N)", "Peak Stress (kPa)"]].mean().reset_index()

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            fig_spd_rough = px.line(speed_group, x="Speed (mm/s)", y="Roughness AVG", markers=True, title="Surface Roughness vs. Speed", height=400)
            st.plotly_chart(fig_spd_rough, use_container_width=True)
        with col_s2:
            fig_spd_load = px.line(speed_group, x="Speed (mm/s)", y="Peak Load (N)", markers=True, title="Peak Load vs. Speed", height=400)
            st.plotly_chart(fig_spd_load, use_container_width=True)
        with col_s3:
            fig_spd_stress = px.line(speed_group, x="Speed (mm/s)", y="Peak Stress (kPa)", markers=True, title="Peak Stress vs. Speed", height=400)
            st.plotly_chart(fig_spd_stress, use_container_width=True)

        st.info("**Key Conclusion:** Higher print speeds degrade surface finish (increasing roughness), but surprisingly correlate with slight improvements in peak load and peak stress.")

    st.markdown("---")
    st.header("📝 Qualitative Material Analysis")
st.markdown("To complement the performance data, a qualitative analysis was performed. This involved analyzing the material description data from Xometry, a significant company in the additive manufacturing space, for the 8 corresponding materials. On this site, they provide descriptions and material properties for a large number of materials that they have tested over the years. This analysis reveals that manufacturers heavily market two primary attributes: Strength and Flexibility.")

col_q1, col_q2 = st.columns([1, 1])

with col_q1:
    st.markdown("""
    ### **Summary of Core Qualitative Themes**
    * **Dominance of Strength:** Strength is cited as a primary advantage 8 times in the descriptions of the 8 materials of interest
    * **Flexibility Frequency:** Flexibility is cited as a primary advantage 5 times in the descriptions of the 8 materials of interest.
    * **Specialized Purpose:** Each material is engineered for unique purposes that go beyond strength, finish, and flexibility.

    Overall takeaway: Materials are designed and marketed to be best for a number of specific scenarios. For example, PP is engineered to excel at chemical resistance, fatigue resistance, and extremely low water absorption rather than mechanical strength and durface finish. It is important to examine the material descriptions before picking the best for your project. However, many of these materials share the same advantages according to their descriptions. This is most notable for strength and flexibility. As seen in the above data, there is a clear discrepancy in strength bewteen the desired materials. This shows that it is necessary to reference performance data to find the true best materials.
    """)

with col_q2:
    kw_df = pd.DataFrame({
        "Property": ["Strength", "Flexibility"],
        "Mentions": [8, 5]
    })
    # Fixed chart bounds and configuration to prevent wide stretching
    fig_kw = px.bar(
        kw_df,
        x="Mentions",
        y="Property",
        orientation='h',
        text="Mentions",
        title="Keyword Frequency in Descriptions",
        color="Property",
        height=300
    )
    fig_kw.update_layout(
        showlegend=False,
        xaxis_title="Total Mentions",
        yaxis_title="",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig_kw.update_xaxes(range=[0, 10])
    st.plotly_chart(fig_kw, use_container_width=True)
    st.markdown("---")

st.header("🎯 Overall Conclusion")
st.markdown("""
There are many factors that go into the performance of a 3D printed product and choosing the best material and print settings are the first step.

Ultimately, achieving the best results requires a careful understanding of the specific performance qualities you are looking for. Different materials and parameters serve distinct goals. A material like PETG excels when maximum mechanical strength is required, while TPU is ideal if your priority is surface finish and flexibility. For process settings, increasing infill density reliably boosts strength, though it comes at the cost of additional material and print time. Additionally, print speed involves its own trade-offs. Slower speeds yield a cleaner surface finish, whereas faster speeds can improve overall strength performance. Balancing these factors is key to optimizing any 3D print and it is important to understand that in advance. Companies will use words like "strong" and "flexible" to describe multiple materials, but you can only understand which material is best for you by comparing the performance data for each with your goals.
""")

st.markdown("---")
st.header("🎯 Practical Meaning & Limitations")
col_l1, col_l2 = st.columns(2)

with col_l1:
    st.subheader("💡 Practical Meaning for Users")
    st.markdown("""
    * **Material Selection Matters:** For high load-bearing, consider materials like PETG and PLA+. For parts with the smoothest surface finish, consider TPU.
    * **Balancing Speed, Strength, and Quality:** Stick to lower speeds (30 mm/s) for better surface aesthetics. Go to higher speeds for better mechanical strength.
    * **Infill Optimization:** Increasing infill density reliably boosts mechanical strength but will require more material and time.
    """)

with col_l2:
    st.subheader("⚠️ Limitations")
    st.markdown("""
    * **Sampling Imbalance:** Not all materials were sampled at the same rate in this data. For example, significantly more samples exist for **PLA+** (213 rows) than standard PLA or PP (9 rows).
    * **Inherent Material Trade-offs:** All materials are designed to have different advantages. This study was specific to strength and surface finish. The materials that performed poorly in this analysis may be an optimal choice for other constraints such as chemical resistance and flexibility.
    * **Scope Constraints:** There are many more materials for 3D printing and some may have even better results for the desired metrics. This study was specific to the 8 tested in the original data source.
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Interactive Dashboard built with Streamlit & Plotly | Data Source: Mendeley FDM 3D Printing Dataset</p>", unsafe_allow_html=True)
