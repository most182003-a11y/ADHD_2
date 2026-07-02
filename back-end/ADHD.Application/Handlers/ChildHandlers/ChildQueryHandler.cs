using ADHD.Application.Queries.ChildQueries;
using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using MediatR;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.ChildHandlers
{
    public class ChildQueryHandler : IRequestHandler<GetChildListQuery, Response<IEnumerable<Child>>>
    {
        private readonly IRepository<Child> _childRepository;
        private readonly ResponseHandler _responseHandler;

        public ChildQueryHandler(IRepository<Child> childRepository, ResponseHandler responseHandler)
        {
            _childRepository = childRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<IEnumerable<Child>>> Handle(GetChildListQuery request, CancellationToken cancellationToken)
        {
            IEnumerable<Child> children;
            if (!string.IsNullOrEmpty(request.ParentId))
            {
                children = await _childRepository.FindAsync(c => c.ParentId == request.ParentId);
            }
            else
            {
                children = await _childRepository.GetAllAsync();
            }
            return _responseHandler.Success(children);
        }
    }
}
