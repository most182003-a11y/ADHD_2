using ADHD.Application.Responses;
using ADHD.Domain.Enums;
using MediatR;

namespace ADHD.Application.Commands.ChildCommands
{
    public class CreateChildCommand : IRequest<Response<string>>
    {
        public string Name { get; set; } = string.Empty;
        public int Age { get; set; }
        public Gender Gender { get; set; }
        public DiagnosisSeverity DiagnosisSeverity { get; set; }
        public ChildStatus Status { get; set; } = ChildStatus.Stable;
        public string AvatarInitials { get; set; } = string.Empty;
        public string? DoctorId { get; set; }
        public string? ParentId { get; set; }
    }
}
