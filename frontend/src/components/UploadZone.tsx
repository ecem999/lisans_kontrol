"use client";
import { useState, useRef } from "react";
import { UploadCloud, Loader2, QrCode, FileText } from "lucide-react";

interface UploadZoneProps {
  onUpload: (formData: FormData) => void;
  isLoading: boolean;
}

export default function UploadZone({ onUpload, isLoading }: UploadZoneProps) {
  const [country, setCountry] = useState("spain");
  const [region, setRegion] = useState("auto");
  const [isDragging, setIsDragging] = useState(false);
  const [isDraggingQR, setIsDraggingQR] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const qrInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file) return;
    const formData = new FormData();
    formData.append("country", country);
    if (region) formData.append("region", region);
    formData.append("file", file);
    onUpload(formData);
  };

  const borderClass = (dragState: boolean) => dragState 
    ? "border-blue-400 bg-blue-500/10 shadow-[0_0_20px_rgba(59,130,246,0.2)]" 
    : "border-white/20 hover:border-white/40 hover:bg-white/5";
    
  const inputClass = "w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl focus:outline-none focus:border-blue-500/50 text-white transition-all";

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <select value={country} onChange={(e) => setCountry(e.target.value)} className={inputClass}>
          <option value="spain" className="bg-slate-800">İspanya</option>
          <option value="france" className="bg-slate-800">Fransa</option>
          <option value="italy" className="bg-slate-800">İtalya</option>
        </select>
        
        {country === "spain" && (
          <select value={region} onChange={(e) => setRegion(e.target.value)} className={`${inputClass} animate-in fade-in`}>
            <option value="auto" className="bg-slate-800 text-blue-400 font-bold">✨ Otomatik Algıla (Yapay Zeka)</option>
            <option value="" className="bg-slate-800">Bölge Seçiniz (Zorunlu)</option>
            <option value="andalucia" className="bg-slate-800">Endülüs (Andalucía)</option>
            <option value="aragon" className="bg-slate-800">Aragón</option>
            <option value="asturias" className="bg-slate-800">Asturias</option>
            <option value="baleares" className="bg-slate-800">Balear Adaları (Baleares)</option>
            <option value="canarias" className="bg-slate-800">Kanarya Adaları (Canarias)</option>
            <option value="cantabria" className="bg-slate-800">Cantabria</option>
            <option value="castilla_la_mancha" className="bg-slate-800">Kastilya-La Mancha</option>
            <option value="castilla_y_leon" className="bg-slate-800">Kastilya ve Leon</option>
            <option value="catalunya" className="bg-slate-800">Katalonya (Cataluña)</option>
            <option value="extremadura" className="bg-slate-800">Extremadura</option>
            <option value="galicia" className="bg-slate-800">Galiçya (Galicia)</option>
            <option value="madrid" className="bg-slate-800">Madrid</option>
            <option value="murcia" className="bg-slate-800">Murcia</option>
            <option value="navarra" className="bg-slate-800">Navarra</option>
            <option value="pais_vasco" className="bg-slate-800">Bask Bölgesi (País Vasco)</option>
            <option value="rioja" className="bg-slate-800">La Rioja</option>
            <option value="valencia" className="bg-slate-800">Valensiya (Comunidad Valenciana)</option>
            <option value="ceuta_melilla" className="bg-slate-800">Ceuta ve Melilla</option>
          </select>
        )}
      </div>

      {country === "italy" ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* İtalya QR Yükleme Alanı */}
          <div 
            className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${borderClass(isDraggingQR)}`}
            onDragOver={(e) => { e.preventDefault(); setIsDraggingQR(true); }}
            onDragLeave={() => setIsDraggingQR(false)}
            onDrop={(e) => { e.preventDefault(); setIsDraggingQR(false); handleFile(e.dataTransfer.files ? e.dataTransfer.files[0] : null as any); }}
            onClick={() => qrInputRef.current?.click()}
          >
            <input type="file" className="hidden" ref={qrInputRef} onChange={(e) => e.target.files && handleFile(e.target.files[0])} accept="image/jpeg, image/png, image/webp" />
            
            {isLoading ? (
              <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in-95 duration-300">
                <Loader2 className="w-10 h-10 text-emerald-400 animate-spin" />
                <p className="text-emerald-300 font-medium text-sm">QR Taranıyor...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className={`p-4 rounded-full transition-colors ${isDraggingQR ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/10 text-slate-300'}`}>
                  <QrCode className="w-8 h-8" />
                </div>
                <p className="text-slate-200 font-medium text-sm">QR Kod Fotoğrafı</p>
                <p className="text-xs text-slate-400">Sürükleyin veya tıklayın</p>
              </div>
            )}
          </div>

          {/* İtalya Yaka Kartı Yükleme Alanı */}
          <div 
            className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${borderClass(isDragging)}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files ? e.dataTransfer.files[0] : null as any); }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input type="file" className="hidden" ref={fileInputRef} onChange={(e) => e.target.files && handleFile(e.target.files[0])} accept="image/jpeg, image/png, image/webp" />
            
            {isLoading ? (
              <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in-95 duration-300">
                <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
                <p className="text-blue-300 font-medium text-sm">Belge Okunuyor...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className={`p-4 rounded-full transition-colors ${isDragging ? 'bg-blue-500/20 text-blue-400' : 'bg-white/10 text-slate-300'}`}>
                  <FileText className="w-8 h-8" />
                </div>
                <p className="text-slate-200 font-medium text-sm">Normal Yaka Kartı</p>
                <p className="text-xs text-slate-400">Sürükleyin veya tıklayın</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div 
          className={`relative border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center text-center transition-all cursor-pointer ${borderClass(isDragging)}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files ? e.dataTransfer.files[0] : null as any); }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input type="file" className="hidden" ref={fileInputRef} onChange={(e) => e.target.files && handleFile(e.target.files[0])} accept="image/jpeg, image/png, image/webp" />
          
          {isLoading ? (
            <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in-95 duration-300">
              <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
              <p className="text-blue-300 font-medium tracking-wide">Yapay Zeka (OCR) Görseli İşliyor...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className={`p-4 rounded-full transition-colors ${isDragging ? 'bg-blue-500/20 text-blue-400' : 'bg-white/10 text-slate-300'}`}>
                <UploadCloud className="w-10 h-10" />
              </div>
              <p className="text-slate-200 font-medium text-lg">Yaka kartı fotoğrafını sürükleyin</p>
              <p className="text-sm text-slate-400">veya <span className="text-blue-400 font-medium">bilgisayardan seçmek için tıklayın</span></p>
              <p className="text-xs text-slate-500 mt-2 font-mono">JPG, PNG (Max 5MB)</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
