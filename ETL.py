# ///////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\ 
# |         Contributed by Robb Northrup         |
# \\\\\\\\\\\\\\\\\\\\\\\/////////////////////////

import pandas as pd
import sqlite3

# Filepaths
excel_file = "sample ClassSched-CS-S25.xlsx"  # Replace with the actual Excel file path
database_file = "College.db"  # SQLite database file

# Step 1: Extract - Load data from Excel
def extract_data(file_path):
    # Load the single sheet into a DataFrame
    schedule_df = pd.read_excel(file_path, sheet_name=0, skiprows=1)  # Skip the first row (header)
    return schedule_df

# Step 2: Transform - Clean and prepare the data
def transform_data(schedule_df):
    # Debug: Print column names to verify
    print("Columns in the dataset:", schedule_df.columns)

    # Rename columns to match database schema
    schedule_df.rename(columns={
        "College": "College",
        "Subject": "Subject",
        "Catalog": "Course_ID",
        "Section": "Section_Code",
        "Title": "Title",
        "Room": "Classroom_ID",
        "Instructor Last Name": "Instructor_Last",
        "Instructor First Name": "Instructor_First",
        "Room Capacity": "Room_Capacity",
        "Enrollment Capacity": "Enrollment_Capacity",
        "Current Enrollment": "Enrollment_Actual",
        "Waitlist Capacity": "Waitlist_Capacity",
        "Waitlist Total": "Waitlist_Actual",
        "Class Days": "Meeting_Day",
        "Class Start Time": "Meeting_Time",
        "Start Date": "Start_Date",
        "End Date": "End_Date"
    }, inplace=True)

    # Example transformations
    schedule_df["Meeting_Time"] = schedule_df["Meeting_Time"].astype(str)  # Ensure time is string
    schedule_df["Enrollment_Actual"] = schedule_df["Enrollment_Actual"].fillna(0).astype(int)
    schedule_df["Waitlist_Actual"] = schedule_df["Waitlist_Actual"].fillna(0).astype(int)
    schedule_df["Status"] = "Open"  # Default status

    # Split instructor names into separate columns
    schedule_df["Instructor_Name"] = schedule_df["Instructor_First"] + " " + schedule_df["Instructor_Last"]

    return schedule_df

# Step 3: Load - Insert data into SQLite database
def load_data(schedule_df, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Insert data into the appropriate tables
    # Example: Insert into Course_Section
    course_section_df = schedule_df[[
        "Course_ID", "Section_Code", "Classroom_ID", "Meeting_Day", "Meeting_Time",
        "Enrollment_Capacity", "Waitlist_Capacity", "Enrollment_Actual", "Waitlist_Actual"
    ]]
    # Fix: Ensure Course_ID and Section_Code are strings before concatenation
    course_section_df.loc[:, "Section_ID"] = course_section_df["Course_ID"].astype(str) + "-" + course_section_df["Section_Code"].astype(str)
    course_section_df.loc[:, "Term"] = "Spring 2025"  # Default term
    course_section_df.loc[:, "Status"] = "Open"  # Default status

    # Map Instructor_ID from Instructor table
    instructor_df = schedule_df[["Instructor_First", "Instructor_Last"]].drop_duplicates()
    instructor_df["Instructor_ID"] = instructor_df["Instructor_First"].str[0] + instructor_df["Instructor_Last"]
    instructor_df["Name"] = instructor_df["Instructor_First"] + " " + instructor_df["Instructor_Last"]
    instructor_mapping = instructor_df.set_index("Name")["Instructor_ID"].to_dict()
    course_section_df["Instructor_ID"] = schedule_df["Instructor_Name"].map(instructor_mapping)

    course_section_df.to_sql("Course_Section", conn, if_exists="append", index=False)

    # Example: Insert into Instructor
    instructor_df.to_sql("Instructor", conn, if_exists="append", index=False)

    # Extract and load Building data
    building_df = schedule_df[["Room"]].drop_duplicates()
    building_df["BLDG_ID"] = building_df["Room"].str.split(" ").str[0]  # Extract building ID
    building_df["NAME"] = building_df["BLDG_ID"]  # Use BLDG_ID as NAME for simplicity
    building_df.to_sql("Building", conn, if_exists="append", index=False)

    # Extract and load Classroom data
    classroom_df = schedule_df[["Room", "Room Capacity"]].drop_duplicates()
    classroom_df["Classroom_ID"] = classroom_df["Room"]
    classroom_df["Bldg_ID"] = classroom_df["Room"].str.split(" ").str[0]  # Extract building ID
    classroom_df["Room_Num"] = classroom_df["Room"].str.split(" ").str[1]  # Extract room number
    classroom_df["Floor"] = 1  # Default value
    classroom_df["Seats"] = classroom_df["Room Capacity"]
    classroom_df["WiFi"] = "No"  # Default value
    classroom_df["ADA_Access"] = "No"  # Default value
    classroom_df.to_sql("Classroom", conn, if_exists="append", index=False)

    # Extract and load Course data
    course_df = schedule_df[["Course_ID", "Title"]].drop_duplicates()
    course_df["Description"] = "No description available"  # Default value
    course_df["No_Credits"] = 3  # Default value
    course_df.to_sql("Course", conn, if_exists="append", index=False)

    # Extract and load Course_Prerequisite data (if prerequisites exist in the dataset)
    if "Pre_Req_Course_ID" in schedule_df.columns:
        course_prerequisite_df = schedule_df[["Course_ID", "Pre_Req_Course_ID"]].dropna()
        course_prerequisite_df.to_sql("Course_Prerequisite", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

# Main ETL Process
def etl_process(excel_file, database_file):
    print("Starting ETL process...")
    print("Extracting data...")
    schedule_df = extract_data(excel_file)
    print("Transforming data...")
    cleaned_schedule_df = transform_data(schedule_df)
    print("Loading data into database...")
    load_data(cleaned_schedule_df, database_file)
    print("ETL process completed successfully!")

# Run the ETL process
if __name__ == "__main__":
    etl_process(excel_file, database_file)