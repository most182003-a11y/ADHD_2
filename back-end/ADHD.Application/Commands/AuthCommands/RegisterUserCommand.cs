using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.AuthCommands
{
    public class RegisterUserCommand : IRequest<Response<string>>
    {
        public string UserName { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
        public string Role { get; set; } = "Parent"; // Default to Parent
        public string? PhoneNumber { get; set; }
        public string? Specialization { get; set; }
    }
}
