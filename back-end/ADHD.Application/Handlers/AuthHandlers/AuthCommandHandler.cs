using ADHD.Application.Commands.AuthCommands;
using ADHD.Application.Interfaces.Auth;
using ADHD.Application.Responses;
using ADHD.Domain.Entities;
using MediatR;
using Microsoft.AspNetCore.Identity;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Handlers.AuthHandlers
{
    public class AuthCommandHandler : 
        IRequestHandler<RegisterUserCommand, Response<string>>,
        IRequestHandler<LoginCommand, Response<ADHD.Application.DTOs.LoginResponseDto>>,
        IRequestHandler<RefreshTokenCommand, Response<ADHD.Application.DTOs.LoginResponseDto>>
    {
        private readonly UserManager<AppUser> _userManager;
        private readonly SignInManager<AppUser> _signInManager;
        private readonly ResponseHandler _responseHandler;
        private readonly IJwtProvider _jwtProvider;

        public AuthCommandHandler(
            UserManager<AppUser> userManager, 
            SignInManager<AppUser> signInManager, 
            ResponseHandler responseHandler,
            IJwtProvider jwtProvider)
        {
            _userManager = userManager;
            _signInManager = signInManager;
            _responseHandler = responseHandler;
            _jwtProvider = jwtProvider;
        }

        public async Task<Response<string>> Handle(RegisterUserCommand request, CancellationToken cancellationToken)
        {
            if ((request.Role == "Doctor" || request.Role == "Parent") && string.IsNullOrWhiteSpace(request.PhoneNumber))
            {
                return new Response<string>("رقم الهاتف مطلوب لتسجيل هذا الحساب.", false);
            }

            AppUser user;
            
            if (request.Role == "Doctor")
            {
                user = new Doctor
                {
                    UserName = request.UserName,
                    Email = request.Email,
                    PhoneNumber = request.PhoneNumber,
                    Specialization = request.Specialization
                };
            }
            else if (request.Role == "Parent")
            {
                user = new Parent
                {
                    UserName = request.UserName,
                    Email = request.Email,
                    PhoneNumber = request.PhoneNumber
                };
            }
            else if (request.Role == "Admin")
            {
                user = new Admin
                {
                    UserName = request.UserName,
                    Email = request.Email,
                    PhoneNumber = request.PhoneNumber
                };
            }
            else
            {
                user = new AppUser
                {
                    UserName = request.UserName,
                    Email = request.Email,
                    PhoneNumber = request.PhoneNumber
                };
            }

            var result = await _userManager.CreateAsync(user, request.Password);

            if (!result.Succeeded)
            {
                return new Response<string>("Registration failed", false)
                {
                    Errors = result.Errors.Select(e => e.Description).ToList()
                };
            }

            if (!string.IsNullOrEmpty(request.Role))
            {
                await _userManager.AddToRoleAsync(user, request.Role);
            }

            return _responseHandler.Success("User registered successfully");
        }

        public async Task<Response<ADHD.Application.DTOs.LoginResponseDto>> Handle(LoginCommand request, CancellationToken cancellationToken)
        {
            var user = await _userManager.FindByEmailAsync(request.Email);
            if (user == null)
            {
                return _responseHandler.BadRequest<ADHD.Application.DTOs.LoginResponseDto>("Invalid email or password");
            }

            var result = await _signInManager.PasswordSignInAsync(user, request.Password, false, false);

            if (!result.Succeeded)
            {
                return _responseHandler.BadRequest<ADHD.Application.DTOs.LoginResponseDto>("Invalid email or password");
            }

            var roles = await _userManager.GetRolesAsync(user);
            var role = roles.FirstOrDefault() ?? "Parent";

            // Generate JWT Token
            var token = _jwtProvider.GenerateToken(user, roles);

            // Generate Refresh Token
            var refreshToken = _jwtProvider.GenerateRefreshToken();
            user.RefreshToken = refreshToken;
            user.RefreshTokenExpiryTime = DateTime.UtcNow.AddDays(7);
            await _userManager.UpdateAsync(user);

            var responseDto = new ADHD.Application.DTOs.LoginResponseDto
            {
                Message = "Login successful",
                Role = role,
                Token = token,
                Expiration = DateTime.UtcNow.AddMinutes(180),
                RefreshToken = refreshToken,
                RefreshTokenExpiration = user.RefreshTokenExpiryTime.Value
            };

            return _responseHandler.Success(responseDto);
        }

        public async Task<Response<ADHD.Application.DTOs.LoginResponseDto>> Handle(RefreshTokenCommand request, CancellationToken cancellationToken)
        {
            var principal = _jwtProvider.GetPrincipalFromExpiredToken(request.AccessToken);
            if (principal == null)
            {
                return _responseHandler.BadRequest<ADHD.Application.DTOs.LoginResponseDto>("رمز الجلسة غير صالح.");
            }

            var email = principal.FindFirst(System.Security.Claims.ClaimTypes.Email)?.Value 
                        ?? principal.FindFirst("email")?.Value
                        ?? principal.Identity?.Name;

            if (string.IsNullOrEmpty(email))
            {
                return _responseHandler.BadRequest<ADHD.Application.DTOs.LoginResponseDto>("رمز الجلسة لا يحتوي على معلومات المستخدم.");
            }

            var user = await _userManager.FindByEmailAsync(email) ?? await _userManager.FindByNameAsync(email);
            if (user == null || user.RefreshToken != request.RefreshToken || user.RefreshTokenExpiryTime <= System.DateTime.UtcNow)
            {
                return _responseHandler.BadRequest<ADHD.Application.DTOs.LoginResponseDto>("انتهت صلاحية الجلسة، يرجى تسجيل الدخول مرة أخرى.");
            }

            var roles = await _userManager.GetRolesAsync(user);
            var role = roles.FirstOrDefault() ?? "Parent";

            var newAccessToken = _jwtProvider.GenerateToken(user, roles);
            var newRefreshToken = _jwtProvider.GenerateRefreshToken();

            user.RefreshToken = newRefreshToken;
            user.RefreshTokenExpiryTime = System.DateTime.UtcNow.AddDays(7);
            await _userManager.UpdateAsync(user);

            var responseDto = new ADHD.Application.DTOs.LoginResponseDto
            {
                Message = "تم تجديد الجلسة بنجاح",
                Role = role,
                Token = newAccessToken,
                Expiration = System.DateTime.UtcNow.AddMinutes(180),
                RefreshToken = newRefreshToken,
                RefreshTokenExpiration = user.RefreshTokenExpiryTime.Value
            };

            return _responseHandler.Success(responseDto);
        }
    }
}
