using ADHD.Application.Commands.DoctorCommands;
using ADHD.Application.Queries.DoctorQueries;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class DoctorsController : ControllerBase
    {
        private readonly IMediator _mediator;

        public DoctorsController(IMediator mediator)
        {
            _mediator = mediator;
        }


        [HttpGet]
        [Authorize(Roles = "Admin,Doctor")]
        public async Task<IActionResult> GetAllDoctors()
        {
            var query = new GetDoctorListQuery();
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpGet("{id}")]
        [Authorize(Roles = "Admin,Doctor")]
        public async Task<IActionResult> GetDoctorById(string id)
        {
            var query = new GetDoctorByIdQuery { Id = id };
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : NotFound(result);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> DeleteDoctor(string id)
        {
            var command = new DeleteDoctorCommand { Id = id };
            var result = await _mediator.Send(command);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }
    }
}
