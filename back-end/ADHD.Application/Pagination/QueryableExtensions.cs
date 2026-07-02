using System;
using System.Collections.Generic;
using System.Linq;

namespace ADHD.Application.Pagination
{
    public static class QueryableExtensions
    {
        public static PaginatedResult<T> ToPaginatedList<T>(this IEnumerable<T> source, int pageNumber, int pageSize)
       where T : class
        {
            if (source == null)
            {
                throw new Exception("Empty");
            }

            pageNumber = pageNumber == 0 ? 1 : pageNumber;
            pageSize = pageSize == 0 ? 10 : pageSize;

            int count = source.Count();
            if (count == 0)
            {
                return PaginatedResult<T>.Success(new List<T>(), count, pageNumber, pageSize);
            }

            pageNumber = pageNumber <= 0 ? 1 : pageNumber;
            var items = source.Skip((pageNumber - 1) * pageSize).Take(pageSize).ToList();

            return PaginatedResult<T>.Success(items, count, pageNumber, pageSize);
        }
    }
}
