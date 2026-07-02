using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.AuthCommands
{
    public class LoginCommand : IRequest<Response<ADHD.Application.DTOs.LoginResponseDto>>
    {
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }
}
