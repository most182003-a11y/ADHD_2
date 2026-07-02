using ADHD.Application.Commands.AdminCommands;
using ADHD.Application.Queries.AdminQueries;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize(Roles = "Admin")]
    public class AdminsController : ControllerBase
    {
        private readonly IMediator _mediator;

        public AdminsController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost]
        public async Task<IActionResult> CreateAdmin([FromBody] CreateAdminCommand command)
        {
            var result = await _mediator.Send(command);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpGet]
        public async Task<IActionResult> GetAllAdmins()
        {
            var query = new GetAdminListQuery();
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetAdminById(string id)
        {
            var query = new GetAdminByIdQuery { Id = id };
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : NotFound(result);
        }
    }
}
