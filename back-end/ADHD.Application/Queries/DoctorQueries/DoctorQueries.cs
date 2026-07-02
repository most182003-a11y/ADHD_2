using ADHD.Application.Responses;
using ADHD.Application.DTOs;
using MediatR;
using System.Collections.Generic;

namespace ADHD.Application.Queries.DoctorQueries
{
    public class GetDoctorListQuery : IRequest<Response<IEnumerable<DoctorDto>>>
    {
    }

    public class GetDoctorByIdQuery : IRequest<Response<DoctorDto>>
    {
        public string Id { get; set; } = string.Empty;
    }
}
