"use client";
import { CheckCircle2, XCircle, AlertCircle, RefreshCw } from "lucide-react";

interface StatusCardProps {
  result: any;
  onReset?: () => void;
}

export default function StatusCard({ result, onReset }: StatusCardProps) {
  if (!result) return null;

  const styleMap: any = {
    "VALID": { 
      border: "border-emerald-500/50", 
      bg: "bg-emerald-500/10", 
      icon: <CheckCircle2 className="w-10 h-10 text-emerald-400" />, 
      title: "text-emerald-400" 
    },
    "INVALID": { 
      border: "border-red-500/50", 
      bg: "bg-red-500/10", 
      icon: <XCircle className="w-10 h-10 text-red-400" />, 
      title: "text-red-400" 
    },
    "UNKNOWN": { 
      border: "border-yellow-500/50", 
      bg: "bg-yellow-500/10", 
      icon: <AlertCircle className="w-10 h-10 text-yellow-400" />, 
      title: "text-yellow-400" 
    }
  };

  const currentStyle = styleMap[result.status] || styleMap["UNKNOWN"];

  return (
    <div className={`mt-10 p-8 rounded-2xl border backdrop-blur-xl shadow-2xl ${currentStyle.border} ${currentStyle.bg} animate-in fade-in slide-in-from-bottom-8 duration-500`}>
      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
        <div className="flex-shrink-0 p-3 bg-white/5 rounded-full border border-white/10 shadow-inner">
          {currentStyle.icon}
        </div>
        <div className="flex-1">
          <h3 className={`text-2xl font-bold mb-2 ${currentStyle.title}`}>{result.label || "Sonuç"}</h3>
          <p className="text-slate-300 text-base leading-relaxed mb-4">{result.message}</p>
          
          {result.url && (
            <div className="mb-4">
              <span className="text-slate-400 text-sm font-medium">Kaynak: </span>
              <a href={result.url} target="_blank" rel="noreferrer" className="inline-block text-blue-400 hover:text-blue-300 underline underline-offset-4 text-sm break-all transition-colors">
                {result.url}
              </a>
            </div>
          )}
          
          {result.extracted_data && (
            <div className="mt-4 pt-4 border-t border-white/10 text-left">
              {result.detected_region_name && (
                <div className="mb-4 bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/30 p-3 rounded-lg shadow-inner">
                  <p className="text-xs text-blue-300 uppercase tracking-widest font-semibold flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span> Yapay Zeka Görsel Analizi
                  </p>
                  <div className="mt-2 text-sm text-blue-100">
                    Tespit Edilen Bölge: <strong className="text-white">{result.detected_region_name}</strong> 
                    <span className="text-blue-300 ml-2">(%{result.match_score} Eşleşme)</span>
                  </div>
                </div>
              )}
              <p className="text-xs text-slate-400 mb-3 uppercase tracking-widest font-semibold">OCR ile Tespit Edilen Veriler</p>
              <div className="bg-black/40 p-4 rounded-xl border border-white/5 text-blue-200 text-sm font-mono overflow-x-auto shadow-inner">
                {result.extracted_data.license_no && <div>Lisans No: <span className="text-white">{result.extracted_data.license_no}</span></div>}
                {result.extracted_data.country && <div>Ülke: <span className="text-white">{result.extracted_data.country.toUpperCase()}</span></div>}
              </div>
            </div>
          )}
        </div>
        
        {onReset && (
          <button 
            onClick={onReset}
            className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium text-slate-300 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Yeni</span>
          </button>
        )}
      </div>
      
      {onReset && (
        <button 
          onClick={onReset}
          className="mt-6 w-full sm:hidden flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-medium text-slate-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Yeni Sorgulama Yap</span>
        </button>
      )}
    </div>
  );
}
