using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.DoctorCommands
{
    public class DeleteDoctorCommand : IRequest<Response<string>>
    {
        public string Id { get; set; } = string.Empty;
    }
}
