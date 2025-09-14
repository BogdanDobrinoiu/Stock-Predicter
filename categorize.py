import pandas as pd

df_categorize = pd.read_csv("categorize.csv")

# for i in range(58, 77):
csv_name = "tests/bvb_merged_table_" + str(57) +".csv"
df = pd.read_csv(csv_name)
merged_df = pd.merge(df, df_categorize, on="Simbol", how="left")
merged_df.to_csv(csv_name)

