using ADHD.Infrastructure.Data;
using ADHD.Domain.Entities;
using ADHD.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class SessionsController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly IAnalysisService _analysisService;
        private readonly ILogger<SessionsController> _logger;
        private readonly IServiceScopeFactory _scopeFactory;

        public SessionsController(AppDbContext context, IAnalysisService analysisService, ILogger<SessionsController> logger, IServiceScopeFactory scopeFactory)
        {
            _context = context;
            _analysisService = analysisService;
            _logger = logger;
            _scopeFactory = scopeFactory;
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

            // ── Trigger AI Analysis (fire-and-forget safe) ──
            _ = Task.Run(async () =>
            {
                using (var scope = _scopeFactory.CreateScope())
                {
                    var scopedContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                    var scopedAnalysisService = scope.ServiceProvider.GetRequiredService<IAnalysisService>();
                    var scopedLogger = scope.ServiceProvider.GetRequiredService<ILogger<SessionsController>>();

                    try
                    {
                        // Count previous sessions for trend context
                        var previousSessionsCount = await scopedContext.GameSessions
                            .CountAsync(s => s.ChildId == session.ChildId && s.Id != sessionId);

                        // Gather trials for the AI agent
                        var mirrorTrials = await scopedContext.MirrorMeTrials.Where(t => t.SessionId == sessionId).ToListAsync();
                        var greenTrials = await scopedContext.GreenLightTrials.Where(t => t.SessionId == sessionId).ToListAsync();
                        var simonTrials = await scopedContext.SimonTrials.Where(t => t.SessionId == sessionId).ToListAsync();
                        var reactionTrials = await scopedContext.ReactionTrials.Where(t => t.SessionId == sessionId).ToListAsync();

                        object[] trials = Array.Empty<object>();
                        if (mirrorTrials.Count > 0)
                        {
                            trials = mirrorTrials.Select(t => (object)new
                            {
                                t.TrialIndex,
                                t.TargetPoseId,
                                t.ReactionTimeMs,
                                t.PoseSimilarity,
                                t.HoldingDurationMs,
                                t.FidgetScore,
                                t.PrematureMovement,
                                t.AttentionPercent
                            }).ToArray();
                        }
                        else if (greenTrials.Count > 0)
                        {
                            trials = greenTrials.Select(t => (object)new
                            {
                                t.TrialIndex,
                                t.Phase,
                                t.StopSignalDelayMs,
                                t.MovementIntensity,
                                t.StopReactionTimeMs,
                                t.FreezeQuality,
                                t.FalseStart
                            }).ToArray();
                        }
                        else if (simonTrials.Count > 0)
                        {
                            trials = simonTrials.Select(t => (object)new
                            {
                                t.Level,
                                t.SequenceLength,
                                t.Speed,
                                t.Step,
                                t.Expected,
                                t.Pressed,
                                t.Correct,
                                t.ReactionTimeMs
                            }).ToArray();
                        }
                        else if (reactionTrials.Count > 0)
                        {
                            trials = reactionTrials.Select(t => (object)new
                            {
                                t.Trial,
                                t.TargetLED,
                                t.Delay,
                                t.Result,
                                t.PressedButton,
                                t.ReactionTimeMs,
                                t.Correct,
                                t.ImpulsiveError
                            }).ToArray();
                        }

                        // Let's retrieve a fresh copy of the session from the scoped context to avoid cross-context tracking issues
                        var scopedSession = await scopedContext.GameSessions.FirstOrDefaultAsync(s => s.Id == sessionId);
                        if (scopedSession == null) return;

                        var analysisResult = await scopedAnalysisService.AnalyzeSessionAsync(
                            scopedSession.ChildId, sessionId, previousSessionsCount,
                            scopedSession, trials, request);

                        // Persist the AI analysis
                        var aiAnalysis = new AIAnalysis
                        {
                            SessionId = sessionId,
                            AttentionScore = analysisResult.AttentionScore ?? 0,
                            ImpulsivityScore = analysisResult.ImpulsivityScore ?? 0,
                            MotorControlScore = analysisResult.MotorControlScore ?? 0,
                            AttentionChange = analysisResult.AttentionChange,
                            ImpulsivityChange = analysisResult.ImpulsivityChange,
                            MotorControlChange = analysisResult.MotorControlChange,
                            SummaryText = analysisResult.SummaryText,
                            RecommendationsJson = analysisResult.Recommendations != null
                                ? JsonSerializer.Serialize(analysisResult.Recommendations)
                                : null,
                            ModelUsed = analysisResult.ModelUsed,
                            RawRequestJson = analysisResult.RawRequestJson,
                            RawResponseJson = analysisResult.RawResponseJson,
                            IsSuccessful = analysisResult.IsSuccessful,
                            ErrorMessage = analysisResult.ErrorMessage,
                            AnalysisDate = DateTime.UtcNow
                        };

                        scopedContext.AIAnalyses.Add(aiAnalysis);
                        await scopedContext.SaveChangesAsync();

                        scopedLogger.LogInformation(
                            "AI analysis completed for session {SessionId}: Success={IsSuccess}, Model={Model}",
                            sessionId, analysisResult.IsSuccessful, analysisResult.ModelUsed);
                    }
                    catch (Exception ex)
                    {
                        scopedLogger.LogError(ex, "AI analysis failed for session {SessionId}", sessionId);
                    }
                }
            });

            return Ok(new { succeeded = true });
        }

        /// <summary>
        /// Get the AI-processed analysis for a session.
        /// </summary>
        [HttpGet("{sessionId}/analysis")]
        [AllowAnonymous]
        public async Task<IActionResult> GetAnalysis(string sessionId)
        {
            var analysis = await _context.AIAnalyses
                .FirstOrDefaultAsync(a => a.SessionId == sessionId);

            if (analysis == null)
                return NotFound(new { succeeded = false, message = "Analysis not found for this session" });

            string[]? recommendations = null;
            if (!string.IsNullOrEmpty(analysis.RecommendationsJson))
            {
                try { recommendations = JsonSerializer.Deserialize<string[]>(analysis.RecommendationsJson); }
                catch { recommendations = null; }
            }

            return Ok(new
            {
                succeeded = true,
                data = new
                {
                    analysis.SessionId,
                    analysis.AnalysisDate,
                    scores = new
                    {
                        attention = analysis.AttentionScore,
                        impulsivity = analysis.ImpulsivityScore,
                        motorControl = analysis.MotorControlScore
                    },
                    trend = new
                    {
                        attentionChange = analysis.AttentionChange,
                        impulsivityChange = analysis.ImpulsivityChange,
                        motorControlChange = analysis.MotorControlChange
                    },
                    summaryText = analysis.SummaryText,
                    recommendations,
                    analysis.ModelUsed,
                    analysis.IsSuccessful,
                    analysis.ErrorMessage
                }
            });
        }

        /// <summary>
        /// Get AI analyses for all sessions of a child.
        /// </summary>
        [HttpGet("child/{childId}/analyses")]
        [AllowAnonymous]
        public async Task<IActionResult> GetChildAnalyses(string childId)
        {
            var analyses = await _context.AIAnalyses
                .Join(_context.GameSessions,
                    a => a.SessionId,
                    s => s.Id,
                    (a, s) => new { Analysis = a, Session = s })
                .Where(x => x.Session.ChildId == childId && x.Analysis.IsSuccessful)
                .OrderByDescending(x => x.Analysis.AnalysisDate)
                .Select(x => new
                {
                    x.Analysis.SessionId,
                    x.Analysis.AnalysisDate,
                    x.Session.GameType,
                    scores = new
                    {
                        attention = x.Analysis.AttentionScore,
                        impulsivity = x.Analysis.ImpulsivityScore,
                        motorControl = x.Analysis.MotorControlScore
                    },
                    trend = new
                    {
                        attentionChange = x.Analysis.AttentionChange,
                        impulsivityChange = x.Analysis.ImpulsivityChange,
                        motorControlChange = x.Analysis.MotorControlChange
                    },
                    summaryText = x.Analysis.SummaryText,
                    recommendations = x.Analysis.RecommendationsJson
                })
                .ToListAsync();

            return Ok(new { succeeded = true, data = analyses });
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
