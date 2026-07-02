using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.AuthCommands
{
    public class RefreshTokenCommand : IRequest<Response<ADHD.Application.DTOs.LoginResponseDto>>
    {
        public string AccessToken { get; set; } = string.Empty;
        public string RefreshToken { get; set; } = string.Empty;
    }
}
