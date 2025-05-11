# ///////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\ 
# |         Contributed by Robb Northrup         |
# \\\\\\\\\\\\\\\\\\\\\\\/////////////////////////

import pandas as pd
import sqlite3

# Filepaths
excel_file = "sample ClassSched-CS-S25.xlsx"  # Replace with the actual Excel file path
database_file = "College.db"  # SQLite database file

# Step 1: Extract -> Here we will take the data from the given excel file and then convert it into a pandas dataframe
def extract_data(file_path):
    # Load the single sheet into a DataFrame
    schedule_df = pd.read_excel(file_path, sheet_name=0, skiprows=1)  # Skip the first row (header)
    return schedule_df

# Step 2: Transform -> This is the step where we clean and transform the data to fit the database schema (detailed in the ERD)
def transform_data(schedule_df):
    # Debug: Print column names to verify
    print("Columns in the dataset prior to transformation:", schedule_df.columns)

    # Rename columns to match ERD schema
    # NOTE: THE BUILDING AND ROOM NUMBERS ARE COMBINED INTO A SINGLE COLUMN, HERE
    schedule_df.rename(columns={
        # Unused right now
        "College": "Department", # FIX: Currently unused
        "Subject": "Subject", # FIX: Currently unused
        "Catalog": "Catalog", # FIX: Currently unused
        "Start Date": "Start_Date",
        "End Date": "End_Date",
        "Component": "Component", # FIX: Currently unused

        # used right now
        "Class Nbr": "Course_ID",
        # inst ID
        # Classroom ID (to be pulled from room?)
        # Term
        "Class Days": "Meeting_Day",
        "Class Start Time": "CLASS_START_TIME",
        "Class End Time": "CLASS_END_TIME",
        "Section": "Section_Code",
        "Enrollment Capacity": "Enrollment_Capacity",
        "Waitlist Capacity": "Waitlist_Capacity",
        "Class Status": "Status",
        "Waitlist Total": "Waitlist_Actual",
        "Current Enrollment": "Enrollment_Actual",
        # PRE_REQ_COURSE_ID
        "Title": "Title",
        # DESCRIPTION
        "Prgrss Unt": "No_Credits",
        "Instructor Last Name": "Instructor_Last", # TO BE COMBINED WITH FIRST NAME as "NAME - INSTRUCTOR"
        "Instructor First Name": "Instructor_First",
        "Room": "Classroom_ID", # FIX: TO BE SPLIT INTO BLDG_ID AND ROOM_NUM
        # BLDG_ID to be pulled from first part of room
        # ROOM_NUM to be pulled from second part of room
        # FLOOR to be pulled from first digit of ROOM_NUM
        "Room Capacity": "Seats"
        # WIFI
        # ADA_ACCESS
        # NAME (BLDG)    
    }, inplace=True)

    schedule_df["Enrollment_Actual"] = schedule_df["Enrollment_Actual"].fillna(0).astype(int)
    schedule_df["Waitlist_Actual"] = schedule_df["Waitlist_Actual"].fillna(0).astype(int)
    for index, row in schedule_df.iterrows():
        if row["Waitlist_Actual"] > 0:
            schedule_df.at[index, "Status"] = "Waitlist"
        else:
            schedule_df.at[index, "Status"] = "Open"

    # Split Room into Bldg_ID and Room_Num
    schedule_df["Bldg_ID"] = schedule_df["Classroom_ID"].str.split(" ").str[0]
    schedule_df["Room_Num"] = schedule_df["Classroom_ID"].str.split(" ").str[1]

    # Derive FLOOR from first digit of Room_Num (if numeric)
    schedule_df["Floor"] = schedule_df["Room_Num"].str[0].apply(lambda x: int(x) if x.isdigit() else 1)

    # Add WiFi and ADA_Access columns with default values
    schedule_df["WiFi"] = ""
    schedule_df["ADA_Access"] = ""

    # Add NAME (BLDG) as a copy of Bldg_ID or set as needed
    schedule_df["BLDG_NAME"] = schedule_df["Bldg_ID"]
    for index, row in schedule_df.iterrows():
        if row["Bldg_ID"] == "SEM":
            schedule_df.at[index, "BLDG_NAME"] = "Scrugham Engineering Mines"
        elif row["Bldg_ID"] == "WPEB":
            schedule_df.at[index, "BLDG_NAME"] = "William N. Pennington Engineering Building"
        elif row["Bldg_ID"] == "LME":
            schedule_df.at[index, "BLDG_NAME"] = "Paul Laxalt Mineral Engineering"
        elif row["Bldg_ID"] == "DMSC":
            schedule_df.at[index, "BLDG_NAME"] = "Davidson Math and Science Center"
        elif row["Bldg_ID"] == "CFA":
            schedule_df.at[index, "BLDG_NAME"] = "Church Fine Arts"
        elif row["Bldg_ID"] == "AB":
            schedule_df.at[index, "BLDG_NAME"] = "Ansari Business Building"

    # If PRE_REQ_COURSE_ID or DESCRIPTION are missing, add with default values
    if "Pre_Req_Course_ID" not in schedule_df.columns:
        schedule_df["Pre_Req_Course_ID"] = None
    if "Description" not in schedule_df.columns:
        schedule_df["Description"] = "No description available"
    if "Instructor_ID" not in schedule_df.columns:
        schedule_df["Instructor_ID"] = None

    # Generate Instructor_ID if not present
    schedule_df["Instructor_ID"] = (
        schedule_df["Instructor_First"].str[0].fillna('X') +
        schedule_df["Instructor_Last"].fillna('Unknown')
    ).str.upper()
    print(schedule_df.head())

    return schedule_df

