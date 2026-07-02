using ADHD.Application.Commands.ChildCommands;
using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.ChildHandlers
{
    public class ChildCommandHandler : 
        IRequestHandler<CreateChildCommand, Response<string>>,
        IRequestHandler<UpdateChildCommand, Response<string>>
    {
        private readonly IRepository<Child> _childRepository;
        private readonly ResponseHandler _responseHandler;

        public ChildCommandHandler(IRepository<Child> childRepository, ResponseHandler responseHandler)
        {
            _childRepository = childRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<string>> Handle(CreateChildCommand request, CancellationToken cancellationToken)
        {
            var child = new Child
            {
                Name = request.Name,
                Age = request.Age,
                Gender = request.Gender,
                DiagnosisSeverity = request.DiagnosisSeverity,
                Status = request.Status,
                AvatarInitials = request.AvatarInitials,
                RegisteredDate = DateTime.UtcNow,
                DoctorId = request.DoctorId,
                ParentId = request.ParentId
            };

            await _childRepository.AddAsync(child);
            return _responseHandler.Success("Child created successfully");
        }

        public async Task<Response<string>> Handle(UpdateChildCommand request, CancellationToken cancellationToken)
        {
            var child = await _childRepository.GetByIdAsync(request.Id);
            if (child == null)
            {
                return _responseHandler.NotFound<string>("Child not found");
            }

            // Update details
            child.Name = request.Name;
            child.Age = request.Age;
            child.Gender = request.Gender;
            child.DiagnosisSeverity = request.DiagnosisSeverity;
            child.Status = request.Status;
            child.DoctorId = request.DoctorId;
            child.ParentId = request.ParentId;

            _childRepository.Update(child);
            return _responseHandler.Success("Child updated successfully");
        }
    }
}
