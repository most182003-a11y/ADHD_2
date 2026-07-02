using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace ADHD.API.Middlewares
{
    public class ExceptionHandlingMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<ExceptionHandlingMiddleware> _logger;

        public ExceptionHandlingMiddleware(RequestDelegate next, ILogger<ExceptionHandlingMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                await _next(context);
                if (context.Response.StatusCode == StatusCodes.Status429TooManyRequests)
                {
                    _logger.LogWarning("Too many requests detected. Sending custom response.");
                    await HandleTooManyRequestsAsync(context);
                }
                if (context.Response.StatusCode == StatusCodes.Status401Unauthorized)
                {
                    _logger.LogWarning("Unauthorized");
                    await HandleUnauthorizedAsync(context);
                }
                if (context.Response.StatusCode == StatusCodes.Status403Forbidden)
                {
                    _logger.LogWarning("Forbidden");
                    await HandleForbiddenAsync(context);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unhandled exception occurred.");
                await HandleExceptionAsync(context, ex);
            }
        }
        private static Task HandleCustomResponseAsync(HttpContext context, int statusCode, string title, string detail)
        {
            var response = new ProblemDetails
            {
                Status = statusCode,
                Title = title,
                Detail = detail
            };

            context.Response.ContentType = "application/json";
            context.Response.StatusCode = statusCode;

            return context.Response.WriteAsync(JsonSerializer.Serialize(response));

        }
        private static async Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            await HandleCustomResponseAsync(context, StatusCodes.Status500InternalServerError,
                "An unexpected error occurred. Please try again later.", exception.Message);
        }
        private static async Task HandleTooManyRequestsAsync(HttpContext context)
        {
            await HandleCustomResponseAsync(context, StatusCodes.Status429TooManyRequests, "Too Many Requests",
                "Too many requests. Please slow down and try again later.");
        }
        private static async Task HandleUnauthorizedAsync(HttpContext context)
        {
            await HandleCustomResponseAsync(context, StatusCodes.Status401Unauthorized, "Unauthorized",
                "You are not authorized to access this resource.");
        }
        private static async Task HandleForbiddenAsync(HttpContext context)
        {
            await HandleCustomResponseAsync(context, StatusCodes.Status403Forbidden, "Forbidden",
                "You do not have permission to access this resource.");
        }

    }

    public static class MiddlewareExtensions
    {
        public static IApplicationBuilder UseMethodNotAllowedHandler(this IApplicationBuilder app)
        {
            return app.Use(async (context, next) =>
            {
                await next.Invoke();

                if (context.Response.StatusCode == StatusCodes.Status405MethodNotAllowed)
                {
                    context.Response.ContentType = "application/json";
                    await context.Response.WriteAsync("{\"message\": \"This method is not supported for this route\"}");
                }
            });
        }
    }
    public static class UseExecptionMidllerware
    {
        public static void UseExceptionHandlingMiddleware(this IApplicationBuilder app)
        {
            app.UseMethodNotAllowedHandler();
            app.UseMiddleware<ExceptionHandlingMiddleware>();
        }
    }
}
