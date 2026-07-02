using ADHD.Application.Commands.ParentCommands;
using ADHD.Application.Queries.ParentQueries;
using ADHD.Application.Responses;
using ADHD.Application.DTOs;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using MediatR;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.ParentHandlers
{
    public class ParentCommandHandler : 
        IRequestHandler<CreateParentCommand, Response<string>>,
        IRequestHandler<DeleteParentCommand, Response<string>>
    {
        private readonly IRepository<Parent> _parentRepository;
        private readonly IRepository<Child> _childRepository;
        private readonly ResponseHandler _responseHandler;

        public ParentCommandHandler(
            IRepository<Parent> parentRepository, 
            IRepository<Child> childRepository,
            ResponseHandler responseHandler)
        {
            _parentRepository = parentRepository;
            _childRepository = childRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<string>> Handle(CreateParentCommand request, CancellationToken cancellationToken)
        {
            var parent = new Parent
            {
                UserName = request.Email,
                Email = request.Email,
                PhoneNumber = request.PhoneNumber
            };

            await _parentRepository.AddAsync(parent);
            return _responseHandler.Success("Parent created successfully");
        }

        public async Task<Response<string>> Handle(DeleteParentCommand request, CancellationToken cancellationToken)
        {
            var parent = await _parentRepository.GetByIdAsync(request.Id);
            if (parent == null)
            {
                return _responseHandler.NotFound<string>("Parent not found");
            }

            // Fetch and delete all children associated with this parent
            var children = await _childRepository.FindAsync(c => c.ParentId == parent.Id);
            foreach (var child in children)
            {
                _childRepository.Remove(child);
            }

            // Delete the parent
            _parentRepository.Remove(parent);

            return _responseHandler.Success("Parent and all associated children deleted successfully");
        }
    }

    public class ParentQueryHandler : 
        IRequestHandler<GetParentListQuery, Response<IEnumerable<ParentDto>>>,
        IRequestHandler<GetParentByIdQuery, Response<ParentDto>>
    {
        private readonly IRepository<Parent> _parentRepository;
        private readonly ResponseHandler _responseHandler;

        public ParentQueryHandler(IRepository<Parent> parentRepository, ResponseHandler responseHandler)
        {
            _parentRepository = parentRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<IEnumerable<ParentDto>>> Handle(GetParentListQuery request, CancellationToken cancellationToken)
        {
            var parents = await _parentRepository.GetAllAsync();
            var dtos = parents.Select(p => new ParentDto
            {
                Id = p.Id,
                UserName = p.UserName,
                Email = p.Email,
                PhoneNumber = p.PhoneNumber,
                ImageUrl = p.ImageUrl
            }).ToList();
            return _responseHandler.Success<IEnumerable<ParentDto>>(dtos);
        }

        public async Task<Response<ParentDto>> Handle(GetParentByIdQuery request, CancellationToken cancellationToken)
        {
            var parent = await _parentRepository.GetByIdAsync(request.Id);
            if (parent == null)
            {
                return _responseHandler.NotFound<ParentDto>("Parent not found");
            }
            var dto = new ParentDto
            {
                Id = parent.Id,
                UserName = parent.UserName,
                Email = parent.Email,
                PhoneNumber = parent.PhoneNumber,
                ImageUrl = parent.ImageUrl
            };
            return _responseHandler.Success(dto);
        }
    }
}
