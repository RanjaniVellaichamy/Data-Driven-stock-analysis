# Data-Driven-stock-analysis
This project provides a comprehensive and interactive dashboard to analyze the performance of Nifty 50 stocks. Using historical stock data, the dashboard helps investors, analysts, and enthusiasts explore market trends, compare sector performance, and identify high-performing or volatile stocks.

🔍 Features

-📈 Market Summary: View the overall performance of Nifty 50 stocks.

-🏭 Sector-Wise Analysis: Break down stock performance by sector (IT, Finance, Pharma, etc.).

-💹 Top Performers: Identify stocks with the highest yearly returns.

-⚠️ Volatility Analysis: Explore the most volatile stocks based on daily returns.

-🔎 Interactive Filtering: Filter stocks by sector, date range, and other parameters.

-📊 Visualizations: Clean and insightful charts using Matplotlib/Seaborn in Streamlit or Power BI.



🗃️ Data Source

-Historical stock data (Open, High, Low, Close, Volume) in CSV format.

-Sector mapping (CSV file manually or from external sources).

-Daily data organized by date (e.g., data/2023-10-03_05-30-00.yaml or .csv).



🛠️ Tech Stack

-Frontend: Streamlit for building the interactive web app.

-Visualization: Matplotlib, Seaborn, Power BI (optional).

-Backend: Pandas, Python.

-Data Storage: Local CSV files / MySQL (optional for structured storage).



📁 Project Structure

stock-analysis/
├── data/

│   ├── 2023-10/

│   └── sector_mapping.csv

├── app.py

├── Extractdata.py

├── utils/

│   └── helpers.py

├── README.md

└── requirements.txt


