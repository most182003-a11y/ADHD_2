using ADHD.Application.Interfaces.Auth;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using ADHD.Infrastructure.Auth;
using ADHD.Infrastructure.Data;
using ADHD.Infrastructure.Repositories;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Localization;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using System.Globalization;
using System.Text;

namespace ADHD.Infrastructure.DI
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddDbContext<AppDbContext>(options =>
                options.UseSqlServer(configuration.GetConnectionString("DefaultConnection")));

            services.AddIdentity<AppUser, IdentityRole>(options =>
            {
                options.User.AllowedUserNameCharacters = ""; // Allow all characters (Arabic, spaces, etc.) in username
            })
                .AddEntityFrameworkStores<AppDbContext>()
                .AddDefaultTokenProviders();

            // Bind JWT Configuration Options
            services.Configure<JwtOptions>(configuration.GetSection("Jwt"));

            // Register IJwtProvider Implementation
            services.AddScoped<IJwtProvider, JwtProvider>();

            // Configure JWT Authentication
            var jwtSecret = configuration["Jwt:Secret"] ?? "ADHD_Progress_Insights_Super_Secure_Encryption_Key_2026_Must_Be_Long!";
            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            })
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = configuration["Jwt:Issuer"],
                    ValidAudience = configuration["Jwt:Audience"],
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
                };
            });

            services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
            services.AddScoped<ADHD.Application.Interfaces.IEmailService, ADHD.Infrastructure.Services.EmailService>();
            services.AddHttpClient<ADHD.Application.Interfaces.IAnalysisService, ADHD.Infrastructure.Services.HuggingFaceAnalysisService>();

            ConfigureLocalizationOptions(services);

            return services;
        }

        public static void UseSharedCulture(this IApplicationBuilder app)
        {
            app.Use(async (context, next) =>
            {
                var culture = context.Request.Query["culture"];
                if (!string.IsNullOrWhiteSpace(culture))
                {
                    CultureInfo cultureInfo = new CultureInfo(culture!);
                    CultureInfo.CurrentCulture = cultureInfo;
                    CultureInfo.CurrentUICulture = cultureInfo;
                }
                await next();
            });
        }

        private static void ConfigureLocalizationOptions(IServiceCollection services)
        {
            services.AddLocalization(options => options.ResourcesPath = "");

            services.Configure<RequestLocalizationOptions>(options =>
            {
                var supportedCultures = new[]
                {
                    new CultureInfo("en-US"),
                    new CultureInfo("ar-EG"),
                 };

                options.DefaultRequestCulture = new RequestCulture("en-US");
                options.SupportedCultures = supportedCultures;
                options.SupportedUICultures = supportedCultures;
            });
        }
    }
}
