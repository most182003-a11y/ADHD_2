using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.DoctorCommands
{
    public class CreateDoctorCommand : IRequest<Response<string>>
    {
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string? PhoneNumber { get; set; }
        public string? Specialization { get; set; }
    }
}
