namespace ADHD.Application.DTOs
{
    public class DoctorDto
    {
        public string Id { get; set; } = string.Empty;
        public string? UserName { get; set; }
        public string? Email { get; set; }
        public string? PhoneNumber { get; set; }
        public string? ImageUrl { get; set; }
        public string? Specialization { get; set; }
    }
}
