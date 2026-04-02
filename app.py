import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

st.set_page_config(layout="wide", page_title="Startup Funding Analysis")

# ── Load & clean data ──────────────────────────────────────────────
df = pd.read_csv("Startup_Clean.csv")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Convert to Million USD
df["Amount in USD"] = (df["Amount in USD"] / 1_000_000).round(2)

# ── Sidebar ────────────────────────────────────────────────────────
st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select View", ["Overall Analysis", "Startup", "Investor"])

# ── Helper functions ───────────────────────────────────────────────

def show_overall():
    st.title("Overall Analysis")

    col1, col2, col3 = st.columns(3)
    total = df["Amount in USD"].sum()
    max_funding = df.groupby("Investors Name")["Amount in USD"].max().max()
    avg_funding = df.groupby("Investors Name")["Amount in USD"].sum().mean()

    col1.metric("Total Investment (Million USD)", f"${total:,.1f}M")
    col2.metric("Max Single Funding (Million USD)", f"${max_funding:,.1f}M")
    col3.metric("Avg Funding per Investor (Million USD)", f"${avg_funding:,.1f}M")

    st.header("Year-over-Year Funding")
    yoy_type = st.selectbox("Select Type", ["Total", "Count"])

    if yoy_type == "Total":
        temp = df.groupby("Year")["Amount in USD"].sum().reset_index()
        ylabel = "Total Investment (Million USD)"
    else:
        temp = df.groupby("Year")["Amount in USD"].count().reset_index()
        ylabel = "Number of Deals"

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(temp["Year"].astype(str), temp["Amount in USD"], marker="o")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_title(f"YoY {yoy_type}")
    fig.tight_layout()
    st.pyplot(fig)

    st.header("Top Sectors by Funding")
    sector_data = df.groupby("Vertical")["Amount in USD"].sum().sort_values(ascending=False).head(7)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.barh(sector_data.index[::-1], sector_data.values[::-1])
    ax2.set_xlabel("Total Funding (Million USD)")
    ax2.set_title("Funding by Sector")
    fig2.tight_layout()
    st.pyplot(fig2)


def show_investor(selected):
    st.title(f"Investor: {selected}")

    filtered = df[df["Investors Name"].str.contains(selected, na=False)]

    st.subheader("Recent Investments")
    st.dataframe(
        filtered.head(5)[["Startup Name", "Amount in USD", "Vertical",
                           "InvestmentnType", "City", "SubVertical"]],
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Biggest Investments by Startup")
        biggest = (
            filtered.groupby("Startup Name")["Amount in USD"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        fig, ax = plt.subplots()
        ax.bar(biggest.index, biggest.values)
        ax.set_ylabel("Million USD")
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
        plt.xticks(rotation=25, ha="right")
        fig.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Investment by Sector")
        sector_pie = filtered.groupby("Vertical")["Amount in USD"].sum()
        fig2, ax2 = plt.subplots()
        ax2.pie(sector_pie, labels=sector_pie.index, autopct="%0.1f%%", shadow=True)
        fig2.tight_layout()
        st.pyplot(fig2)

    st.subheader("Year-over-Year Investment")
    yoy = filtered.groupby("Year")["Amount in USD"].sum()
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(yoy.index.astype(str), yoy.values, marker="o")
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Million USD")
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    fig3.tight_layout()
    st.pyplot(fig3)


# ── Main routing ───────────────────────────────────────────────────

if option == "Overall Analysis":
    show_overall()

elif option == "Startup":
    selected_startup = st.sidebar.selectbox(
        "Select Startup", sorted(df["Startup Name"].dropna().unique())
    )
    if st.sidebar.button("Show Details"):
        st.title(f"Startup: {selected_startup}")
        startup_data = df[df["Startup Name"] == selected_startup]
        st.dataframe(startup_data[["Date", "Investors Name", "Amount in USD",
                                    "InvestmentnType", "City"]], use_container_width=True)
        total_raised = startup_data["Amount in USD"].sum()
        st.metric("Total Raised (Million USD)", f"${total_raised:,.1f}M")

elif option == "Investor":
    all_investors = sorted(set(
        inv.strip()
        for investors in df["Investors Name"].dropna()
        for inv in investors.split(",")
        if inv.strip()
    ))
    selected_investor = st.sidebar.selectbox("Select Investor", all_investors)
    if st.sidebar.button("Show Investor Details"):
        show_investor(selected_investor)