# Step 3: Load -> Here we are gunna load the data into the database (College.db)
def load_data(schedule_df, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # --- Building Table ---
    building_df = schedule_df[["Bldg_ID", "BLDG_NAME"]].drop_duplicates()
    building_df.rename(columns={"BLDG_NAME": "NAME"}, inplace=True)
    building_df.to_sql("Building", conn, if_exists="append", index=False)

    # --- Classroom Table ---
    classroom_df = schedule_df[["Classroom_ID", "Bldg_ID", "Room_Num", "Floor", "Seats", "WiFi", "ADA_Access"]].drop_duplicates()
    classroom_df.to_sql("Classroom", conn, if_exists="append", index=False)

    # --- Instructor Table ---
    # Use Instructor_ID from schedule_df (already created in transform_data)
    instructor_df = schedule_df[["Instructor_ID", "Instructor_First", "Instructor_Last"]].drop_duplicates()
    instructor_df.rename(columns={
        "Instructor_First": "FIRST_NAME",
        "Instructor_Last": "LAST_NAME"
    }, inplace=True)
    instructor_df = instructor_df[["Instructor_ID", "FIRST_NAME", "LAST_NAME"]]
    instructor_df.to_sql("Instructor", conn, if_exists="append", index=False)

    # --- Course Table ---
    course_df = schedule_df[["Course_ID", "Title", "Description", "No_Credits"]].drop_duplicates()
    course_df.rename(columns={"No_Credits": "NO_CREDITS"}, inplace=True)
    course_df.to_sql("Course", conn, if_exists="append", index=False)

    # --- Course_Section Table ---
    # Use Instructor_ID from schedule_df
    schedule_df["SECTION_ID"] = schedule_df["Course_ID"].astype(str) + "-" + schedule_df["Section_Code"].astype(str)
    schedule_df["TERM"] = "Spring 2025"
    course_section_df = schedule_df[[
        "Department", "SECTION_ID", "Course_ID", "Instructor_ID", "Classroom_ID", "TERM",
        "CLASS_START_TIME", "CLASS_END_TIME", "Component", "Meeting_Day", "Section_Code",
        "Enrollment_Capacity", "Waitlist_Capacity", "Status", "Waitlist_Actual", "Enrollment_Actual"
    ]].copy()
    course_section_df.rename(columns={
        "CLASS_START_TIME": "CLASS_START_TIME",
        "CLASS_END_TIME": "CLASS_END_TIME",
        "Component": "COMPONENT",
        "Meeting_Day": "MEETING_DAY",
        "Section_Code": "SECTION_CODE",
        "Enrollment_Capacity": "ENROLLMENT_CAPACITY",
        "Waitlist_Capacity": "WAITLIST_CAPACITY",
        "Status": "STATUS",
        "Waitlist_Actual": "WAITLIST_ACTUAL",
        "Enrollment_Actual": "ENROLLMENT_ACTUAL"
    }, inplace=True)
    course_section_df["CLASS_END_TIME"] = course_section_df["CLASS_START_TIME"]
    course_section_df = course_section_df[[
        "Department", "SECTION_ID", "Course_ID", "Instructor_ID", "Classroom_ID", "TERM",
        "CLASS_START_TIME", "CLASS_END_TIME", "COMPONENT", "MEETING_DAY",
        "SECTION_CODE", "ENROLLMENT_CAPACITY", "WAITLIST_CAPACITY", "STATUS", "WAITLIST_ACTUAL", "ENROLLMENT_ACTUAL"
    ]]
    course_section_df.to_sql("Course_Section", conn, if_exists="append", index=False)

    # --- Course_Prerequisite Table ---
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
