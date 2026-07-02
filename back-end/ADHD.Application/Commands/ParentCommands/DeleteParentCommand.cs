using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.ParentCommands
{
    public class DeleteParentCommand : IRequest<Response<string>>
    {
        public string Id { get; set; } = string.Empty;
    }
}
