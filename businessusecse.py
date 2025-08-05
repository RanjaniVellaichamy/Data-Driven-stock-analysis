import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

# ---- Config ----
st.set_page_config(page_title="📈 Nifty 50 Dashboard", layout="wide")

# ---- Sidebar Navigation ----
with st.sidebar:
    selected = option_menu(
        menu_title="Nifty 50 Dashboard",
        options=[
            "Market Summary", "Volatility", "Top Performers", "Sector-wise Analysis",
            "Correlation Heatmap", "Monthly Gainers/Losers", "Stock Rankings",
            "Investment Insights", "Decision Support"
        ],
        icons=["bar-chart", "activity", "arrow-up-circle", "pie-chart", "grid-3x3", "calendar",
               "trophy", "graph-up", "lightbulb"],
        menu_icon="graph-up",
        default_index=0,
    )

folder_path = "nifty_50"
if not os.path.exists(folder_path):
    st.error("❌ 'nifty_50' folder not found.")
    st.stop()

# ---- Load and Process All Stock Data ----
def load_stock_data():
    all_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            symbol = file.replace(".csv", "").upper()
            try:
                df = pd.read_csv(os.path.join(folder_path, file))
                df['date'] = pd.to_datetime(df['date'])
                df = df[df['date'].dt.year == 2023]
                df['symbol'] = symbol
                all_data.append(df)
            except Exception as e:
                st.warning(f"⚠️ Error loading {symbol}: {e}")
    return all_data

stock_dfs = load_stock_data()
if not stock_dfs:
    st.warning("⚠️ No CSV files loaded.")
    st.stop()

# ---- Merge Closing Prices for Heatmap ----
def get_merged_close_prices(stock_dfs):
    close_data = []
    for df in stock_dfs:
        symbol = df['symbol'].iloc[0]
        temp = df[['date', 'close']].rename(columns={'close': symbol})
        close_data.append(temp)

    merged = close_data[0]
    for df in close_data[1:]:
        merged = pd.merge(merged, df, on='date', how='inner')
    merged = merged[merged['date'].dt.year == 2023]
    merged.set_index('date', inplace=True)
    return merged

# ---- Calculate summary upfront (used by several pages) ----
df_all = pd.concat(stock_dfs, ignore_index=True)
df_all.sort_values(by=["symbol", "date"], inplace=True)
summary = df_all.groupby("symbol").agg(
    first_close=('close', lambda x: x.iloc[0]),
    last_close=('close', lambda x: x.iloc[-1]),
    average_price=('close', 'mean'),
    volatility=('close', 'std')
).reset_index()
summary['return_%'] = ((summary['last_close'] - summary['first_close']) / summary['first_close']) * 100
top_10 = summary.sort_values(by="return_%", ascending=False).head(10)
bottom_10 = summary.sort_values(by="return_%").head(10)

# ---- Market Summary ----
if selected == "Market Summary":
    st.title("📊 Market Summary - Nifty 50 (2023)")
    green_count = (summary['return_%'] > 0).sum()
    red_count = (summary['return_%'] <= 0).sum()
    st.markdown(f"✅ **Green Stocks**: {green_count} &nbsp;&nbsp;&nbsp; ❌ **Red Stocks**: {red_count}")
    st.markdown(f"💰 **Average Price**: ₹{summary['average_price'].mean():.2f} &nbsp;&nbsp;&nbsp; "
                f"📦 **Avg Volatility**: {summary['volatility'].mean():.2f}")

    st.subheader("🟢 Top 10 Green Stocks")
    st.dataframe(top_10[['symbol', 'return_%']].style.format({"return_%": "{:.2f}"}))

    st.subheader("🔴 Top 10 Red Stocks")
    st.dataframe(bottom_10[['symbol', 'return_%']].sort_values("return_%").style.format({"return_%": "{:.2f}"}))

# ---- Volatility ----
elif selected == "Volatility":
    st.title("📈 Most Volatile Nifty 50 Stocks (2023)")
    df_all['daily_return'] = df_all.groupby('symbol')['close'].pct_change()
    df_all.dropna(subset=['daily_return'], inplace=True)
    volatility_df = df_all.groupby('symbol')['daily_return'].std().reset_index().rename(columns={'daily_return': 'volatility'})
    top10 = volatility_df.sort_values('volatility', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top10, x='symbol', y='volatility', palette='magma', ax=ax)
    ax.set_title('Top 10 Most Volatile Stocks')
    ax.set_xlabel('Stock Symbol')
    ax.set_ylabel('Volatility (Std Dev)')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ---- Top Performers ----
elif selected == "Top Performers":
    st.title("📈 Cumulative Returns - Top 5 Performing Stocks (2023)")
    df_all['cumulative_return'] = df_all.groupby('symbol')['close'].transform(lambda x: x / x.iloc[0])
    top5_symbols = df_all.groupby('symbol')['cumulative_return'].last().sort_values(ascending=False).head(5).index.tolist()
    df_top5 = df_all[df_all['symbol'].isin(top5_symbols)]
    fig, ax = plt.subplots(figsize=(12, 6))
    for sym in top5_symbols:
        sym_df = df_top5[df_top5['symbol'] == sym]
        ax.plot(sym_df['date'], sym_df['cumulative_return'], label=sym)
    ax.set_title("Top 5 Performing Stocks (Cumulative Return)")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    st.pyplot(fig)

