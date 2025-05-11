PRAGMA foreign_keys = 'off';

BEGIN TRANSACTION;-- Table: Building

CREATE TABLE IF NOT EXISTS Building (
    BLDG_ID TEXT PRIMARY KEY,
    NAME    TEXT
);-- Table: Classroom

CREATE TABLE IF NOT EXISTS Classroom (
    Classroom_ID TEXT    PRIMARY KEY,
    Bldg_ID      TEXT    REFERENCES Building (BLDG_ID),
    Room_Num     TEXT,
    Floor        INTEGER,
    Seats        INTEGER,
    WiFi         TEXT,
    ADA_Access   TEXT
);-- Table: Course

CREATE TABLE IF NOT EXISTS Course (
    Course_ID   TEXT    PRIMARY KEY,
    Title       TEXT,
    Description TEXT,
    No_Credits  INTEGER
);-- Table: Course_Prerequisite

CREATE TABLE IF NOT EXISTS Course_Prerequisite (
    Course_ID         TEXT REFERENCES Course (Course_ID),
    Pre_Req_Course_ID TEXT REFERENCES Course (Course_ID),
    PRIMARY KEY (
        Course_ID,
        Pre_Req_Course_ID
    )
);-- Table: Course_Section

CREATE TABLE IF NOT EXISTS Course_Section (
    Section_ID          TEXT    PRIMARY KEY,
    Course_ID           TEXT    REFERENCES Course (Course_ID),
    Instructor_ID       TEXT    REFERENCES Instructor (Instructor_ID),
    Classroom_ID        TEXT    REFERENCES Classroom (Classroom_ID),
    Term                TEXT,
    Meeting_Day         TEXT,
    Meeting_Time        TEXT,
    Section_Code        TEXT,
    Enrollment_Capacity INTEGER,
    Waitlist_Capacity   INTEGER,
    Status              TEXT,
    Waitlist_Actual     INTEGER,
    Enrollment_Actual   INTEGER
);-- Table: Instructor

CREATE TABLE IF NOT EXISTS Instructor (
    Instructor_ID TEXT PRIMARY KEY,
    Name          TEXT
);

COMMIT TRANSACTION ; 

PRAGMA foreign_keys = 'on';
