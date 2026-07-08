/* ==============   ================================================
   ADHD_DB � fake data seeder (FIXED)
   Populates: children, game_sessions, session_summaries,
              simon_trials, reaction_trials, mirror_me_trials,
              green_light_trials

   FIXES APPLIED:
   1. GameType assignment for game_sessions no longer uses an
      uncorrelated CROSS APPLY ... ORDER BY NEWID() (which was
      collapsing to a single value, 'ReactionTime', for every
      session). It now uses an inline CASE on ABS(CHECKSUM(NEWID())) % 4
      computed per row, guaranteeing a real per-row random pick.
   2. The final summary now counts rows created by THIS run only
      (joined against #Sessions), instead of filtering the
      permanent tables by CreatedBy = 'seed-script', which was
      showing lifetime totals across every past run.

   ASSUMPTIONS (check these before running):
   - All Id columns are UNIQUEIDENTIFIER with a default (e.g. NEWID())
   - At least one row already exists in Parents and in Doctors
   - CreatedBy / UpdatedBy are nvarchar, IsDeleted is bit

   Run the whole batch at once (F5). Safe to re-run; it only adds
   new rows, it never deletes anything.
   ============================================================== */

SET NOCOUNT ON;

------------------------------------------------------------
-- 1. CONFIG � tweak these to control how much data you get
------------------------------------------------------------
DECLARE @NumChildren      INT = 15;   -- fake children to create
DECLARE @SessionsPerChild INT = 4;    -- game sessions per child
DECLARE @TrialsPerSession INT = 10;   -- trial rows per session

------------------------------------------------------------
-- 2. A disposable "numbers" table to drive row generation
------------------------------------------------------------
IF OBJECT_ID('tempdb..#Numbers') IS NOT NULL DROP TABLE #Numbers;
SELECT TOP (2000) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
INTO #Numbers
FROM sys.all_objects a CROSS JOIN sys.all_objects b;

------------------------------------------------------------
-- 3. Fake children
------------------------------------------------------------
IF OBJECT_ID('tempdb..#Children') IS NOT NULL DROP TABLE #Children;
CREATE TABLE #Children (RowNum INT IDENTITY(1,1), ChildId UNIQUEIDENTIFIER);

IF NOT EXISTS (SELECT 1 FROM Parents)
BEGIN
    RAISERROR('No rows found in Parents � insert at least one Parent first.', 16, 1);
    RETURN;
END
IF NOT EXISTS (SELECT 1 FROM Doctors)
BEGIN
    RAISERROR('No rows found in Doctors � insert at least one Doctor first.', 16, 1);
    RETURN;
END

