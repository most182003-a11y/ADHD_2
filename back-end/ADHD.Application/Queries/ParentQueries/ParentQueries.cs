using ADHD.Application.Responses;
using ADHD.Application.DTOs;
using MediatR;
using System.Collections.Generic;

namespace ADHD.Application.Queries.ParentQueries
{
    public class GetParentListQuery : IRequest<Response<IEnumerable<ParentDto>>>
    {
    }

    public class GetParentByIdQuery : IRequest<Response<ParentDto>>
    {
        public string Id { get; set; } = string.Empty;
    }
}
