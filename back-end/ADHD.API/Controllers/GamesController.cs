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
                new 
                { 
                    id = "mirror_me", 
                    name = "تقليد الحركات (Mirror Me)", 
                    description = "لعبة تقليد الحركات لقياس التركيز البصري والتحكم الحركي وتحديد مدى ثبات الطفل وقدرته على الاستجابة للتوجيهات الجسدية.", 
                    relevantMetrics = "MotorControlScore,FalseMoves,SuccessRate,TotalTrials",
                    isActive = true,
                    categoryId = "attention_motor",
                    categoryNameAr = "تشتت الانتباه والتحكم الحركي",
                    categoryNameEn = "Attention & Motor Control"
                },
                new 
                { 
                    id = "green_light", 
                    name = "الضوء الأخضر والضوء الأحمر (Green Light)", 
                    description = "لعبة التحكم في الاندفاع والاستجابة للإشارات (توقف/تحرك) لقياس قدرة الطفل على تثبيط الاستجابة الحركية والتسرع.", 
                    relevantMetrics = "ImpulsivityIndex,FalseMoves,AvgReactionTime,SuccessRate,TotalTrials",
                    isActive = true,
                    categoryId = "hyperactivity_impulsivity",
                    categoryNameAr = "فرط الحركة والاندفاعية",
                    categoryNameEn = "Hyperactivity & Impulsivity"
                },
                new 
                { 
                    id = "simon", 
                    name = "سيمون يقول (Simon Memory)", 
                    description = "لعبة تذكر تتابع الألوان والأصوات وتكراره لقياس سعة الذاكرة العاملة البصرية والسمعية والانتباه المستدام.", 
                    relevantMetrics = "MaxConsecutiveSuccess,SuccessRate,AvgReactionTime,TotalTrials",
                    isActive = true,
                    categoryId = "working_memory_attention",
                    categoryNameAr = "الذاكرة العاملة والانتباه",
                    categoryNameEn = "Working Memory & Attention"
                },
                new 
                { 
                    id = "reaction_time", 
                    name = "سرعة الاستجابة (Reaction Time)", 
                    description = "لعبة قياس سرعة رد الفعل وزمن الاستجابة للمؤثرات البصرية المفاجئة وتحديد مستوى التشتت الذهني.", 
                    relevantMetrics = "AvgReactionTime,FalseStops,SuccessRate,TotalTrials",
                    isActive = true,
                    categoryId = "attention_speed",
                    categoryNameAr = "سرعة الاستجابة والتركيز",
                    categoryNameEn = "Attention & Speed"
                }
            };

            return Ok(new { succeeded = true, data = games });
        }
    }
}
