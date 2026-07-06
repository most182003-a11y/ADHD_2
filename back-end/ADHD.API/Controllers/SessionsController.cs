using ADHD.Infrastructure.Data;
using ADHD.Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Linq;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class SessionsController : ControllerBase
    {
        private readonly AppDbContext _context;

        public SessionsController(AppDbContext context)
        {
            _context = context;
        }

        [HttpPost]
        [AllowAnonymous]
        public async Task<IActionResult> CreateSession([FromBody] CreateSessionRequest request)
        {
            var session = new GameSession
            {
                ChildId = request.ChildId,
                GameType = request.GameType
            };

            _context.GameSessions.Add(session);
            await _context.SaveChangesAsync();

            return Ok(new { succeeded = true, data = new { session.Id } });
        }

        [HttpGet]
        public async Task<IActionResult> GetSessions([FromQuery] string? childId, [FromQuery] string? gameType)
        {
            var query = _context.GameSessions.AsQueryable();

            if (!string.IsNullOrWhiteSpace(childId))
                query = query.Where(s => s.ChildId == childId);
            if (!string.IsNullOrWhiteSpace(gameType))
                query = query.Where(s => s.GameType == gameType);

            var sessions = await query
                .OrderByDescending(s => s.CreatedAt)
                .Select(s => new
                {
                    s.Id,
                    s.ChildId,
                    s.GameType,
                    s.CreatedAt,
                    MirrorMeTrialsCount = s.MirrorMeTrials.Count,
                    GreenLightTrialsCount = s.GreenLightTrials.Count,
                    SimonTrialsCount = s.SimonTrials.Count,
                    ReactionTrialsCount = s.ReactionTrials.Count,
                    HasSummary = s.Summary != null
                })
                .ToListAsync();

            return Ok(new { succeeded = true, data = sessions });
        }

        [HttpGet("{sessionId}")]
        public async Task<IActionResult> GetSession(string sessionId)
        {
            var session = await _context.GameSessions
                .Include(s => s.MirrorMeTrials)
                .Include(s => s.GreenLightTrials)
                .Include(s => s.SimonTrials)
                .Include(s => s.ReactionTrials)
                .Include(s => s.Summary)
                .FirstOrDefaultAsync(s => s.Id == sessionId);

            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            return Ok(new { succeeded = true, data = session });
        }

        [HttpPost("{sessionId}/mirror-me-trials")]
        [AllowAnonymous]
        public async Task<IActionResult> AddMirrorMeTrials(string sessionId, [FromBody] AddMirrorMeTrialsRequest request)
        {
            var session = await _context.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            foreach (var trial in request.Trials)
            {
                _context.MirrorMeTrials.Add(new MirrorMeTrial
                {
                    SessionId = sessionId,
                    TrialIndex = trial.TrialIndex,
                    TargetPoseId = trial.TargetPoseId,
                    ReactionTimeMs = trial.ReactionTimeMs,
                    PoseSimilarity = trial.PoseSimilarity,
                    HoldingDurationMs = trial.HoldingDurationMs,
                    FidgetScore = trial.FidgetScore,
                    PrematureMovement = trial.PrematureMovement,
                    AttentionPercent = trial.AttentionPercent
                });
            }

            await _context.SaveChangesAsync();
            return Ok(new { succeeded = true });
        }

        [HttpPost("{sessionId}/green-light-trials")]
        [AllowAnonymous]
        public async Task<IActionResult> AddGreenLightTrials(string sessionId, [FromBody] AddGreenLightTrialsRequest request)
        {
            var session = await _context.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            foreach (var trial in request.Trials)
            {
                _context.GreenLightTrials.Add(new GreenLightTrial
                {
                    SessionId = sessionId,
                    TrialIndex = trial.TrialIndex,
                    Phase = trial.Phase,
                    StopSignalDelayMs = trial.StopSignalDelayMs,
                    MovementIntensity = trial.MovementIntensity,
                    StopReactionTimeMs = trial.StopReactionTimeMs,
                    FreezeQuality = trial.FreezeQuality,
                    FalseStart = trial.FalseStart
                });
            }

            await _context.SaveChangesAsync();
            return Ok(new { succeeded = true });
        }

        [HttpPost("{sessionId}/simon-trials")]
        [AllowAnonymous]
        public async Task<IActionResult> AddSimonTrials(string sessionId, [FromBody] AddSimonTrialsRequest request)
        {
            var session = await _context.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            foreach (var trial in request.Trials)
            {
                _context.SimonTrials.Add(new SimonTrial
                {
                    SessionId = sessionId,
                    Level = trial.Level,
                    SequenceLength = trial.SequenceLength,
                    Speed = trial.Speed,
                    Step = trial.Step,
                    Expected = trial.Expected,
                    Pressed = trial.Pressed,
                    Correct = trial.Correct,
                    ReactionTimeMs = trial.ReactionTimeMs
                });
            }

            await _context.SaveChangesAsync();
            return Ok(new { succeeded = true });
        }

        [HttpPost("{sessionId}/reaction-trials")]
        [AllowAnonymous]
        public async Task<IActionResult> AddReactionTrials(string sessionId, [FromBody] AddReactionTrialsRequest request)
        {
            var session = await _context.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            foreach (var trial in request.Trials)
            {
                _context.ReactionTrials.Add(new ReactionTrial
                {
                    SessionId = sessionId,
                    Trial = trial.Trial,
                    TargetLED = trial.TargetLED,
                    Delay = trial.Delay,
                    Result = trial.Result,
                    PressedButton = trial.PressedButton,
                    ReactionTimeMs = trial.ReactionTimeMs,
                    Correct = trial.Correct,
                    ImpulsiveError = trial.ImpulsiveError
                });
            }

            await _context.SaveChangesAsync();
            return Ok(new { succeeded = true });
        }

        [HttpPost("{sessionId}/summary")]
        [AllowAnonymous]
        public async Task<IActionResult> SaveSummary(string sessionId, [FromBody] SaveSummaryRequest request)
        {
            var session = await _context.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
            if (session == null)
                return NotFound(new { succeeded = false, message = "Session not found" });

            var existing = await _context.SessionSummaries.FirstOrDefaultAsync(s => s.SessionId == sessionId);
            if (existing != null)
                return BadRequest(new { succeeded = false, message = "Summary already exists for this session" });

            _context.SessionSummaries.Add(new SessionSummary
            {
                SessionId = sessionId,
                TotalTrials = request.TotalTrials,
                AverageReactionTimeMs = request.AverageReactionTimeMs,
                AverageSimilarity = request.AverageSimilarity,
                TotalFidgetScore = request.TotalFidgetScore,
                AttentionOverall = request.AttentionOverall,
                AverageStopReactionTimeMs = request.AverageStopReactionTimeMs,
                FalseStartCount = request.FalseStartCount,
                AverageFreezeQuality = request.AverageFreezeQuality,
                MovementIntensityOverall = request.MovementIntensityOverall,

                // Simon Memory fields
                FinalLevel = request.FinalLevel,
                TotalCorrectSteps = request.TotalCorrectSteps,
                TotalSteps = request.TotalSteps,
                PrematurePressesDuringShow = request.PrematurePressesDuringShow,
                EndStatus = request.EndStatus,

                // Reaction Time fields
                Hits = request.Hits,
                FalseStarts = request.FalseStarts,
                Misses = request.Misses,
                ImpulsiveErrors = request.ImpulsiveErrors,
                WrongButtons = request.WrongButtons,
                ReactionTimeStdDevMs = request.ReactionTimeStdDevMs,
                ImpulsivityScore = request.ImpulsivityScore,
                AttentionScore = request.AttentionScore
            });

            await _context.SaveChangesAsync();
            return Ok(new { succeeded = true });
        }
    }

    public class CreateSessionRequest
    {
        public string ChildId { get; set; } = string.Empty;
        public string GameType { get; set; } = string.Empty;
    }

    public class AddMirrorMeTrialsRequest
    {
        public MirrorMeTrialRequest[] Trials { get; set; } = [];
    }

    public class MirrorMeTrialRequest
    {
        public int TrialIndex { get; set; }
        public string? TargetPoseId { get; set; }
        public int ReactionTimeMs { get; set; }
        public double PoseSimilarity { get; set; }
        public int HoldingDurationMs { get; set; }
        public double FidgetScore { get; set; }
        public bool PrematureMovement { get; set; }
        public double AttentionPercent { get; set; }
    }

    public class AddGreenLightTrialsRequest
    {
        public GreenLightTrialRequest[] Trials { get; set; } = [];
    }

    public class GreenLightTrialRequest
    {
        public int TrialIndex { get; set; }
        public string Phase { get; set; } = string.Empty;
        public int? StopSignalDelayMs { get; set; }
        public double? MovementIntensity { get; set; }
        public int? StopReactionTimeMs { get; set; }
        public double? FreezeQuality { get; set; }
        public bool? FalseStart { get; set; }
    }

    public class SaveSummaryRequest
    {
        public int TotalTrials { get; set; }
        public double? AverageReactionTimeMs { get; set; }
        public double? AverageSimilarity { get; set; }
        public double? TotalFidgetScore { get; set; }
        public double? AttentionOverall { get; set; }
        public double? AverageStopReactionTimeMs { get; set; }
        public int? FalseStartCount { get; set; }
        public double? AverageFreezeQuality { get; set; }
        public double? MovementIntensityOverall { get; set; }

        // Simon Memory fields
        public int? FinalLevel { get; set; }
        public int? TotalCorrectSteps { get; set; }
        public int? TotalSteps { get; set; }
        public int? PrematurePressesDuringShow { get; set; }
        public string? EndStatus { get; set; }

        // Reaction Time fields
        public int? Hits { get; set; }
        public int? FalseStarts { get; set; }
        public int? Misses { get; set; }
        public int? ImpulsiveErrors { get; set; }
        public int? WrongButtons { get; set; }
        public double? ReactionTimeStdDevMs { get; set; }
        public double? ImpulsivityScore { get; set; }
        public double? AttentionScore { get; set; }
    }

    public class AddSimonTrialsRequest
    {
        public SimonTrialRequest[] Trials { get; set; } = [];
    }

    public class SimonTrialRequest
    {
        public int Level { get; set; }
        public int SequenceLength { get; set; }
        public double Speed { get; set; }
        public int Step { get; set; }
        public int Expected { get; set; }
        public int Pressed { get; set; }
        public bool Correct { get; set; }
        public double ReactionTimeMs { get; set; }
    }

    public class AddReactionTrialsRequest
    {
        public ReactionTrialRequest[] Trials { get; set; } = [];
    }

    public class ReactionTrialRequest
    {
        public int Trial { get; set; }
        public int TargetLED { get; set; }
        public double Delay { get; set; }
        public string Result { get; set; } = string.Empty;
        public int PressedButton { get; set; }
        public double? ReactionTimeMs { get; set; }
        public bool Correct { get; set; }
        public bool ImpulsiveError { get; set; }
    }
}
