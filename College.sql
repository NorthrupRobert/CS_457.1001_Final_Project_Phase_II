PRAGMA foreign_keys = 'on';

BEGIN TRANSACTION;

-- Table: Building
CREATE TABLE IF NOT EXISTS Building (
    BLDG_ID TEXT PRIMARY KEY,
    NAME_BLDG    TEXT NOT NULL
);

-- Table: Classroom
CREATE TABLE IF NOT EXISTS Classroom (
    Bldg_ID      TEXT NOT NULL REFERENCES Building (BLDG_ID) ON DELETE CASCADE,
    Room_Num     TEXT NOT NULL,
    Floor        INTEGER NOT NULL,
    Seats        INTEGER NOT NULL,
    WiFi         TEXT DEFAULT 'No',
    ADA_Access   TEXT DEFAULT 'No',
    PRIMARY KEY (Bldg_ID, Room_Num)
);

-- Table: Course
CREATE TABLE IF NOT EXISTS Course (
    Course_ID   TEXT PRIMARY KEY,
    Title       TEXT NOT NULL,
    Description TEXT,
    No_Credits  INTEGER NOT NULL,
    Department  TEXT,           -- Added for Department/Subject Section
    Subject     TEXT            -- Added for Department/Subject Section
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
    Bldg_ID             TEXT NOT NULL,
    Room_Num            TEXT NOT NULL,
    Term                TEXT NOT NULL,
    College             TEXT,                -- Added for College Section
    Component           TEXT,                -- Added for Component (Lab/Lec/etc.)
    Meeting_Day         TEXT NOT NULL,
    CLASS_START_TIME    TEXT,                -- Added for CLASS_START_TIME
    CLASS_END_TIME      TEXT,                -- Added for CLASS_END_TIME
    Meeting_Time        TEXT NOT NULL,
    Section_Code        TEXT NOT NULL,
    Enrollment_Capacity INTEGER NOT NULL,
    Waitlist_Capacity   INTEGER NOT NULL,
    Status              TEXT DEFAULT 'Open',
    Waitlist_Actual     INTEGER DEFAULT 0,
    Enrollment_Actual   INTEGER DEFAULT 0,
    FOREIGN KEY (Bldg_ID, Room_Num) REFERENCES Classroom (Bldg_ID, Room_Num) ON DELETE SET NULL
);

-- Table: Instructor
CREATE TABLE IF NOT EXISTS Instructor (
    Instructor_ID TEXT PRIMARY KEY,
    FIRST_NAME    TEXT,                  -- Added
    LAST_NAME     TEXT,                  -- Added
    NAME_INST     TEXT                   -- Renamed from NAME for clarity
);

COMMIT TRANSACTION;
