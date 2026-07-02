using ADHD.Application.Commands.AdminCommands;
using ADHD.Application.Queries.AdminQueries;
using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using MediatR;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.AdminHandlers
{
    public class AdminCommandHandler : IRequestHandler<CreateAdminCommand, Response<string>>
    {
        private readonly IRepository<Admin> _adminRepository;
        private readonly ResponseHandler _responseHandler;

        public AdminCommandHandler(IRepository<Admin> adminRepository, ResponseHandler responseHandler)
        {
            _adminRepository = adminRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<string>> Handle(CreateAdminCommand request, CancellationToken cancellationToken)
        {
            var admin = new Admin
            {
                UserName = request.Email,
                Email = request.Email
            };

            await _adminRepository.AddAsync(admin);
            return _responseHandler.Success("Admin created successfully");
        }
    }

    public class AdminQueryHandler : 
        IRequestHandler<GetAdminListQuery, Response<IEnumerable<Admin>>>,
        IRequestHandler<GetAdminByIdQuery, Response<Admin>>
    {
        private readonly IRepository<Admin> _adminRepository;
        private readonly ResponseHandler _responseHandler;

        public AdminQueryHandler(IRepository<Admin> adminRepository, ResponseHandler responseHandler)
        {
            _adminRepository = adminRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<IEnumerable<Admin>>> Handle(GetAdminListQuery request, CancellationToken cancellationToken)
        {
            var admins = await _adminRepository.GetAllAsync();
            return _responseHandler.Success(admins);
        }

        public async Task<Response<Admin>> Handle(GetAdminByIdQuery request, CancellationToken cancellationToken)
        {
            var admin = await _adminRepository.GetByIdAsync(request.Id);
            return admin != null ? _responseHandler.Success(admin) : _responseHandler.NotFound<Admin>("Admin not found");
        }
    }
}
