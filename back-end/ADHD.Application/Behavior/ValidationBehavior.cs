using ADHD.Application.Responses;
using FluentValidation;
using MediatR;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ADHD.Application.Behavior
{
    public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
         where TRequest : IRequest<TResponse>
    {
        private readonly IEnumerable<IValidator<TRequest>> _validators;

        public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        {
            _validators = validators;
        }

        public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
        {
            if (_validators.Any())
            {
                var context = new ValidationContext<TRequest>(request);
                var validationResults = await Task.WhenAll(_validators.Select(v => v.ValidateAsync(context, cancellationToken)));
                var failures = validationResults.SelectMany(r => r.Errors).Where(f => f != null).ToList();

                if (failures.Count != 0)
                {
                    var responseType = typeof(TResponse);
                    if (responseType.IsGenericType && responseType.GetGenericTypeDefinition() == typeof(Response<>))
                    {
                        var responseInstance = (TResponse)Activator.CreateInstance(responseType)!;
                        var responseProperty = responseType.GetProperty("Errors");
                        responseProperty?.SetValue(responseInstance, failures.Select(e => e.ErrorMessage).ToList());
                        
                        var succeededProperty = responseType.GetProperty("Succeeded");
                        succeededProperty?.SetValue(responseInstance, false);

                        return responseInstance;
                    }

                    throw new ValidationException(failures);
                }
            }

            return await next();
        }
    }
}
