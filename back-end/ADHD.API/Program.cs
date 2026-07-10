using ADHD.Infrastructure.DI;
using ADHD.API.Middlewares;
using Microsoft.Extensions.Options;
using ADHD.Application.DI;
using Microsoft.AspNetCore.Identity;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });
builder.Services.AddApplicationDI();
builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
//builder.Services.AddOpenApi();

var app = builder.Build();

app.UseSharedCulture();
app.UseExceptionHandlingMiddleware();

app.UseRequestLocalization(app.Services.GetRequiredService<IOptions<RequestLocalizationOptions>>().Value);

// Configure the HTTP request pipeline.
//if (app.Environment.IsDevelopment())
//{
//    app.MapOpenApi();
//}

 
    app.UseSwagger();
    app.UseSwaggerUI();
 

app.UseCors(policy => policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());

app.UseHttpsRedirection();

app.UseAuthentication();

app.UseAuthorization();

// Seed default roles and admin account if they do not exist
using (var scope = app.Services.CreateScope())
{
    var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
    var userManager = scope.ServiceProvider.GetRequiredService<UserManager<ADHD.Domain.Entities.AppUser>>();
    
    var roles = new[] { "Admin", "Doctor", "Parent" };
    foreach (var role in roles)
    {
        if (!roleManager.RoleExistsAsync(role).GetAwaiter().GetResult())
        {
            roleManager.CreateAsync(new IdentityRole(role)).GetAwaiter().GetResult();
        }
    }

    // Seed default Admin user
    var adminEmail = "admin@adhd.com";
    var existingUser = userManager.FindByEmailAsync(adminEmail).GetAwaiter().GetResult();
    if (existingUser != null && existingUser.GetType() != typeof(ADHD.Domain.Entities.Admin))
    {
        userManager.DeleteAsync(existingUser).GetAwaiter().GetResult();
        existingUser = null;
    }

    if (existingUser == null)
    {
        var adminUser = new ADHD.Domain.Entities.Admin
        {
            UserName = adminEmail,
            Email = adminEmail,
            EmailConfirmed = true
        };
        var result = userManager.CreateAsync(adminUser, "admin@123").GetAwaiter().GetResult();
        if (result.Succeeded)
        {
            userManager.AddToRoleAsync(adminUser, "Admin").GetAwaiter().GetResult();
        }
    }

}

app.MapControllers();

app.Run();
