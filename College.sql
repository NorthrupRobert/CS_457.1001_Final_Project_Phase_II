PRAGMA foreign_keys = 'on';

BEGIN TRANSACTION;

-- Table: Building
CREATE TABLE IF NOT EXISTS Building (
    BLDG_ID TEXT PRIMARY KEY,
    NAME    TEXT NOT NULL
);

-- Table: Classroom
CREATE TABLE IF NOT EXISTS Classroom (
    Classroom_ID TEXT PRIMARY KEY,
    Bldg_ID      TEXT NOT NULL REFERENCES Building (BLDG_ID) ON DELETE CASCADE,
    Room_Num     TEXT NOT NULL,
    Floor        INTEGER NOT NULL,
    Seats        INTEGER NOT NULL,
    WiFi         TEXT DEFAULT 'No',
    ADA_Access   TEXT DEFAULT 'No'
);

-- Table: Course
CREATE TABLE IF NOT EXISTS Course (
    Course_ID   TEXT PRIMARY KEY,
    Title       TEXT NOT NULL,
    Description TEXT,
    No_Credits  INTEGER NOT NULL
);

-- Table: Course_Prerequisite
CREATE TABLE IF NOT EXISTS Course_Prerequisite (
    Course_ID         TEXT NOT NULL REFERENCES Course (Course_ID) ON DELETE CASCADE,
    Pre_Req_Course_ID TEXT NOT NULL REFERENCES Course (Course_ID) ON DELETE CASCADE,
    PRIMARY KEY (Course_ID, Pre_Req_Course_ID)
);

-- Table: Course_Section
CREATE TABLE IF NOT EXISTS Course_Section (
    Section_ID          TEXT PRIMARY KEY,
    Course_ID           TEXT NOT NULL REFERENCES Course (Course_ID) ON DELETE CASCADE,
    Instructor_ID       TEXT NOT NULL REFERENCES Instructor (Instructor_ID) ON DELETE SET NULL,
    Classroom_ID        TEXT NOT NULL REFERENCES Classroom (Classroom_ID) ON DELETE SET NULL,
    Term                TEXT NOT NULL,
    Meeting_Day         TEXT NOT NULL,
    Meeting_Time        TEXT NOT NULL,
    Section_Code        TEXT NOT NULL,
    Enrollment_Capacity INTEGER NOT NULL,
    Waitlist_Capacity   INTEGER NOT NULL,
    Status              TEXT DEFAULT 'Open',
    Waitlist_Actual     INTEGER DEFAULT 0,
    Enrollment_Actual   INTEGER DEFAULT 0
);

-- Table: Instructor
CREATE TABLE IF NOT EXISTS Instructor (
    Instructor_ID TEXT PRIMARY KEY,
    Name          TEXT NOT NULL
);

COMMIT TRANSACTION;
