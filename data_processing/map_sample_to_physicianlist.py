import pandas as pd
import os
import re

def process_data():
    # Paths
    csv_path = "data/doctor_image_details (1).csv"
    excel_path = "data/R232C6_Dhanmondi_Data (2).xlsx"
    output_path = "data/mapped_doctor_data.csv"

    print(f"Loading CSV: {csv_path}")
    df_csv = pd.read_csv(csv_path)
    print(f"CSV loaded. Sample data:\n{df_csv.head(2)}")

    # Extract PR from path
    # User says: "starting with pr is the pr"
    # Example: /content/drive/MyDrive/All_Image/PR232C6DHK23_P001.jpg -> PR232C6DHK23_P001
    def extract_pr(path):
        if not isinstance(path, str):
            return None
        # Extract the filename part starting with PR (case insensitive just in case, but usually uppercase)
        match = re.search(r'(PR[A-Z0-9_]+)', os.path.basename(path), re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    df_csv['extracted_pr'] = df_csv['IMAGE_NAME_WITH_PATH'].apply(extract_pr)
    print(f"Extracted PR sample: {df_csv['extracted_pr'].head().tolist()}")

    print(f"Loading Excel: {excel_path}")
    # Load Excel - using the first sheet by default as checked before
    df_xl = pd.read_excel(excel_path)
    print(f"Excel loaded. Sample data:\n{df_xl.head(2)}")
    
    # Let's check for case insensitive match too
    df_xl['IMG_NM_upper'] = df_xl['IMG_NM'].astype(str).str.upper()
    df_csv['extracted_pr_upper'] = df_csv['extracted_pr'].astype(str).str.upper()

    print("Merging with Dhanmondi Data...")
    # Join on IMG_NM as it's the actual link between the files
    merged_df = pd.merge(
        df_csv, 
        df_xl, 
        left_on='extracted_pr_upper', 
        right_on='IMG_NM_upper', 
        how='left'
    )

    # Now load Physicianlist
    physician_list_path = "data/Physicianlist.xlsx"
    print(f"Loading Physician List: {physician_list_path}")
    df_physician = pd.read_excel(physician_list_path)
    
    # In Dhanmondi data it is 'PHYID', in Physicianlist it is 'PHY_ID'
    print("Merging with Physician List...")
    merged_df = pd.merge(
        merged_df,
        df_physician,
        left_on='PHYID',
        right_on='PHY_ID',
        how='left',
        suffixes=('', '_phy')
    )

    # Clean up temporary columns and unwanted columns
    columns_to_drop = [
        'extracted_pr', 'extracted_pr_upper', 'IMG_NM_upper',
        'DOCTOR_DETAILS_COMBINED', 'MONTH', 'ROUND', 'YEAR', 'BOOKID', 'SHOPID', 
        'CDATE', 'PDATE', 'PRSTYPE', 'PSCSLNO', 'PHY_ID', 'PHY_NM', 'PHY_DEG',
        'VC2', 'NAME', 'GP', 'QTPRS', 'QTPURCH', 'CYCLE', 'FICODE', 'OPERATOR', 
        'DIAGCD', 'DIAGNAME', 'DIAGOPTR', 'DIAGEDTR', 'GENDER', 'AGE', 'PHYSPCD', 
        'CINSTCD', 'EDATE', 'ETIME', 'DIAEDATE', 'DIAETIME', 'SCHDSLT', 'FSCODE', 
        'EDITOR', 'EDDATE', 'ROUND_phy', 'CINSTCD_phy', 'MCODE', 'MARKET', 
        'PHYSP_C', 'FICODE_phy', 'SC', 'NOTE', 'PD03', 'PD04', 'DUPLICATE', 
        'OLDCODE', 'SHEETNO', 'EDITDATE', 'EDITOR_phy', 'UNICODE', 'CYCLE_phy', 
        'DSDCODE', 'MCHCODE', 'CH_PHNO1', 'CH_PHNO2', 'CH_PHNO3', 'PHY_PHNO', 
        'PHYEMAIL', 'PHYNM_DT_DUP', 'PHYNM_ALL_DUP', 'CHNM_DT_DUP', 'CHNM_ALL_DUP'
    ]
    
    # Filter columns_to_drop to only those that exist in the dataframe
    existing_drops = [c for c in columns_to_drop if c in merged_df.columns]
    merged_df = merged_df.drop(columns=existing_drops)
    

    print(f"Merge complete. Rows in CSV: {len(df_csv)}, Rows in Merged: {len(merged_df)}")
    print(f"Matched rows in Dhanmondi: {merged_df['PRSID'].notna().sum() if 'PRSID' in merged_df.columns else 'N/A'}")
    print(f"Remaining columns: {merged_df.columns.tolist()}")

    # Save to CSV
    merged_df.to_csv(output_path, index=False)
    print(f"Result saved to: {output_path}")

if __name__ == "__main__":
    process_data()
