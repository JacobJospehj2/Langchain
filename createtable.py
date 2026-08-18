from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType
import pandas as pd
import os
import re
from io import BytesIO
from notebookutils import mssparkutils # Microsoft Fabric file system utility

# ✅ Initialize Spark session
spark = SparkSession.builder.appName("ExcelToCSV").getOrCreate()

# ✅ Function to sanitize column names and convert to uppercase
def sanitize_column_name(name):
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    return sanitized_name.replace('_', '').upper()

# ✅ Function to sanitize table names and convert to camel case
def sanitize_table_name(name):
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    parts = sanitized_name.split('_')
    camel_case_name = ''.join(part.capitalize() for part in parts)
    return camel_case_name

# ✅ Function to check if a file has been processed
def is_file_processed(filename):
    file_list_df = spark.table("WellBeing.file_list")
    return file_list_df.filter((file_list_df.filename == filename) & (file_list_df.processed == "Y")).count() > 0

# ✅ Function to mark a file as being processed
def mark_file_as_processing(filename):
    spark.sql(f"""
        INSERT INTO WellBeing.file_list (filename, processed, datetime)
        VALUES ('{filename}', 'N', current_timestamp())
    """)

# ✅ Function to mark a file as processed
def mark_file_as_processed(filename):
    spark.sql(f"""
        UPDATE WellBeing.file_list
        SET processed = 'Y', datetime = current_timestamp()
        WHERE filename = '{filename}'
    """)

# ✅ Check if the WellBeing.file_list table exists and create it if not
if not spark.catalog.tableExists("WellBeing.file_list"):
    schema = StructType([
        StructField("filename", StringType(), True),
        StructField("processed", StringType(), True),
        StructField("datetime", TimestampType(), True)
    ])
    empty_df = spark.createDataFrame([], schema)
    empty_df.write.format("delta").saveAsTable("WellBeing.file_list")

# ✅ Function to extract period (Quarterly, Monthly, Weekly) from filename
def extract_period_from_path(file_path):
    filename = os.path.basename(file_path)
    if "Monthly" in filename:
        return "Monthly"
    elif "Quarterly" in filename:
        return "Quarterly"
    elif "Weekly" in filename:
        return "Weekly"
    return "Unknown"

# ✅ Function to extract date (YYYYMMDD) from filename
def extract_date_from_filename(filename):
    match = re.search(r'(\d{2}\.\d{2}\.\d{4})', filename)
    if match:
        date_str = match.group(1) # Extracts 01.01.2025
        formatted_date = date_str.replace(".", "") # Converts to 01012025
        return formatted_date
    return "Unknown_Date"

# ✅ List all Excel files from Files/Excel/ (no moving)
source_path = "Files/Excel/"

# ✅ Debug: Check if directory exists and list contents
print(f"🔍 Checking if directory exists: {source_path}")
try:
    files_in_dir = mssparkutils.fs.ls(source_path)
    print(f"✅ Directory exists. Found {len(files_in_dir)} items:")
    for f in files_in_dir:
        print(f"  - {f.name} ({'Directory' if f.isDir else 'File'})")
except Exception as e:
    print(f"❌ Directory {source_path} does not exist or is not accessible: {str(e)}")
    print("Please ensure the Files/Excel/ directory exists and contains Excel files.")
    exit()

# Check if there are any .xlsx files
xlsx_files = [f for f in files_in_dir if f.name.endswith('.xlsx')]
if not xlsx_files:
    print("❌ No .xlsx files found in Files/Excel/ directory.")
    print("Available files:")
    for f in files_in_dir:
        print(f"  - {f.name}")
    exit()

print(f"✅ Found {len(xlsx_files)} Excel files to process")

# ✅ Get list of Excel file paths directly from mssparkutils
files_list = [f.path for f in xlsx_files]
print(f"📁 Excel files to process: {[f.name for f in xlsx_files]}")

