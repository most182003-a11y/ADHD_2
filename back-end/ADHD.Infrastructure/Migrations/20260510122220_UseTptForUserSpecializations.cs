using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ADHD.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class UseTptForUserSpecializations : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_children_AspNetUsers_DoctorId",
                table: "children");

            migrationBuilder.DropForeignKey(
                name: "FK_children_AspNetUsers_ParentId",
                table: "children");

            migrationBuilder.CreateTable(
                name: "Admins",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Admins", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Admins_AspNetUsers_Id",
                        column: x => x.Id,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Doctors",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Doctors", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Doctors_AspNetUsers_Id",
                        column: x => x.Id,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Parents",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Parents", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Parents_AspNetUsers_Id",
                        column: x => x.Id,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.Sql("""
                INSERT INTO [Admins] ([Id])
                SELECT [Id]
                FROM [AspNetUsers]
                WHERE [Discriminator] = 'Admin'
                """);

            migrationBuilder.Sql("""
                INSERT INTO [Doctors] ([Id])
                SELECT [Id]
                FROM [AspNetUsers]
                WHERE [Discriminator] = 'Doctor'
                """);

            migrationBuilder.Sql("""
                INSERT INTO [Parents] ([Id])
                SELECT [Id]
                FROM [AspNetUsers]
                WHERE [Discriminator] = 'Parent'
                """);

            migrationBuilder.DropColumn(
                name: "Discriminator",
                table: "AspNetUsers");

            migrationBuilder.AddForeignKey(
                name: "FK_children_Doctors_DoctorId",
                table: "children",
                column: "DoctorId",
                principalTable: "Doctors",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_children_Parents_ParentId",
                table: "children",
                column: "ParentId",
                principalTable: "Parents",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_children_Doctors_DoctorId",
                table: "children");

            migrationBuilder.DropForeignKey(
                name: "FK_children_Parents_ParentId",
                table: "children");

            migrationBuilder.DropTable(
                name: "Admins");

            migrationBuilder.DropTable(
                name: "Doctors");

            migrationBuilder.DropTable(
                name: "Parents");

            migrationBuilder.AddColumn<string>(
                name: "Discriminator",
                table: "AspNetUsers",
                type: "nvarchar(8)",
                maxLength: 8,
                nullable: false,
                defaultValue: "");

            migrationBuilder.Sql("""
                UPDATE [AspNetUsers]
                SET [Discriminator] = 'AppUser'
                """);

            migrationBuilder.Sql("""
                UPDATE u
                SET u.[Discriminator] = 'Admin'
                FROM [AspNetUsers] u
                INNER JOIN [Admins] a ON a.[Id] = u.[Id]
                """);

            migrationBuilder.Sql("""
                UPDATE u
                SET u.[Discriminator] = 'Doctor'
                FROM [AspNetUsers] u
                INNER JOIN [Doctors] d ON d.[Id] = u.[Id]
                """);

            migrationBuilder.Sql("""
                UPDATE u
                SET u.[Discriminator] = 'Parent'
                FROM [AspNetUsers] u
                INNER JOIN [Parents] p ON p.[Id] = u.[Id]
                """);

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
    }
}
