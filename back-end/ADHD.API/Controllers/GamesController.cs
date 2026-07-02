using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class GamesController : ControllerBase
    {
        [HttpGet]
        [AllowAnonymous]
        public IActionResult GetGameTypes()
        {
            var games = new[]
            {
                new { id = "mirror_me", name = "Mirror Me" },
                new { id = "green_light", name = "Green Light" }
            };

            return Ok(new { succeeded = true, data = games });
        }
    }
}