# ✅ Process each Excel file
print(f"\n🔄 Starting to process {len(files_list)} Excel files...")
for i, excel_file_path in enumerate(files_list, 1):
    file_name = os.path.basename(excel_file_path).replace(".xlsx", "") # Extract file name
    file_date = extract_date_from_filename(file_name) # Extract date for subfolder
    period = extract_period_from_path(excel_file_path) # Extract period (Quarterly, Monthly, Weekly)
    final_destination_path = f"Files/CSV/{period}/{file_date}/" # Define dynamic destination path based on period and date

    print(f"\n🔄 Processing file {i}/{len(files_list)}: {file_name}")
    print(f"   📅 Date: {file_date}, Period: {period}")
    print(f"   📁 Destination: {final_destination_path}")

    # ✅ Check if the file has already been processed
    if is_file_processed(file_name):
        print(f"📂 File already processed: {file_name}")
        continue

    # ✅ Mark the file as being processed
    mark_file_as_processing(file_name)

    try:
        # ✅ Read Excel file as binary
        file_df = spark.read.format("binaryFile").load(excel_file_path)
        file_data = file_df.select("content").collect()[0][0] # Extract binary content
    except Exception as e:
        print(f"❌ Skipping file: {excel_file_path}. Error: {str(e)}")
        continue # Skip to the next file

    # ✅ Convert binary content to a Pandas-readable stream
    file_stream = BytesIO(file_data)

    # ✅ Read Excel file using Pandas
    try:
        xls = pd.ExcelFile(file_stream, engine="openpyxl")
        print(f"📊 Found {len(xls.sheet_names)} sheets in {file_name}")
    except Exception as e:
        print(f"❌ Error reading Excel file {file_name}: {str(e)}")
        continue

    sheets_processed = 0
    # ✅ Process each sheet
    for sheet_name in xls.sheet_names:
        print(f"  📋 Processing sheet: {sheet_name}")
        
        try:
            # Read sheet as Pandas DataFrame
            df = xls.parse(sheet_name)

            # Normalize column names
            df.columns = [col.strip().lower() for col in df.columns]

            # Find the 'date' column (case-insensitive)
            date_col = next((col for col in df.columns if 'date' in col), None)

            if date_col is None:
                print(f"    ❌ No 'Date' column found in sheet: {sheet_name}. Skipping sheet.")
                continue

            # Skip rows where the date column is null
            df = df[df[date_col].notnull()]

            # ✅ Handle empty DataFrame issue
            if df.empty:
                print(f"    📂 Skipping empty sheet: {sheet_name}")
                continue # Skip empty sheets

            # Convert Pandas DataFrame to Spark DataFrame
            spark_df = spark.createDataFrame(df)

            # ✅ Sanitize column names
            for col in spark_df.columns:
                spark_df = spark_df.withColumnRenamed(col, sanitize_column_name(col))

            # ✅ Rename specific long column name to shorter version
            if "WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME" in spark_df.columns:
                spark_df = spark_df.withColumnRenamed("WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME", "SITEOFCARE")
                print(f"    🔄 Renamed column: WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME → SITEOFCARE")

            # ✅ Convert specific columns to numeric(10,2)
            for col in ['DISTRESSED', 'STRUGGLING', 'OKAY', 'THRIVING']:
                if col in spark_df.columns:
                    spark_df = spark_df.withColumn(col, spark_df[col].cast("decimal(10,2)"))

            # ✅ Define the final CSV path with proper subfolders
            temp_path = f"{final_destination_path}{sheet_name}_temp"

            # Ensure directory exists
            mssparkutils.fs.mkdirs(final_destination_path)

            # ✅ Save as a **temporary** CSV file (Fixing the "CSV as folder" issue)
            spark_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(temp_path)

            # ✅ Rename the generated CSV file to a proper `.csv`
            files = mssparkutils.fs.ls(temp_path)
            for f in files:
                if f.name.startswith("part-") and f.name.endswith(".csv"):
                    final_csv_path = f"{final_destination_path}{sheet_name}.csv"

                    # ✅ Check if the file already exists and delete it if it does
                    if mssparkutils.fs.exists(final_csv_path):
                        mssparkutils.fs.rm(final_csv_path, recurse=False)

                    # ✅ Move the file
                    mssparkutils.fs.mv(f.path, final_csv_path, True)

                    # ✅ Remove temporary folder
                    mssparkutils.fs.rm(temp_path, recurse=True)
                    print(f"    ✅ CSV Saved: {final_csv_path}")
                    sheets_processed += 1

        except Exception as e:
            print(f"    ❌ Error processing sheet {sheet_name}: {str(e)}")
            continue

    # ✅ Mark the file as processed (moved outside the sheet loop)
    if sheets_processed > 0:
        mark_file_as_processed(file_name)
        print(f"✅ File processed successfully: {file_name} ({sheets_processed} sheets processed)")
    else:
        print(f"⚠️ No sheets processed for file: {file_name}")

print("✅ Processing complete for all files!")

# ✅ Process the CSVs saved in Step 1
# Process CSV files from all periods (Monthly, Quarterly, Weekly)
all_periods = ["Monthly", "Quarterly", "Weekly"]