;WITH FirstNames AS (
    SELECT v FROM (VALUES ('Liam'),('Olivia'),('Noah'),('Emma'),('Ali'),('Sara'),
        ('Omar'),('Layla'),('Yusuf'),('Mona'),('Karim'),('Nour'),('Adam'),('Hana'),('Zain')) t(v)
),
LastNames AS (
    SELECT v FROM (VALUES ('Hassan'),('Ibrahim'),('Ali'),('Mostafa'),('Said'),
        ('Fahmy'),('Khalil'),('Nasser'),('Adel'),('Sami')) t(v)
)
INSERT INTO children
    (  Id,  Name, Age, Gender, DiagnosisSeverity, RegisteredDate, Status, AvatarInitials,
     DoctorId, ParentId, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
OUTPUT inserted.Id INTO #Children(ChildId)
SELECT 
  NEWID(),       
    fn.v + ' ' + ln.v,
    6 + ABS(CHECKSUM(NEWID())) % 11,                                   -- age 6-16
    CASE WHEN ABS(CHECKSUM(NEWID())) % 2 = 0 THEN 'Male' ELSE 'Female' END,
    sev.v,
    DATEADD(DAY, -(ABS(CHECKSUM(NEWID())) % 500), SYSUTCDATETIME()),
    st.v,
    LEFT(fn.v,1) + LEFT(ln.v,1),
    doc.Id,
    par.Id,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Numbers num
CROSS APPLY (SELECT TOP 1 v FROM FirstNames ORDER BY NEWID()) fn
CROSS APPLY (SELECT TOP 1 v FROM LastNames  ORDER BY NEWID()) ln
CROSS APPLY (SELECT TOP 1 v FROM (VALUES('Mild'),('Moderate'),('Severe')) s(v) ORDER BY NEWID()) sev
CROSS APPLY (SELECT TOP 1 v FROM (VALUES('Active'),('Inactive'),('Pending')) s(v) ORDER BY NEWID()) st
CROSS APPLY (SELECT TOP 1 Id FROM Doctors ORDER BY NEWID()) doc(Id)
CROSS APPLY (SELECT TOP 1 Id FROM Parents ORDER BY NEWID()) par(Id)
WHERE num.n <= @NumChildren;

------------------------------------------------------------
-- 4. Fake game sessions (one per game type per child, x N rounds)
--    FIX: GameType now picked inline per row via CASE on
--    ABS(CHECKSUM(NEWID())) % 4, instead of an uncorrelated
--    CROSS APPLY ... ORDER BY NEWID() which was always
--    resolving to the same value for every row.
------------------------------------------------------------
IF OBJECT_ID('tempdb..#Sessions') IS NOT NULL DROP TABLE #Sessions;
CREATE TABLE #Sessions (RowNum INT IDENTITY(1,1), SessionId UNIQUEIDENTIFIER, GameType NVARCHAR(50));

INSERT INTO game_sessions
    (Id, ChildId, GameType, SessionNumber, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
OUTPUT inserted.Id, inserted.GameType INTO #Sessions(SessionId, GameType)
SELECT
    NEWID(),
    c.ChildId,
    CASE ABS(CHECKSUM(NEWID())) % 4
        WHEN 0 THEN 'MirrorMe'
        WHEN 1 THEN 'GreenLight'
        WHEN 2 THEN 'Simon'
        ELSE 'ReactionTime'
    END,
    s.n,
    DATEADD(DAY, -(ABS(CHECKSUM(NEWID())) % 200), SYSUTCDATETIME()),
    SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Children c
CROSS JOIN #Numbers s
WHERE s.n <= @SessionsPerChild;

------------------------------------------------------------
-- 5. Fake session_summaries (one per session)
------------------------------------------------------------
INSERT INTO session_summaries (
    id,SessionId, TotalTrials, AverageReactionTimeMs, AverageSimilarity, TotalFidgetScore, AttentionOverall,
    AverageStopReactionTimeMs, FalseStartCount, AverageFreezeQuality, MovementIntensityOverall,
    CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted,
    AttentionScore, EndStatus, FalseStarts, FinalLevel, Hits, ImpulsiveErrors, ImpulsivityScore,
    Misses, PrematurePressesDuringShow, ReactionTimeStdDevMs, TotalCorrectSteps, TotalSteps, WrongButtons
)
SELECT
  NEWID(),  
    ses.SessionId,
    @TrialsPerSession,
    300 + ABS(CHECKSUM(NEWID())) % 700,
    CASE WHEN ses.GameType = 'MirrorMe'  THEN 40 + ABS(CHECKSUM(NEWID())) % 60 ELSE NULL END,
    CASE WHEN ses.GameType = 'MirrorMe'  THEN ABS(CHECKSUM(NEWID())) % 50 ELSE NULL END,
    30 + ABS(CHECKSUM(NEWID())) % 70,
    CASE WHEN ses.GameType = 'GreenLight' THEN 300 + ABS(CHECKSUM(NEWID())) % 500 ELSE NULL END,
    CASE WHEN ses.GameType = 'GreenLight' THEN ABS(CHECKSUM(NEWID())) % 4 ELSE NULL END,
    CASE WHEN ses.GameType = 'GreenLight' THEN 40 + ABS(CHECKSUM(NEWID())) % 60 ELSE NULL END,
    CASE WHEN ses.GameType = 'GreenLight' THEN ABS(CHECKSUM(NEWID())) % 100 ELSE NULL END,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0,
    40 + ABS(CHECKSUM(NEWID())) % 60,
    'Completed',
    ABS(CHECKSUM(NEWID())) % 4,
    CASE WHEN ses.GameType = 'Simon' THEN 1 + ABS(CHECKSUM(NEWID())) % 10 ELSE NULL END,
    5 + ABS(CHECKSUM(NEWID())) % 6,
    ABS(CHECKSUM(NEWID())) % 4,
    30 + ABS(CHECKSUM(NEWID())) % 70,
    ABS(CHECKSUM(NEWID())) % 4,
    ABS(CHECKSUM(NEWID())) % 3,
    50 + ABS(CHECKSUM(NEWID())) % 200,
    CASE WHEN ses.GameType = 'Simon' THEN 5 + ABS(CHECKSUM(NEWID())) % 20 ELSE NULL END,
    CASE WHEN ses.GameType = 'Simon' THEN 10 + ABS(CHECKSUM(NEWID())) % 20 ELSE NULL END,
    ABS(CHECKSUM(NEWID())) % 4
FROM #Sessions ses;

------------------------------------------------------------
-- 6. Fake trials, one table per game type
------------------------------------------------------------

-- Simon
INSERT INTO simon_trials
    (id,SessionId, Level, SequenceLength, Speed, Step, Expected, Pressed, Correct, ReactionTimeMs,
     CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
SELECT
NEWID(),
    ses.SessionId,
    1 + ((num.n - 1) / 3),
    3 + ((num.n - 1) / 3),
    500 + ABS(CHECKSUM(NEWID())) % 500,
    num.n,
    ABS(CHECKSUM(NEWID())) % 4,
    ABS(CHECKSUM(NEWID())) % 4,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 8 THEN 1 ELSE 0 END,
    300 + ABS(CHECKSUM(NEWID())) % 700,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Sessions ses
CROSS JOIN #Numbers num
WHERE ses.GameType = 'Simon' AND num.n <= @TrialsPerSession;

-- Reaction time
INSERT INTO reaction_trials
    (id,SessionId, Trial, TargetLED, Delay, Result, PressedButton, ReactionTimeMs, Correct, ImpulsiveError,
     CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
SELECT
  NEWID(),  
    ses.SessionId,
    num.n,
    1 + ABS(CHECKSUM(NEWID())) % 4,
    500 + ABS(CHECKSUM(NEWID())) % 1500,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 8 THEN 'Hit' ELSE 'Miss' END,
    1 + ABS(CHECKSUM(NEWID())) % 4,
    250 + ABS(CHECKSUM(NEWID())) % 750,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 8 THEN 1 ELSE 0 END,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 2 THEN 1 ELSE 0 END,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Sessions ses
CROSS JOIN #Numbers num
WHERE ses.GameType = 'ReactionTime' AND num.n <= @TrialsPerSession;

-- Mirror me
INSERT INTO mirror_me_trials
    (Id, SessionId, TrialIndex, TargetPoseId, ReactionTimeMs, PoseSimilarity, HoldingDurationMs,
     FidgetScore, PrematureMovement, AttentionPercent, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
SELECT
    NEWID(),
    ses.SessionId,
    num.n,
    1 + ABS(CHECKSUM(NEWID())) % 10,
    400 + ABS(CHECKSUM(NEWID())) % 1000,
    40 + ABS(CHECKSUM(NEWID())) % 60,
    1000 + ABS(CHECKSUM(NEWID())) % 3000,
    ABS(CHECKSUM(NEWID())) % 20,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 2 THEN 1 ELSE 0 END,
    30 + ABS(CHECKSUM(NEWID())) % 70,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Sessions ses
CROSS JOIN #Numbers num
WHERE ses.GameType = 'MirrorMe' AND num.n <= @TrialsPerSession;

-- Green light / stop-signal
INSERT INTO green_light_trials
    (Id, SessionId, TrialIndex, Phase, StopSignalDelayMs, MovementIntensity, StopReactionTimeMs,
     FreezeQuality, FalseStart, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy, IsDeleted)
SELECT
    NEWID(),
    ses.SessionId,
    num.n,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 2 = 0 THEN 'Go' ELSE 'Stop' END,
    200 + ABS(CHECKSUM(NEWID())) % 800,
    ABS(CHECKSUM(NEWID())) % 100,
    250 + ABS(CHECKSUM(NEWID())) % 750,
    40 + ABS(CHECKSUM(NEWID())) % 60,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 10 < 2 THEN 1 ELSE 0 END,
    SYSUTCDATETIME(), SYSUTCDATETIME(), 'seed-script', 'seed-script', 0
FROM #Sessions ses
CROSS JOIN #Numbers num
WHERE ses.GameType = 'GreenLight' AND num.n <= @TrialsPerSession;

------------------------------------------------------------
-- 7. Summary of what was inserted
--    FIX: all counts now scoped to THIS run via #Sessions,
--    instead of filtering the permanent tables by
--    CreatedBy = 'seed-script' (which summed every past run).
------------------------------------------------------------
SELECT 'children'         AS TableName, COUNT(*) AS RowsInserted FROM #Children
UNION ALL SELECT 'game_sessions',        COUNT(*) FROM #Sessions
UNION ALL SELECT 'session_summaries',    COUNT(*) FROM session_summaries ss
                                          JOIN #Sessions ses ON ses.SessionId = ss.SessionId
UNION ALL SELECT 'simon_trials',         COUNT(*) FROM simon_trials st
                                          JOIN #Sessions ses ON ses.SessionId = st.SessionId
UNION ALL SELECT 'reaction_trials',      COUNT(*) FROM reaction_trials rt
                                          JOIN #Sessions ses ON ses.SessionId = rt.SessionId
UNION ALL SELECT 'mirror_me_trials',     COUNT(*) FROM mirror_me_trials mt
                                          JOIN #Sessions ses ON ses.SessionId = mt.SessionId
UNION ALL SELECT 'green_light_trials',   COUNT(*) FROM green_light_trials gt
                                          JOIN #Sessions ses ON ses.SessionId = gt.SessionId;

DROP TABLE #Numbers;
DROP TABLE #Children;
DROP TABLE #Sessions;