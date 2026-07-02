using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class NewGameSessionModel : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[child_progress_snapshots]', N'U') IS NOT NULL DROP TABLE [dbo].[child_progress_snapshots]");
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[session_agent_requests]', N'U') IS NOT NULL DROP TABLE [dbo].[session_agent_requests]");
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[session_analyses]', N'U') IS NOT NULL DROP TABLE [dbo].[session_analyses]");
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[sessions]', N'U') IS NOT NULL DROP TABLE [dbo].[sessions]");
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[games]', N'U') IS NOT NULL DROP TABLE [dbo].[games]");
            migrationBuilder.Sql("IF OBJECT_ID(N'[dbo].[game_categories]', N'U') IS NOT NULL DROP TABLE [dbo].[game_categories]");

            migrationBuilder.CreateTable(
                name: "game_sessions",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GameType = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionNumber = table.Column<int>(type: "int", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_game_sessions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_game_sessions_children_ChildId",
                        column: x => x.ChildId,
                        principalTable: "children",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "green_light_trials",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    TrialIndex = table.Column<int>(type: "int", nullable: false),
                    Phase = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    StopSignalDelayMs = table.Column<int>(type: "int", nullable: true),
                    MovementIntensity = table.Column<double>(type: "float", nullable: true),
                    StopReactionTimeMs = table.Column<int>(type: "int", nullable: true),
                    FreezeQuality = table.Column<double>(type: "float", nullable: true),
                    FalseStart = table.Column<bool>(type: "bit", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_green_light_trials", x => x.Id);
                    table.ForeignKey(
                        name: "FK_green_light_trials_game_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "game_sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "mirror_me_trials",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    TrialIndex = table.Column<int>(type: "int", nullable: false),
                    TargetPoseId = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ReactionTimeMs = table.Column<int>(type: "int", nullable: false),
                    PoseSimilarity = table.Column<double>(type: "float", nullable: false),
                    HoldingDurationMs = table.Column<int>(type: "int", nullable: false),
                    FidgetScore = table.Column<double>(type: "float", nullable: false),
                    PrematureMovement = table.Column<bool>(type: "bit", nullable: false),
                    AttentionPercent = table.Column<double>(type: "float", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mirror_me_trials", x => x.Id);
                    table.ForeignKey(
                        name: "FK_mirror_me_trials_game_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "game_sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "session_summaries",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    TotalTrials = table.Column<int>(type: "int", nullable: false),
                    AverageReactionTimeMs = table.Column<double>(type: "float", nullable: true),
                    AverageSimilarity = table.Column<double>(type: "float", nullable: true),
                    TotalFidgetScore = table.Column<double>(type: "float", nullable: true),
                    AttentionOverall = table.Column<double>(type: "float", nullable: true),
                    AverageStopReactionTimeMs = table.Column<double>(type: "float", nullable: true),
                    FalseStartCount = table.Column<int>(type: "int", nullable: true),
                    AverageFreezeQuality = table.Column<double>(type: "float", nullable: true),
                    MovementIntensityOverall = table.Column<double>(type: "float", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_session_summaries", x => x.Id);
                    table.ForeignKey(
                        name: "FK_session_summaries_game_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "game_sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_game_sessions_ChildId_GameType",
                table: "game_sessions",
                columns: new[] { "ChildId", "GameType" });

            migrationBuilder.CreateIndex(
                name: "IX_green_light_trials_SessionId",
                table: "green_light_trials",
                column: "SessionId");

            migrationBuilder.CreateIndex(
                name: "IX_mirror_me_trials_SessionId",
                table: "mirror_me_trials",
                column: "SessionId");

            migrationBuilder.CreateIndex(
                name: "IX_session_summaries_SessionId",
                table: "session_summaries",
                column: "SessionId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "green_light_trials");

            migrationBuilder.DropTable(
                name: "mirror_me_trials");

            migrationBuilder.DropTable(
                name: "session_summaries");

            migrationBuilder.DropTable(
                name: "game_sessions");

            migrationBuilder.CreateTable(
                name: "game_categories",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Code = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    NameAr = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    NameEn = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_game_categories", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "child_progress_snapshots",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GameCategoryId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    AvgDistractionScore = table.Column<double>(type: "float", nullable: true),
                    AvgImpulsivityIndex = table.Column<double>(type: "float", nullable: true),
                    AvgMotorControlScore = table.Column<double>(type: "float", nullable: true),
                    AvgPlayerScore = table.Column<double>(type: "float", nullable: false),
                    AvgReactionTime = table.Column<double>(type: "float", nullable: true),
                    AvgSuccessRate = table.Column<double>(type: "float", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    GeneratedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    OverallTrend = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PeriodStart = table.Column<DateTime>(type: "datetime2", nullable: false),
                    TotalSessions = table.Column<int>(type: "int", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_child_progress_snapshots", x => x.Id);
                    table.ForeignKey(
                        name: "FK_child_progress_snapshots_children_ChildId",
                        column: x => x.ChildId,
                        principalTable: "children",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_child_progress_snapshots_game_categories_GameCategoryId",
                        column: x => x.GameCategoryId,
                        principalTable: "game_categories",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "games",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GameCategoryId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    RelevantMetrics = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_games", x => x.Id);
                    table.ForeignKey(
                        name: "FK_games_game_categories_GameCategoryId",
                        column: x => x.GameCategoryId,
                        principalTable: "game_categories",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "sessions",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GameId = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    AvgReactionTime = table.Column<double>(type: "float", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    DifficultyLevel = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    DistractionScore = table.Column<double>(type: "float", nullable: true),
                    DurationMinutes = table.Column<int>(type: "int", nullable: false),
                    FalseMoves = table.Column<int>(type: "int", nullable: true),
                    FalseStops = table.Column<int>(type: "int", nullable: true),
                    ImpulsivityIndex = table.Column<double>(type: "float", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    MaxConsecutiveSuccess = table.Column<int>(type: "int", nullable: false),
                    MotorControlScore = table.Column<double>(type: "float", nullable: true),
                    PlayerScore = table.Column<double>(type: "float", nullable: false),
                    SessionNumber = table.Column<int>(type: "int", nullable: false),
                    StartTime = table.Column<DateTime>(type: "datetime2", nullable: false),
                    SuccessRate = table.Column<double>(type: "float", nullable: false),
                    TotalTrials = table.Column<int>(type: "int", nullable: false),
                    Trend = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_sessions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_sessions_children_ChildId",
                        column: x => x.ChildId,
                        principalTable: "children",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_sessions_games_GameId",
                        column: x => x.GameId,
                        principalTable: "games",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "session_agent_requests",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    GameType = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    PreviousSessionsCount = table.Column<int>(type: "int", nullable: false),
                    RawRequestJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    SessionSummaryJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Timestamp = table.Column<DateTime>(type: "datetime2", nullable: false),
                    TrialsJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_session_agent_requests", x => x.Id);
                    table.ForeignKey(
                        name: "FK_session_agent_requests_children_ChildId",
                        column: x => x.ChildId,
                        principalTable: "children",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_session_agent_requests_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "session_analyses",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    AnalysisDate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    AttentionChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    AttentionScore = table.Column<double>(type: "float", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ErrorMessage = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImpulsivityChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImpulsivityScore = table.Column<double>(type: "float", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true),
                    IsSuccessful = table.Column<bool>(type: "bit", nullable: false),
                    ModelUsed = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    MotorControlChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    MotorControlScore = table.Column<double>(type: "float", nullable: true),
                    RawRequestJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RawResponseJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RecommendationsJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    SummaryText = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_session_analyses", x => x.Id);
                    table.ForeignKey(
                        name: "FK_session_analyses_children_ChildId",
                        column: x => x.ChildId,
                        principalTable: "children",
                        principalColumn: "Id");
                    table.ForeignKey(
                        name: "FK_session_analyses_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_child_progress_snapshots_ChildId_GameCategoryId_PeriodStart",
                table: "child_progress_snapshots",
                columns: new[] { "ChildId", "GameCategoryId", "PeriodStart" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_child_progress_snapshots_GameCategoryId",
                table: "child_progress_snapshots",
                column: "GameCategoryId");

            migrationBuilder.CreateIndex(
                name: "IX_game_categories_Code",
                table: "game_categories",
                column: "Code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_games_GameCategoryId",
                table: "games",
                column: "GameCategoryId");

            migrationBuilder.CreateIndex(
                name: "IX_session_agent_requests_ChildId",
                table: "session_agent_requests",
                column: "ChildId");

            migrationBuilder.CreateIndex(
                name: "IX_session_agent_requests_SessionId",
                table: "session_agent_requests",
                column: "SessionId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_session_analyses_ChildId",
                table: "session_analyses",
                column: "ChildId");

            migrationBuilder.CreateIndex(
                name: "IX_session_analyses_SessionId",
                table: "session_analyses",
                column: "SessionId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_sessions_ChildId_SessionNumber",
                table: "sessions",
                columns: new[] { "ChildId", "SessionNumber" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_sessions_GameId",
                table: "sessions",
                column: "GameId");
        }
    }
}
