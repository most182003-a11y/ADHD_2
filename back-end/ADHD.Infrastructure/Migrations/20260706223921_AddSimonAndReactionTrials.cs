using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSimonAndReactionTrials : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<double>(
                name: "AttentionScore",
                table: "session_summaries",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "EndStatus",
                table: "session_summaries",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "FalseStarts",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "FinalLevel",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "Hits",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "ImpulsiveErrors",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<double>(
                name: "ImpulsivityScore",
                table: "session_summaries",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "Misses",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "PrematurePressesDuringShow",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<double>(
                name: "ReactionTimeStdDevMs",
                table: "session_summaries",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TotalCorrectSteps",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "TotalSteps",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "WrongButtons",
                table: "session_summaries",
                type: "int",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "reaction_trials",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Trial = table.Column<int>(type: "int", nullable: false),
                    TargetLED = table.Column<int>(type: "int", nullable: false),
                    Delay = table.Column<double>(type: "float", nullable: false),
                    Result = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PressedButton = table.Column<int>(type: "int", nullable: false),
                    ReactionTimeMs = table.Column<double>(type: "float", nullable: true),
                    Correct = table.Column<bool>(type: "bit", nullable: false),
                    ImpulsiveError = table.Column<bool>(type: "bit", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_reaction_trials", x => x.Id);
                    table.ForeignKey(
                        name: "FK_reaction_trials_game_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "game_sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "simon_trials",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Level = table.Column<int>(type: "int", nullable: false),
                    SequenceLength = table.Column<int>(type: "int", nullable: false),
                    Speed = table.Column<double>(type: "float", nullable: false),
                    Step = table.Column<int>(type: "int", nullable: false),
                    Expected = table.Column<int>(type: "int", nullable: false),
                    Pressed = table.Column<int>(type: "int", nullable: false),
                    Correct = table.Column<bool>(type: "bit", nullable: false),
                    ReactionTimeMs = table.Column<double>(type: "float", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_simon_trials", x => x.Id);
                    table.ForeignKey(
                        name: "FK_simon_trials_game_sessions_SessionId",
                        column: x => x.SessionId,
                        principalTable: "game_sessions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_reaction_trials_SessionId",
                table: "reaction_trials",
                column: "SessionId");

            migrationBuilder.CreateIndex(
                name: "IX_simon_trials_SessionId",
                table: "simon_trials",
                column: "SessionId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "reaction_trials");

            migrationBuilder.DropTable(
                name: "simon_trials");

            migrationBuilder.DropColumn(
                name: "AttentionScore",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "EndStatus",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "FalseStarts",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "FinalLevel",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "Hits",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "ImpulsiveErrors",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "ImpulsivityScore",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "Misses",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "PrematurePressesDuringShow",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "ReactionTimeStdDevMs",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "TotalCorrectSteps",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "TotalSteps",
                table: "session_summaries");

            migrationBuilder.DropColumn(
                name: "WrongButtons",
                table: "session_summaries");
        }
    }
}
