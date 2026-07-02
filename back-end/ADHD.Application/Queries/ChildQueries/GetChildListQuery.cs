using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using MediatR;
using System.Collections.Generic;

namespace ADHD.Application.Queries.ChildQueries
{
    public class GetChildListQuery : IRequest<Response<IEnumerable<Child>>>
    {
        public string? ParentId { get; set; }
    }
}