for period in all_periods:
    print(f"\n🔄 Processing {period} period...")
    base_period_path = f"Files/CSV/{period}/"
    processed_base_path = f"Files/CSV/Processed/{period}/" # ✅ Move processed files here

    # ✅ Ensure the main period directory exists before listing subfolders
    try:
        subfolders = [f.path for f in mssparkutils.fs.ls(base_period_path) if f.isDir]
    except Exception as e:
        print(f"❌ Directory {base_period_path} not found. Skipping processing for {period}.")
        continue

    if not subfolders:
        print(f"❌ No date-based subfolders found in {base_period_path}. Skipping {period}.")
        continue

    # ✅ Scan all date-based subfolders (YYYYMMDD)
    csv_files_list = []
    for subfolder in subfolders:
        try:
            csv_files = [f.path for f in mssparkutils.fs.ls(subfolder) if f.name.endswith(".csv")]
            csv_files_list.extend(csv_files)
        except Exception as e:
            print(f"❌ Error accessing {subfolder}: {str(e)}")
            continue # Skip inaccessible subfolders

    if not csv_files_list:
        print(f"❌ No CSV files found in {base_period_path}. Skipping {period}.")
        continue

    print(f"✅ Found {len(csv_files_list)} CSV files in {period}.")

    # ✅ Process each CSV file
    for csv_file_path in csv_files_list:
        # Extract folder details
        path_parts = csv_file_path.split("/")
        date_folder = path_parts[-2] # Extract YYYYMMDD
        sheet_name = path_parts[-1].replace(".csv", "") # Extract sheet name

        # ✅ Sanitize table name (Now follows: {sheet_name}_{period})
        table_name = sanitize_table_name(f"{sheet_name}_{period}")
        
        # ✅ Define full table name with period isolation
        full_table_name = f"WellBeing.{table_name}"
        
        print(f"    🏷️ Creating/updating table: {full_table_name}")

        # ✅ Read CSV into Spark DataFrame
        try:
            df = spark.read.option("header", "true").csv(csv_file_path)
        except Exception as e:
            print(f"❌ Error reading file {csv_file_path}: {str(e)}")
            continue # Skip this file

        # ✅ Sanitize column names
        for col in df.columns:
            df = df.withColumnRenamed(col, sanitize_column_name(col))

        # ✅ Rename specific long column name to shorter version
        if "WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME" in df.columns:
            df = df.withColumnRenamed("WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME", "SITEOFCARE")
            print(f"    🔄 Renamed column: WHATISTHEPRIMARYSITEINWHICHYOUSPENDTHEMAJORITYOFYOURTIME → SITEOFCARE")

        # ✅ Convert specific columns to numeric(10,2)
        for col in ['DISTRESSED', 'STRUGGLING', 'OKAY', 'THRIVING','TOTALEMPLOYEES']:
            if col in df.columns:
                df = df.withColumn(col, df[col].cast("decimal(10,2)"))

        # ✅ Define full table name
        # full_table_name = f"WellBeing.{table_name}" # This line is now redundant as full_table_name is defined above

        # ✅ Check if the table exists (Explicitly Check in Catalog)
        try:
            table_exists = spark._jsparkSession.catalog().tableExists(full_table_name)
        except Exception:
            table_exists = False # Assume the table doesn't exist if Spark fails to check

        if not table_exists:
            # ✅ Create the Delta table (No MSCK REPAIR TABLE required)
            try:
                df.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
                print(f"✅ Table Created: {full_table_name}")
            except Exception as e:
                print(f"❌ Error creating table {full_table_name}: {str(e)}")
                continue # Skip this file if table creation fails
        else:
            # ✅ Table exists, check if this data is already there to avoid duplicates
            try:
                # Check if data with same date already exists
                existing_data = spark.sql(f"SELECT COUNT(*) as count FROM {full_table_name} WHERE DATE = '{df.select('DATE').first()[0]}'")
                existing_count = existing_data.collect()[0]['count']
                
                if existing_count > 0:
                    print(f"    ⚠️ Data for date {df.select('DATE').first()[0]} already exists in {full_table_name}. Skipping insertion.")
                else:
                    # Insert new data
                    df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(full_table_name)
                    print(f"✅ New data inserted into existing table: {full_table_name}")
                    
            except Exception as e:
                print(f"❌ Error checking/inserting into {full_table_name}: {str(e)}")
                continue

        # ✅ Move processed file to centralized "Processed" folder
        processed_folder = f"{processed_base_path}{date_folder}/"
        processed_file_path = f"{processed_folder}{sheet_name}.csv"

        # ✅ Ensure "Processed" folder exists
        mssparkutils.fs.mkdirs(processed_folder)

        # ✅ Check if the file already exists and delete it if it does
        if mssparkutils.fs.exists(processed_file_path):
            mssparkutils.fs.rm(processed_file_path, recurse=False)

        # ✅ Move the file
        mssparkutils.fs.mv(csv_file_path, processed_file_path, True)
        print(f"✅ Moved file to: {processed_file_path}")

print("✅ All CSV files processed, and files moved successfully!")