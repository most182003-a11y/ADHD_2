using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddUserSpecializations : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<string>(
                name: "ParentId",
                table: "children",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "DoctorId",
                table: "children",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldNullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Discriminator",
                table: "AspNetUsers",
                type: "nvarchar(8)",
                maxLength: 8,
                nullable: false,
                defaultValue: "");

            migrationBuilder.CreateIndex(
                name: "IX_children_DoctorId",
                table: "children",
                column: "DoctorId");

            migrationBuilder.CreateIndex(
                name: "IX_children_ParentId",
                table: "children",
                column: "ParentId");

            migrationBuilder.AddForeignKey(
                name: "FK_children_AspNetUsers_DoctorId",
                table: "children",
                column: "DoctorId",
                principalTable: "AspNetUsers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_children_AspNetUsers_ParentId",
                table: "children",
                column: "ParentId",
                principalTable: "AspNetUsers",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_children_AspNetUsers_DoctorId",
                table: "children");

            migrationBuilder.DropForeignKey(
                name: "FK_children_AspNetUsers_ParentId",
                table: "children");

            migrationBuilder.DropIndex(
                name: "IX_children_DoctorId",
                table: "children");

            migrationBuilder.DropIndex(
                name: "IX_children_ParentId",
                table: "children");

            migrationBuilder.DropColumn(
                name: "Discriminator",
                table: "AspNetUsers");

            migrationBuilder.AlterColumn<string>(
                name: "ParentId",
                table: "children",
                type: "nvarchar(max)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "DoctorId",
                table: "children",
                type: "nvarchar(max)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);
        }
    }
}
