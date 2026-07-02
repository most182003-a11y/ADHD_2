using ADHD.Application.Resources;
using Microsoft.Extensions.Localization;
using System.Net;

namespace ADHD.Application.Responses
{
    public class ResponseHandler
    {
        public readonly IStringLocalizer<SharedResource> _localizer;
        public ResponseHandler(IStringLocalizer<SharedResource> localizer)
        {
            _localizer = localizer;
        }

        public Response<T> Deleted<T>()
        {
            return new Response<T>()
            {
                StatusCode = HttpStatusCode.OK,
                Succeeded = true,
                Message = _localizer[SharedResourceKeys.DeletedSuccessfully]
            };
        }
        public Response<T> Success<T>(T entity, object? Meta = null)
        {
            return new Response<T>()
            {
                Data = entity,
                StatusCode = HttpStatusCode.OK,
                Succeeded = true,
                Message = _localizer[SharedResourceKeys.MessageSuccess],
                Meta = Meta
            };
        }

        public Response<T> Unauthorized<T>(string message)
        {
            return new Response<T>()
            {
                StatusCode = HttpStatusCode.Unauthorized,
                Succeeded = true,
                Message = _localizer[SharedResourceKeys.UnAuthorized]
            };
        }
        public Response<T> BadRequest<T>(string? Message = null)
        {
            return new Response<T>()
            {
                StatusCode = HttpStatusCode.BadRequest,
                Succeeded = false,
                Message = Message == null ? _localizer[SharedResourceKeys.NotExist] : Message
            };
        }

        public Response<T> NotFound<T>(string? message = null)
        {
            return new Response<T>()
            {
                StatusCode = HttpStatusCode.NotFound,
                Succeeded = false,
                Message = message == null ? _localizer[SharedResourceKeys.ThisItemNotFound] : message
            };
        }
        public Response<T> Forbidden<T>(string? message = null)
        {
            return new Response<T>()
            {
                StatusCode = HttpStatusCode.Forbidden,
                Succeeded = false,
                Message = message ?? _localizer[SharedResourceKeys.AccessDenied]
            };
        }

        public Response<T> Created<T>(T entity, object? Meta = null)
        {
            return new Response<T>()
            {
                Data = entity,
                StatusCode = HttpStatusCode.Created,
                Succeeded = true,
                Message = _localizer[SharedResourceKeys.MessageSuccess],
                Meta = Meta
            };
        }
    }
}
