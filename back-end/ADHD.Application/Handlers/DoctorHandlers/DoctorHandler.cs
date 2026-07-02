using ADHD.Application.Commands.DoctorCommands;
using ADHD.Application.Queries.DoctorQueries;
using ADHD.Application.Responses;
using ADHD.Application.DTOs;
using ADHD.Domain.Entities;
using ADHD.Domain.Repositories;
using MediatR;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.DoctorHandlers
{
    public class DoctorCommandHandler : 
        IRequestHandler<CreateDoctorCommand, Response<string>>,
        IRequestHandler<DeleteDoctorCommand, Response<string>>
    {
        private readonly IRepository<Doctor> _doctorRepository;
        private readonly IRepository<Child> _childRepository;
        private readonly ResponseHandler _responseHandler;

        public DoctorCommandHandler(
            IRepository<Doctor> doctorRepository, 
            IRepository<Child> childRepository,
            ResponseHandler responseHandler)
        {
            _doctorRepository = doctorRepository;
            _childRepository = childRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<string>> Handle(CreateDoctorCommand request, CancellationToken cancellationToken)
        {
            var doctor = new Doctor
            {
                UserName = request.Email,
                Email = request.Email,
                PhoneNumber = request.PhoneNumber,
                Specialization = request.Specialization
            };

            await _doctorRepository.AddAsync(doctor);
            return _responseHandler.Success("Doctor created successfully");
        }

        public async Task<Response<string>> Handle(DeleteDoctorCommand request, CancellationToken cancellationToken)
        {
            var doctor = await _doctorRepository.GetByIdAsync(request.Id);
            if (doctor == null)
            {
                return _responseHandler.NotFound<string>("Doctor not found");
            }

            // Find all active doctors except the one being deleted
            var allDoctors = await _doctorRepository.GetAllAsync();
            var alternativeDoctor = allDoctors.FirstOrDefault(d => d.Id != doctor.Id);

            // Fetch children assigned to the doctor being deleted
            var children = await _childRepository.FindAsync(c => c.DoctorId == doctor.Id);
            foreach (var child in children)
            {
                child.DoctorId = alternativeDoctor?.Id; // Reassign to first available doctor, or null if none
                _childRepository.Update(child);
            }

            // Delete the doctor
            _doctorRepository.Remove(doctor);

            return _responseHandler.Success("Doctor deleted and patients reassigned successfully");
        }
    }

    public class DoctorQueryHandler : 
        IRequestHandler<GetDoctorListQuery, Response<IEnumerable<DoctorDto>>>,
        IRequestHandler<GetDoctorByIdQuery, Response<DoctorDto>>
    {
        private readonly IRepository<Doctor> _doctorRepository;
        private readonly ResponseHandler _responseHandler;

        public DoctorQueryHandler(IRepository<Doctor> doctorRepository, ResponseHandler responseHandler)
        {
            _doctorRepository = doctorRepository;
            _responseHandler = responseHandler;
        }

        public async Task<Response<IEnumerable<DoctorDto>>> Handle(GetDoctorListQuery request, CancellationToken cancellationToken)
        {
            var doctors = await _doctorRepository.GetAllAsync();
            var dtos = doctors.Select(d => new DoctorDto
            {
                Id = d.Id,
                UserName = d.UserName,
                Email = d.Email,
                PhoneNumber = d.PhoneNumber,
                ImageUrl = d.ImageUrl,
                Specialization = d.Specialization
            }).ToList();
            return _responseHandler.Success<IEnumerable<DoctorDto>>(dtos);
        }

        public async Task<Response<DoctorDto>> Handle(GetDoctorByIdQuery request, CancellationToken cancellationToken)
        {
            var doctor = await _doctorRepository.GetByIdAsync(request.Id);
            if (doctor == null)
            {
                return _responseHandler.NotFound<DoctorDto>("Doctor not found");
            }
            var dto = new DoctorDto
            {
                Id = doctor.Id,
                UserName = doctor.UserName,
                Email = doctor.Email,
                PhoneNumber = doctor.PhoneNumber,
                ImageUrl = doctor.ImageUrl,
                Specialization = doctor.Specialization
            };
            return _responseHandler.Success(dto);
        }
    }
}
