using ADHD.Application.Commands.ParentCommands;
using ADHD.Application.Queries.ParentQueries;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class ParentsController : ControllerBase
    {
        private readonly IMediator _mediator;

        public ParentsController(IMediator mediator)
        {
            _mediator = mediator;
        }


        [HttpGet]
        [Authorize(Roles = "Admin,Doctor")]
        public async Task<IActionResult> GetAllParents()
        {
            var query = new GetParentListQuery();
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }

        [HttpGet("{id}")]
        [Authorize(Roles = "Admin,Doctor")]
        public async Task<IActionResult> GetParentById(string id)
        {
            var query = new GetParentByIdQuery { Id = id };
            var result = await _mediator.Send(query);
            return result.Succeeded == true ? Ok(result) : NotFound(result);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public async Task<IActionResult> DeleteParent(string id)
        {
            var command = new DeleteParentCommand { Id = id };
            var result = await _mediator.Send(command);
            return result.Succeeded == true ? Ok(result) : BadRequest(result);
        }
    }
}