# ---- Sector-wise Analysis, Correlation, Monthly Gainers/Losers (unchanged) ----
elif selected == "Sector-wise Analysis":
    st.title("🏭 Sector-wise Analysis")
    sector_map = {
        'RELIANCE': 'Energy', 'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HDFCBANK': 'Financials',
        'ICICIBANK': 'Financials', 'AXISBANK': 'Financials', 'SBIN': 'Financials', 'KOTAKBANK': 'Financials',
        'HINDUNILVR': 'Consumer', 'ITC': 'Consumer', 'TITAN': 'Consumer', 'ONGC': 'Energy', 'NTPC': 'Utilities',
        'SUNPHARMA': 'Pharma', 'CIPLA': 'Pharma', 'DRREDDY': 'Pharma', 'BAJFINANCE': 'Financials',
        'ASIANPAINT': 'Utilities', 'BHARTIARTL': 'Consumer', 'TECHM': 'IT', 'NESTLEIND': 'Consumer',
        'LT': 'Industrials', 'TATASTEEL': 'Materials', 'JSWSTEEL': 'Materials'
        # Add more mappings as needed
    }

    returns = []
    for df in stock_dfs:
        symbol = df['symbol'].iloc[0]
        sector = sector_map.get(symbol, None)
        if sector:
            cum_return = df.sort_values('date')['close'].iloc[-1] / df.sort_values('date')['close'].iloc[0]
            returns.append({'sector': sector, 'return': cum_return})
    sector_df = pd.DataFrame(returns)
    avg_sector = sector_df.groupby('sector')['return'].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    avg_sector.sort_values(ascending=False).plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title("Average Yearly Return by Sector")
    ax.set_ylabel("Average Cumulative Return")
    st.pyplot(fig)
elif selected == "Correlation Heatmap":
    st.title("🔗 Correlation Heatmap")
    merged_df = get_merged_close_prices(stock_dfs)
    returns_df = merged_df.pct_change().dropna()
    corr_matrix = returns_df.corr()
    fig, ax = plt.subplots(figsize=(16, 10))
    sns.heatmap(corr_matrix, cmap='coolwarm', annot=True, fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Stock Return Correlation Heatmap (Daily % Change)", fontsize=16)
    st.pyplot(fig)

elif selected == "Monthly Gainers/Losers":
    st.title("📅 Monthly Gainers and Losers (2023)")

    monthly_data = []
    for df in stock_dfs:
        df['month'] = df['date'].dt.to_period('M')
        symbol = df['symbol'].iloc[0]
        for month, group in df.groupby('month'):
            group = group.sort_values('date')
            start = group.iloc[0]['close']
            end = group.iloc[-1]['close']
            if start > 0:
                pct_change = (end - start) / start
                monthly_data.append({'symbol': symbol, 'month': str(month), 'return': pct_change})

    returns_df = pd.DataFrame(monthly_data)
    for month in sorted(returns_df['month'].unique()):
        st.markdown(f"### 📆 {month}")
        month_df = returns_df[returns_df['month'] == month]
        top5 = month_df.sort_values('return', ascending=False).head(5)
        bottom5 = month_df.sort_values('return').head(5)

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            ax.barh(top5['symbol'], top5['return'], color='green')
            ax.set_title(f"Top 5 Gainers - {month}")
            ax.set_xlim(0, top5['return'].max()*1.2)
            ax.invert_yaxis()
            st.pyplot(fig)
        with col2:
            fig, ax = plt.subplots()
            ax.barh(bottom5['symbol'], bottom5['return'], color='red')
            ax.set_title(f"Top 5 Losers - {month}")
            ax.set_xlim(bottom5['return'].min()*1.2, 0)
            ax.invert_yaxis()
            st.pyplot(fig)
# ---- Stock Rankings ----
elif selected == "Stock Rankings":
    st.title("🏆 Top & Bottom 10 Stock Rankings")
    st.subheader("🟢 Top 10 Green Stocks")
    st.dataframe(top_10[['symbol', 'return_%']], use_container_width=True)
    st.subheader("🔴 Top 10 Red Stocks")
    st.dataframe(bottom_10[['symbol', 'return_%']], use_container_width=True)
    fig1, ax1 = plt.subplots()
    ax1.bar(top_10['symbol'], top_10['return_%'], color='green')
    ax1.set_title("Top 10 Green Stocks")
    ax1.set_ylabel("Return (%)")
    ax1.set_xticklabels(top_10['symbol'], rotation=45)
    st.pyplot(fig1)
    fig2, ax2 = plt.subplots()
    ax2.bar(bottom_10['symbol'], bottom_10['return_%'], color='red')
    ax2.set_title("Top 10 Red Stocks")
    ax2.set_ylabel("Return (%)")
    ax2.set_xticklabels(bottom_10['symbol'], rotation=45)
    st.pyplot(fig2)

# ---- Investment Insights ----
elif selected == "Investment Insights":
    st.title("📊 Investment Insights: Consistent Gainers & Decliners")
    gainers = summary[summary["return_%"] > 20].sort_values("return_%", ascending=False)
    decliners = summary[summary["return_%"] < -20].sort_values("return_%")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Consistent Gainers (Return > 20%)")
        if not gainers.empty:
            st.dataframe(gainers[['symbol', 'return_%']], use_container_width=True)
        else:
            st.info("No consistent gainers found.")
    with col2:
        st.subheader("📉 Significant Decliners (Return < -20%)")
        if not decliners.empty:
            st.dataframe(decliners[['symbol', 'return_%']], use_container_width=True)
        else:
            st.info("No significant decliners found.")

# ---- Decision Support ----
elif selected == "Decision Support":
    st.title("🧠 Decision Support: Stock Behavior Summary")
    behavior_table = summary[['symbol', 'average_price', 'volatility', 'return_%']] \
        .sort_values(by='return_%', ascending=False).reset_index(drop=True)
    st.dataframe(behavior_table, use_container_width=True)
