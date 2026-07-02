using ADHD.Application.Commands.ChildCommands;
using ADHD.Application.Queries.ChildQueries;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class ChildrenController : ControllerBase
    {
        private readonly IMediator _mediator;

        public ChildrenController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost]
        [AllowAnonymous]
        public async Task<IActionResult> CreateChild([FromBody] CreateChildCommand command)
        {
            var result = await _mediator.Send(command);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpGet]
        [AllowAnonymous]
        public async Task<IActionResult> GetAllChildren([FromQuery] string? parentId)
        {
            if (User.IsInRole("Parent") && string.IsNullOrEmpty(parentId))
            {
                return Forbid();
            }

            var query = new GetChildListQuery { ParentId = parentId };
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Admin,Doctor")]
        public async Task<IActionResult> UpdateChild(string id, [FromBody] UpdateChildCommand command)
        {
            command.Id = id;
            var result = await _mediator.Send(command);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }
    }
}
