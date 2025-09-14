# 1. Idea

The main purpose of this program is to predict whether the stock prices of companies listed on the BVB –  
Bursa de Valori București (Bucharest Stock Exchange) will go up or down.

**DISCLAIMER:** This program was developed for educational purposes only. Any transactions made based on its predictions  
are your sole responsibility.

The app is structured of 4 main bodies: data selection, model training, creating predictions and the GUI.

# 2. Data selection

Multiple official and third-party options existed to access BVB (Bucharest Stock Exchange) data, but they all required 
paid subscriptions or licensing. Consequently, I implemented an automated scraper using Playwright to navigate the 
publicly available pages and extract structured data for each listed company. Before getting into details, you need to 
understand how the site is designed. 

The primary link used by the data_selector.py program is https://www.bvb.ro/FinancialInstruments/Markets/Shares, 
which contains a table listing all companies along with basic information such as Symbol, Price, Date, and Price 
Variation. One of the columns, Category, is too generic for predictive purposes. Therefore, I manually reclassified the 
companies into four categories to allow the app to predict which sector is likely to be profitable: Energy and 
Utilities, Financial and Investment, Construction and Materials, and IT and Consumables.

After extracting all the table data, I performed additional scraping for each company. Each company symbol functions as 
a button linking to a dedicated page with more detailed information. The extracted data is then preprocessed into a 
format readable by the predictive model.

Before proceeding to training the model, the data tables are transposed so that rows represent categories and columns represent
all companies with their associated information. Although this is an inefficient way to handle storage, memory 
constraints are negligible in this context, and prioritizing time efficiency was deemed more important.

# 3. Training 

