import { useState } from "react";
import { getMetricDetails } from "@/core/constants/metrics";
import { useGames, Game } from "@/hooks/useApiData";
import SectionCard from "@/components/SectionCard";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Gamepad2, Search, Brain, Target, Sparkles, Activity, Eye, Info } from "lucide-react";

export function GamesCatalogPage() {
  const { games, loading, error } = useGames();
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);

  // Get unique category names from loaded games
  const uniqueCategories = Array.from(new Set(games.map((g) => g.categoryNameAr))).filter(Boolean);

  const filteredGames = games.filter((game) => {
    const matchesSearch =
      game.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (game.description && game.description.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory =
      categoryFilter === "all" ||
      game.categoryNameAr === categoryFilter ||
      game.categoryNameEn === categoryFilter;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 animate-fade-in text-right" dir="rtl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-2.5">
            <Brain className="w-8 h-8 text-indigo-600 animate-pulse" />
            دليل الألعاب العلاجية والتشخيصية
          </h1>
          <p className="text-muted-foreground">
            عرض وتصفح الألعاب العلاجية والتشخيصية المعتمدة علمياً لتحليل أعراض فرط الحركة وتشتت الانتباه.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Side: Filter Control & Stats */}
        <div className="md:col-span-1 space-y-4">
          <SectionCard className="border-slate-100 shadow-lg bg-white/70 backdrop-blur-md">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2 justify-start">
              <Target className="w-4 h-4 text-indigo-500" />
              أدوات التصفية والبحث
            </h3>
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">البحث عن لعبة</label>
                <div className="relative">
                  <Search className="absolute right-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="ابحث عن لعبة..."
                    className="pr-9 border-slate-200 text-right font-medium"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">التصنيف العلاجي</label>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger className="w-full border-slate-200 text-right">
                    <SelectValue placeholder="تصفية حسب التصنيف" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all" className="text-right">جميع التصنيفات</SelectItem>
                    {uniqueCategories.map((cat) => (
                      <SelectItem key={cat} value={cat} className="text-right">
                        {cat}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </SectionCard>

          <SectionCard className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-0 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <Activity className="w-40 h-40" />
            </div>
            <div className="relative z-10 space-y-3">
              <div className="bg-white/10 w-fit p-2 rounded-xl text-indigo-200">
                <Sparkles className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-lg text-right">التحليل العلمي للألعاب</h4>
              <p className="text-xs text-indigo-200 leading-relaxed text-right">
                تقوم هذه الألعاب بجمع مئات نقاط البيانات في الثانية لقياس الانتباه المستدام والتأخير الاستجابي والتحكم الحركي بدقة ملي ثانية.
              </p>
              <div className="pt-2 flex justify-between items-center text-xs border-t border-white/10" dir="ltr">
                <span className="font-bold bg-indigo-500/30 px-2 py-0.5 rounded-full">{games.length} ألعاب</span>
                <span className="text-right">ألعاب مفعلة حالياً</span>
              </div>
            </div>
          </SectionCard>
        </div>

        {/* Right Side: Games List / Grid */}
        <div className="md:col-span-2">
          {loading ? (
            <SectionCard className="flex flex-col items-center justify-center min-h-[350px] border-slate-100">
              <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-indigo-600 mb-3"></div>
              <p className="text-sm text-slate-500 font-medium">جاري تحميل دليل الألعاب...</p>
            </SectionCard>
          ) : error ? (
            <SectionCard className="border-red-100 bg-red-50/50 p-6 flex flex-col items-center justify-center text-center">
              <div className="p-3 bg-red-100 rounded-2xl text-red-600 mb-3">
                <Info className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-red-800 text-lg mb-1">خطأ في الاتصال بالخادم</h3>
              <p className="text-sm text-red-600 max-w-md">
                فشل في تحميل دليل الألعاب من الباك اند. يرجى التأكد من تشغيل سيرفر الـ .NET والمحاولة مرة أخرى.
              </p>
            </SectionCard>
          ) : (
            <SectionCard className="border-slate-100 shadow-md">
              <div className="rounded-md overflow-hidden border border-slate-100">
                <Table>
                  <TableHeader className="bg-slate-50/70">
                    <TableRow>
                      <TableHead className="w-[200px] text-right font-bold text-slate-700">اسم اللعبة</TableHead>
                      <TableHead className="text-right font-bold text-slate-700">التصنيف العلاجي</TableHead>
                      <TableHead className="hidden md:table-cell text-right font-bold text-slate-700">القياس الطبي</TableHead>
                      <TableHead className="text-center font-bold text-slate-700">التفاصيل</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredGames.length > 0 ? (
                      filteredGames.map((game) => (
                        <TableRow key={game.id} className="hover:bg-slate-50/50 transition-colors">
                          <TableCell className="font-semibold text-slate-800 text-right">
                            <div className="flex items-center gap-3">
                              <div className="bg-indigo-50 p-2.5 rounded-xl text-indigo-600 shadow-sm border border-indigo-100/50">
                                <Gamepad2 className="w-4 h-4" />
                              </div>
                              <div className="flex flex-col text-right">
                                <span>{game.name}</span>
                                {game.isActive ? (
                                  <span className="text-[10px] text-emerald-600 bg-emerald-50/50 border border-emerald-100 rounded-full px-2 py-0.5 w-fit mt-1 font-semibold flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                    مربوطة بالخادم (نشطة)
                                  </span>
                                ) : (
                                  <span className="text-[10px] text-slate-500 bg-slate-50/50 border border-slate-200 rounded-full px-2 py-0.5 w-fit mt-1 font-semibold flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                                    غير نشطة حالياً
                                  </span>
                                )}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            <Badge
                              className={`font-medium px-2.5 py-0.5 rounded-full border text-[11px] shadow-sm ${game.categoryNameEn.includes("Hyperactivity")
                                  ? "bg-rose-50 text-rose-700 border-rose-200"
                                  : "bg-blue-50 text-blue-700 border-blue-200"
                                }`}
                            >
                              {game.categoryNameAr}
                            </Badge>
                          </TableCell>
                          <TableCell className="hidden md:table-cell text-xs text-slate-500 max-w-[200px] truncate text-right">
                            <span className="font-semibold text-slate-600">المؤشرات: </span>
                            {game.relevantMetrics.split(',').map(m => getMetricDetails(m).ar).join('، ')}
                          </TableCell>
                          <TableCell className="text-center">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setSelectedGame(game)}
                              className="border-indigo-100 text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 gap-1.5"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              عرض التفاصيل
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={4} className="h-32 text-center text-slate-400">
                          لا توجد ألعاب تطابق معايير البحث الحالية.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </SectionCard>
          )}
        </div>
      </div>

      {/* Game Details Modal Dialog */}
      <Dialog open={selectedGame !== null} onOpenChange={(open) => !open && setSelectedGame(null)}>
        {selectedGame && (
          <DialogContent className="max-w-xl bg-white border-slate-100 shadow-2xl rounded-2xl p-6 text-right">
            <DialogHeader className="border-b border-slate-100 pb-4 text-right">
              <div className="flex items-center gap-3.5 justify-start">
                <div className="bg-indigo-600 p-3 rounded-2xl text-white shadow-lg shadow-indigo-100">
                  <Gamepad2 className="w-6 h-6" />
                </div>
                <div className="space-y-0.5 text-right font-medium">
                  <DialogTitle className="text-xl font-bold text-slate-800 text-right">{selectedGame.name}</DialogTitle>
                  <DialogDescription className="text-xs text-indigo-600 font-semibold text-right">
                    {selectedGame.categoryNameAr}
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            <div className="py-4 space-y-4 text-right" dir="rtl">
              {/* Connection Status Banner */}
              {selectedGame.isActive ? (
                <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200/85 rounded-xl p-3 flex items-start gap-3 text-right">
                  <Activity className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                  <div className="space-y-1">
                    <h4 className="font-bold text-emerald-800 text-sm">حالة الاتصال والربط بالخادم</h4>
                    <p className="text-xs text-emerald-700 leading-relaxed">
                      هذه اللعبة متصلة بالكامل بالخادم الخلفي (Backend). يتم تسجيل جلسات اللعب ومحاولات الطفل وإرسالها فورياً لحساب الطبيب أو ولي الأمر، وتوليد تقارير الذكاء الاصطناعي تلقائياً.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-3 flex items-start gap-3 text-right">
                  <Info className="w-5 h-5 text-slate-500 mt-0.5 flex-shrink-0" />
                  <div className="space-y-1">
                    <h4 className="font-bold text-slate-700 text-sm">حالة الاتصال والربط بالخادم</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      هذه اللعبة تحت التطوير حالياً وغير مفعلة على هذا الإصدار من النظام.
                    </p>
                  </div>
                </div>
              )}

              {/* Description */}
              <div className="space-y-1.5">
                <h4 className="font-bold text-slate-700 text-sm flex items-center gap-1.5 justify-start">
                  <Brain className="w-4 h-4 text-indigo-500" />
                  الوصف العلمي للأداء والأثر العلاجي:
                </h4>
                <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                  {selectedGame.description || "هذه اللعبة مخصصة لتقييم المهارات الإدراكية والتنفيذية للطفل، وتوفر بيانات تحليلية دقيقة حول مدى تقدم وتطور الاستجابات الحيوية."}
                </p>
              </div>

              {/* Metrics Section */}
              <div className="space-y-2.5">
                <h4 className="font-bold text-slate-700 text-sm flex items-center gap-1.5 justify-start">
                  <Target className="w-4 h-4 text-indigo-500" />
                  المقاييس والمؤشرات الحيوية التي تحللها اللعبة:
                </h4>
                <div className="grid grid-cols-1 gap-2 text-right">
                  {selectedGame.relevantMetrics.split(",").map((metricKey) => {
                    const details = getMetricDetails(metricKey);
                    return (
                      <div key={metricKey} className="flex gap-3 p-3 rounded-xl border border-slate-100 bg-white hover:border-slate-200 transition-all text-right justify-between items-center">
                        <div className="flex-1 space-y-1 text-right">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-sm text-slate-800">{details.ar}</span>
                            <span className="text-[10px] text-slate-400 font-mono font-medium">{details.en}</span>
                          </div>
                          <p className="text-xs text-slate-500 leading-relaxed">{details.desc}</p>
                        </div>
                        <div className={`h-fit text-[10px] font-bold px-2 py-0.5 rounded-md border mr-4 whitespace-nowrap ${details.color}`}>
                          مقياس نشط
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="flex justify-end border-t border-slate-100 pt-4 mt-2">
              <Button onClick={() => setSelectedGame(null)} className="bg-slate-900 hover:bg-slate-800 text-white font-medium">
                إغلاق النافذة
              </Button>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}

export default GamesCatalogPage;
