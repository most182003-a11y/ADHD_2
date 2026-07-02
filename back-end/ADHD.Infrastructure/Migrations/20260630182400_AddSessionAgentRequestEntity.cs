using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSessionAgentRequestEntity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "session_agent_requests",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GameType = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Timestamp = table.Column<DateTime>(type: "datetime2", nullable: false),
                    PreviousSessionsCount = table.Column<int>(type: "int", nullable: false),
                    TrialsJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    SessionSummaryJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    RawRequestJson = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
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

            migrationBuilder.CreateIndex(
                name: "IX_session_agent_requests_ChildId",
                table: "session_agent_requests",
                column: "ChildId");

            migrationBuilder.CreateIndex(
                name: "IX_session_agent_requests_SessionId",
                table: "session_agent_requests",
                column: "SessionId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "session_agent_requests");
        }
    }
}
