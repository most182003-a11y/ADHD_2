using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using MediatR;
using System.Collections.Generic;

namespace ADHD.Application.Queries.AdminQueries
{
    public class GetAdminListQuery : IRequest<Response<IEnumerable<Admin>>>
    {
    }

    public class GetAdminByIdQuery : IRequest<Response<Admin>>
    {
        public string Id { get; set; } = string.Empty;
    }
}
