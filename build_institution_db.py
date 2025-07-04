import pandas as pd

# === Step 1: Load the institution-level merged file ===
csv_path = "/Users/alanelrod/Desktop/frat_finder/origin_data/collegeDB.csv"
print("📄 Reading institution-level data from:", csv_path)

df = pd.read_csv(csv_path, low_memory=False)
print(f"✅ Loaded {len(df)} rows from merged data.")

# === Step 2: Filter to 4-year institutions only ===
df_filtered = df[
    (df['ICLEVEL'] == 1) &  # 1 = 4-year institutions
    (df['CONTROL'].isin([1, 2, 3]))  # 1 = Public, 2 = Private nonprofit, 3 = Private for-profit
]

# === Step 3: Keep relevant columns and rename for clarity ===
df_out = df_filtered[[
    'UNITID', 'INSTNM', 'CITY', 'STABBR', 'INSTURL', 'CONTROL', 'UGDS'
]].rename(columns={
    'INSTNM': 'Institution Name',
    'CITY': 'City',
    'STABBR': 'State',
    'INSTURL': 'Website',
    'CONTROL': 'Control',
    'UGDS': 'Undergrad Enrollment'
})
4
# === Step 4: Clean and filter further ===
df_out = df_out[df_out['Website'].notna()]
df_out = df_out[df_out['Undergrad Enrollment'] > 1000]

# === Step 5: Export to CSV ===
output_path = "filtered_universities.csv"
df_out.to_csv(output_path, index=False)
print(f"✅ Cleaned university list saved to '{output_path}' with {len(df_out)} rows.")
