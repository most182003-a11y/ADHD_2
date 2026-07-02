using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSessionAnalysisEntity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "session_analyses",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    SessionId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChildId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    AnalysisDate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    AttentionScore = table.Column<double>(type: "float", nullable: true),
                    ImpulsivityScore = table.Column<double>(type: "float", nullable: true),
                    MotorControlScore = table.Column<double>(type: "float", nullable: true),
                    AttentionChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ImpulsivityChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    MotorControlChange = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    SummaryText = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RecommendationsJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RawRequestJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    RawResponseJson = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    ModelUsed = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsSuccessful = table.Column<bool>(type: "bit", nullable: false),
                    ErrorMessage = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    CreatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    UpdatedBy = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: true)
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
                name: "IX_session_analyses_ChildId",
                table: "session_analyses",
                column: "ChildId");

            migrationBuilder.CreateIndex(
                name: "IX_session_analyses_SessionId",
                table: "session_analyses",
                column: "SessionId",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "session_analyses");
        }
    }
}
