using ADHD.Domain.Entities;
using System.Collections.Generic;

namespace ADHD.Application.Interfaces.Auth
{
    public interface IJwtProvider
    {
        string GenerateToken(AppUser user, IList<string> roles);
        string GenerateRefreshToken();
        System.Security.Claims.ClaimsPrincipal? GetPrincipalFromExpiredToken(string token);
    }
}
