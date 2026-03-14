CREATE TABLE IF NOT EXISTS measurements(
"date time" TEXT PRIMARY KEY NOT NULL,
temperature REAL             NOT NULL,
pressure    REAL             NOT NULL,
humidity    REAL             NOT NULL,
light       REAL             NOT NULL,
aqi         REAL             NOT NULL,
tvoc        REAL             NOT NULL,
eco2        REAL             NOT NULL,
mode        TEXT             NOT NULL
);