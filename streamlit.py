import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Setting up the title and description for the Streamlit app
st.title("AI-Driven Multi-Agent Stock Trading Platform")
st.write("Analyze and visualize stock data with AI-based agent trading simulations.")

# Sidebar for input controls
st.sidebar.header("Stock Data Settings")
index = st.sidebar.selectbox("Select Stock Index", ["^BSESN"], index=0)
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-06-30"))

# Parameters for moving averages and signal generation
short_window = st.sidebar.slider("Short Moving Average Window", min_value=5, max_value=50, value=20, step=1)
long_window = st.sidebar.slider("Long Moving Average Window", min_value=50, max_value=200, value=100, step=5)
display_volume = st.sidebar.checkbox("Show Volume Chart", value=True)

# Fetch stock data
@st.cache_data
def fetch_data(index, start, end, short_window, long_window):
    ticker = yf.Ticker(index)
    hist = ticker.history(start=start, end=end)

    # Calculate the short and long moving averages
    hist[f"{short_window} DMA"] = hist['Close'].rolling(window=short_window).mean()
    hist[f"{long_window} DMA"] = hist['Close'].rolling(window=long_window).mean()
    
    # Calculate signals for long and short positions
    hist['Signal'] = 0
    hist['Signal'][short_window:] = np.where(hist[f"{short_window} DMA"][short_window:] > hist[f"{long_window} DMA"][short_window:], 1, -1)
    hist['Position'] = hist['Signal'].diff()
    
    # Calculate strategy returns
    hist['Market Return'] = hist['Close'].pct_change()
    hist['Strategy Return'] = hist['Market Return'] * hist['Signal'].shift(1)
    hist['Cumulative Strategy Return'] = (1 + hist['Strategy Return']).cumprod()
    
    return hist

# Fetch and display data
data = None
if st.sidebar.button("Fetch Data"):
    with st.spinner("Fetching data..."):
        data = fetch_data(index, start_date, end_date, short_window, long_window)
        
        if not data.empty:
            st.write(f"Displaying data for {index}")
            st.dataframe(data)

            # Plotting the main stock data with moving averages
            st.subheader("Stock Price Chart with Moving Averages and Signals")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(data.index, data['Close'], label="Close Price", color="blue")
            ax.plot(data.index, data[f"{short_window} DMA"], label=f"{short_window}-Day Moving Average", color="orange")
            ax.plot(data.index, data[f"{long_window} DMA"], label=f"{long_window}-Day Moving Average", color="green")

            # Plot buy (long) and sell (short) signals
            ax.plot(data[data['Position'] == 1].index, data[f"{short_window} DMA"][data['Position'] == 1], '^', markersize=10, color='g', label='Long Signal')
            ax.plot(data[data['Position'] == -1].index, data[f"{short_window} DMA"][data['Position'] == -1], 'v', markersize=10, color='r', label='Short Signal')
            
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            ax.legend()
            st.pyplot(fig)

            # Volume Chart
            if display_volume:
                st.subheader("Volume Chart")
                fig, ax = plt.subplots(figsize=(10, 3))
                ax.bar(data.index, data['Volume'], color="gray", alpha=0.6)
                ax.set_xlabel("Date")
                ax.set_ylabel("Volume")
                st.pyplot(fig)

            # Cumulative Strategy Returns
            st.subheader("Cumulative Strategy Returns")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(data.index, data['Cumulative Strategy Return'], label="Cumulative Strategy Return", color="purple")
            ax.set_xlabel("Date")
            ax.set_ylabel("Cumulative Returns")
            ax.legend()
            st.pyplot(fig)

# Placeholder for AI trading simulation
st.sidebar.header("AI Agent Simulation")
st.sidebar.write("Configure AI agent parameters:")
# Add additional parameters as per your AI model requirements

# AI Simulation Button (Placeholder)
if st.sidebar.button("Run AI Simulation"):
    st.subheader("AI Agent Trading Simulation")
    st.write("Running simulation... (This is a placeholder. Add your AI simulation logic here.)")
    
    # Example simulation result (replace with real output if available)
    st.write("Simulation completed.")
    st.write("Example Result: Profit/Loss, Positions Taken, etc.")

# Option to download data
if data is not None and not data.empty:
    st.subheader("Download Processed Data")
    csv = data.to_csv().encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='processed_stock_data.csv',
        mime='text/csv'
    )
else:
    st.write("No data to download. Please fetch data first.")
