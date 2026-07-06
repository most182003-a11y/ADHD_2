using ADHD.Domain.Entities;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace ADHD.Infrastructure.Data
{
    public class AppDbContext : IdentityDbContext<AppUser>
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<Child> Children { get; set; }
        public DbSet<Parent> Parents { get; set; }
        public DbSet<Doctor> Doctors { get; set; }
        public DbSet<Admin> Admins { get; set; }
        public DbSet<GameSession> GameSessions { get; set; }
        public DbSet<MirrorMeTrial> MirrorMeTrials { get; set; }
        public DbSet<GreenLightTrial> GreenLightTrials { get; set; }
        public DbSet<SimonTrial> SimonTrials { get; set; }
        public DbSet<ReactionTrial> ReactionTrials { get; set; }
        public DbSet<SessionSummary> SessionSummaries { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<AppUser>().UseTptMappingStrategy();
            modelBuilder.Entity<Parent>().ToTable("Parents");
            modelBuilder.Entity<Doctor>().ToTable("Doctors");
            modelBuilder.Entity<Admin>().ToTable("Admins");

            modelBuilder.Entity<Child>(entity =>
            {
                entity.ToTable("children");
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired();
                entity.Property(e => e.Gender).HasConversion<string>();
                entity.Property(e => e.DiagnosisSeverity).HasConversion<string>();
                entity.Property(e => e.Status).HasConversion<string>();

                entity.HasOne(e => e.Parent)
                    .WithMany(p => p.Children)
                    .HasForeignKey(e => e.ParentId)
                    .OnDelete(DeleteBehavior.Restrict);

                entity.HasOne(e => e.Doctor)
                    .WithMany(d => d.Patients)
                    .HasForeignKey(e => e.DoctorId)
                    .OnDelete(DeleteBehavior.Restrict);
            });

            modelBuilder.Entity<GameSession>(entity =>
            {
                entity.ToTable("game_sessions");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Child)
                    .WithMany(c => c.GameSessions)
                    .HasForeignKey(e => e.ChildId);

                entity.HasMany(e => e.MirrorMeTrials)
                    .WithOne(t => t.Session)
                    .HasForeignKey(t => t.SessionId)
                    .OnDelete(DeleteBehavior.Cascade);

                entity.HasMany(e => e.GreenLightTrials)
                    .WithOne(t => t.Session)
                    .HasForeignKey(t => t.SessionId)
                    .OnDelete(DeleteBehavior.Cascade);

                entity.HasMany(e => e.SimonTrials)
                    .WithOne(t => t.Session)
                    .HasForeignKey(t => t.SessionId)
                    .OnDelete(DeleteBehavior.Cascade);

                entity.HasMany(e => e.ReactionTrials)
                    .WithOne(t => t.Session)
                    .HasForeignKey(t => t.SessionId)
                    .OnDelete(DeleteBehavior.Cascade);

                entity.HasOne(e => e.Summary)
                    .WithOne(s => s.Session)
                    .HasForeignKey<SessionSummary>(s => s.SessionId)
                    .OnDelete(DeleteBehavior.Cascade);

                entity.HasIndex(e => new { e.ChildId, e.GameType });
            });

            modelBuilder.Entity<MirrorMeTrial>(entity =>
            {
                entity.ToTable("mirror_me_trials");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Session)
                    .WithMany(s => s.MirrorMeTrials)
                    .HasForeignKey(e => e.SessionId);
            });

            modelBuilder.Entity<GreenLightTrial>(entity =>
            {
                entity.ToTable("green_light_trials");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Session)
                    .WithMany(s => s.GreenLightTrials)
                    .HasForeignKey(e => e.SessionId);
            });

            modelBuilder.Entity<SimonTrial>(entity =>
            {
                entity.ToTable("simon_trials");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Session)
                    .WithMany(s => s.SimonTrials)
                    .HasForeignKey(e => e.SessionId);
            });

            modelBuilder.Entity<ReactionTrial>(entity =>
            {
                entity.ToTable("reaction_trials");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Session)
                    .WithMany(s => s.ReactionTrials)
                    .HasForeignKey(e => e.SessionId);
            });

            modelBuilder.Entity<SessionSummary>(entity =>
            {
                entity.ToTable("session_summaries");
                entity.HasKey(e => e.Id);

                entity.HasOne(e => e.Session)
                    .WithOne(s => s.Summary)
                    .HasForeignKey<SessionSummary>(e => e.SessionId);

                entity.HasIndex(e => e.SessionId).IsUnique();
            });
        }

        public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
        {
            foreach (var entry in ChangeTracker.Entries<BaseEntity>())
            {
                switch (entry.State)
                {
                    case EntityState.Added:
                        entry.Entity.CreatedAt = DateTime.UtcNow;
                        break;
                    case EntityState.Modified:
                        entry.Entity.UpdatedAt = DateTime.UtcNow;
                        break;
                }
            }

            return await base.SaveChangesAsync(cancellationToken);
        }
    }
}
