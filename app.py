import streamlit as st
import pandas as pd
import time as t
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

st.set_page_config(layout="wide", page_title="Startup Analysis")

df = pd.read_csv("Startup_Clean.csv")


#To change it to DateTime...
df["Date"]=pd.to_datetime(df['Date'] , errors="coerce")
df["Year"]=df["Date"].dt.year
df["Month"]=df["Date"].dt.month

#To Chagne Amont in Million$
def Conversion(Dollar):
        return int(Dollar/1000000)

df["Amount in USD"] = df["Amount in USD"].apply(Conversion)



st.sidebar.title("Startup Funding Analysis")

option = st.sidebar.selectbox("Select One", ["Overall Analysis ", "Startup", "Investor"])


# __Functions__

def load_investor_detail(slected_one):

    st.title(slected_one)
    st.subheader("Investments:-")
    Investment_list = df[df["Investors Name"].str.contains(slected_one)].head(5)[
        ["Startup Name", "Amount in USD", "Vertical" , "InvestmentnType" , "City" , "SubVertical"]]
    st.dataframe(Investment_list)
    st.subheader("Biggest Investments:-")

    col1,col2 = st.columns(2)

    with col2:
        Investment_Pie = df[df["Investors Name"].str.contains(slected_one)].groupby("Vertical")[
            "Amount in USD"].sum()
        fig1, ax1 = plt.subplots()
        ax1.pie(Investment_Pie,labels=Investment_Pie.index,autopct="%0.01f%%",shadow=True)
        st.subheader("Investment in Diff Sectors:-")
        st.pyplot(fig1)

    #....................Big Investments...........
    with col1:
        Biggest_Investment = df[df["Investors Name"].str.contains(slected_one)].groupby("Startup Name")[
            "Amount in USD"].sum().sort_values(ascending=False).head(5)

        fig, ax = plt.subplots()
        ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        ax.bar(Biggest_Investment.index, Biggest_Investment.values)
        st.pyplot(fig)


    Year_wise_Investment = df[df["Investors Name"].str.contains(slected_one)].groupby("Year")["Amount in USD"].sum()
    fig3, ax3 = plt.subplots()
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax3.get_yaxis().set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax3.plot(Year_wise_Investment.index.astype(str),
             Year_wise_Investment.values)

    # Display the plot
    st.pyplot(fig3)


def load_Overall_Inverstor():
    st.title("Overall Inverstor")
    col1 , col2 , col3 , col4 = st.columns(4)
    total = round(df["Amount in USD"].sum())
    Max_Funding = df.groupby("Investors Name")["Amount in USD"].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby("Investors Name")["Amount in USD"].sum().mean()
    with col1:
        st.metric("Total Inverstment(In USD)",str(total)+" Million" )
    with col2:
        st.metric("Max Funding(In USD)", str(Max_Funding) + " Million")
    with col3:
        st.metric("Average Funding(In USD)", str(int(avg_funding)) + " Million" )

    st.header("YoY Graph")
    selected_option = st.selectbox("Select Tye",["Total","Count"])
    if selected_option == "Total":
        temp_df= df.groupby(["Year"])["Amount in USD"].sum().reset_index()
        temp_df["x_axis"] = temp_df["Year"]
        fig5, ax5 = plt.subplots(figsize=(10,5))
        ax5.set_xlabel("Date (Year)")
        ax5.set_ylabel("Sum of Investments in Million$")
        ax5.plot(temp_df["x_axis"], temp_df["Amount in USD"])
        st.pyplot(fig5)
    elif selected_option == "Count":
        temp_df = df.groupby(["Year"])["Amount in USD"].count().reset_index()
        temp_df["x_axis"] = temp_df["Year"]
        fig5, ax5 = plt.subplots(figsize=(10, 5))
        ax5.set_xlabel("Date (Year)")
        ax5.set_ylabel("Count of Investments in Million$")
        ax5.plot(temp_df["x_axis"], temp_df["Amount in USD"])
        st.pyplot(fig5)


if option == "Overall Analysis ":
    load_Overall_Inverstor()
elif option == "Startup":
    st.sidebar.selectbox("Select Startup", sorted(df["Startup Name"].unique().tolist()))
    btn2 = st.sidebar.button("Find Startuo Details")
    st.title("Startups Analysis")
else:
    selected_investr = st.sidebar.selectbox("Select Investor", sorted(set(df["Investors Name"].str.split(",").sum())))
    bt1 = st.sidebar.button("Find Startuo Details")
    if bt1:
        load_investor_detail(selected_investr)
