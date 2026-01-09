import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# --- CONFIGURATION ---
# Adjust these filenames if yours are different
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the backend folder
INPUT_FILE = os.path.join(BASE_DIR, 'coursea_origin.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'coursea_data.csv')

# Columns that MUST be treated as numbers (for the recommendation math)
NUMERIC_COLUMNS = ['tuition_fees', 'duration_months', 'min_gpa', 'acceptance_rate']

def preprocess_programs():
    # 1. Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file not found at: {INPUT_FILE}")
        print("   Please check the path or filename.")
        return

    print(f"🔄 Loading raw data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # 2. Handle Missing Values
    print("🧹 Cleaning missing values...")
    
    # Fill text columns with "Unknown"
    text_cols = df.select_dtypes(include=['object']).columns
    df[text_cols] = df[text_cols].fillna('Unknown')
    
    # Fill numeric columns with the Median (avoids skewing data with 0s)
    # We only process columns that actually exist in the CSV
    existing_numeric_cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
    
    for col in existing_numeric_cols:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # 3. Text Standardization
    # Convert 'field' or 'category' to lowercase so "CS" matches "cs"
    if 'field' in df.columns:
        df['field'] = df['field'].str.lower().str.strip()
    if 'program_name' in df.columns:
        df['program_name'] = df['program_name'].str.strip()

    # 4. Normalization (Scaling)
    # This creates new columns with '_norm' suffix (values 0.0 to 1.0)
    # CRITICAL: This fixes the "illogical recommendations" issue.
    print("⚖️  Normalizing numeric data (0-1 scale)...")
    
    if existing_numeric_cols:
        scaler = MinMaxScaler()
        # Calculate scaled values
        scaled_data = scaler.fit_transform(df[existing_numeric_cols])
        
        # Add them back to dataframe with '_norm' suffix
        for i, col in enumerate(existing_numeric_cols):
            new_col_name = f"{col}_norm"
            df[new_col_name] = scaled_data[:, i]
            print(f"   - Created {new_col_name}")
    else:
        print("⚠️ Warning: No numeric columns found to normalize.")

    # 5. Save the Cleaned File
    # Ensure the directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print("-" * 40)
    print(f"✅ Success! Preprocessed data saved to: {OUTPUT_FILE}")
    print("-" * 40)
    print("Next Step: Update your database seed script to load this new file.")

if __name__ == "__main__":
    preprocess_programs()