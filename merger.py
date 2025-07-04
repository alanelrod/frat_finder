import os
import pandas as pd

# === CONFIG ===
BASE_FOLDER = "/Users/alanelrod/Desktop/frat_finder/frat_results_per_school"

# === PROCESS EACH FRATERNITY FOLDER ===
for frat_name in os.listdir(BASE_FOLDER):
    frat_path = os.path.join(BASE_FOLDER, frat_name)
    if not os.path.isdir(frat_path):
        continue

    output_filename = f"{frat_name}_combined.csv"
    output_path = os.path.join(frat_path, output_filename)

    # Skip if already done
    if os.path.exists(output_path):
        print(f"⏩ Skipping {frat_name} (already combined)")
        continue

    csv_files = [f for f in os.listdir(frat_path) if f.endswith(".csv")]
    dataframes = []

    for csv_file in csv_files:
        try:
            df = pd.read_csv(os.path.join(frat_path, csv_file))
            dataframes.append(df)
        except Exception as e:
            print(f"❌ Failed to read {csv_file} in {frat_name}: {e}")

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df.to_csv(output_path, index=False)
        print(f"✅ Saved combined CSV for {frat_name} to {output_path}")
    else:
        print(f"⚠️ No CSVs found for {frat_name}")
