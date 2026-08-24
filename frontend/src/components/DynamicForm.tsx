"use client";
import { useState } from "react";
import { Loader2 } from "lucide-react";

interface DynamicFormProps {
  onSubmit: (data: any) => void;
  isLoading: boolean;
}

export default function DynamicForm({ onSubmit, isLoading }: DynamicFormProps) {
  const [country, setCountry] = useState("spain");
  const [region, setRegion] = useState("");
  const [licenseNo, setLicenseNo] = useState("");
  const [documentType, setDocumentType] = useState("official");
  const [qrUrl, setQrUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ 
      country, 
      region: region || null, 
      license_no: licenseNo || null, 
      document_type: documentType,
      qr_url: qrUrl || null
    });
  };

  const inputClass = "w-full p-3.5 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 text-white transition-all shadow-inner placeholder-slate-400";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Ülke *</label>
          <select value={country} onChange={(e) => setCountry(e.target.value)} className={inputClass}>
            <option value="spain" className="bg-slate-800 text-white">İspanya</option>
            <option value="france" className="bg-slate-800 text-white">Fransa</option>
            <option value="italy" className="bg-slate-800 text-white">İtalya</option>
          </select>
        </div>

        {country === "spain" ? (
          <div className="animate-in fade-in zoom-in-95 duration-300">
            <label className="block text-sm font-medium text-slate-300 mb-2">Bölge (Zorunlu) *</label>
            <select value={region} onChange={(e) => setRegion(e.target.value)} className={inputClass} required>
              <option value="" className="bg-slate-800 text-white">Bölge Seçiniz</option>
              <option value="andalucia" className="bg-slate-800 text-white">Endülüs (Andalucía)</option>
              <option value="aragon" className="bg-slate-800 text-white">Aragón</option>
              <option value="asturias" className="bg-slate-800 text-white">Asturias</option>
              <option value="baleares" className="bg-slate-800 text-white">Balear Adaları (Baleares)</option>
              <option value="canarias" className="bg-slate-800 text-white">Kanarya Adaları (Canarias)</option>
              <option value="cantabria" className="bg-slate-800 text-white">Cantabria</option>
              <option value="castilla_la_mancha" className="bg-slate-800 text-white">Kastilya-La Mancha</option>
              <option value="castilla_y_leon" className="bg-slate-800 text-white">Kastilya ve Leon</option>
              <option value="catalunya" className="bg-slate-800 text-white">Katalonya (Cataluña)</option>
              <option value="extremadura" className="bg-slate-800 text-white">Extremadura</option>
              <option value="galicia" className="bg-slate-800 text-white">Galiçya (Galicia)</option>
              <option value="madrid" className="bg-slate-800 text-white">Madrid</option>
              <option value="murcia" className="bg-slate-800 text-white">Murcia</option>
              <option value="navarra" className="bg-slate-800 text-white">Navarra</option>
              <option value="pais_vasco" className="bg-slate-800 text-white">Bask Bölgesi (País Vasco)</option>
              <option value="rioja" className="bg-slate-800 text-white">La Rioja</option>
              <option value="valencia" className="bg-slate-800 text-white">Valensiya (Comunidad Valenciana)</option>
            </select>
          </div>
        ) : (
          <div className="hidden md:block"></div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Lisans Numarası</label>
          <input 
            type="text" 
            value={licenseNo} 
            onChange={(e) => setLicenseNo(e.target.value)} 
            placeholder="Örn: GT-12345 veya CG-1234567-1" 
            className={inputClass} 
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Belge Tipi</label>
          <select value={documentType} onChange={(e) => setDocumentType(e.target.value)} className={inputClass}>
            <option value="official" className="bg-slate-800 text-white">Resmi Ulusal Lisans</option>
            <option value="wftga" className="bg-slate-800 text-white">WFTGA Kartı</option>
          </select>
        </div>
      </div>

      {country === "italy" && (
        <div className="animate-in fade-in slide-in-from-bottom-2">
          <label className="block text-sm font-medium text-slate-300 mb-2">İtalya QR URL (Hızlı Doğrulama)</label>
          <input 
            type="url" 
            value={qrUrl} 
            onChange={(e) => setQrUrl(e.target.value)} 
            placeholder="https://www.ministeroturismo.gov.it/verify?id=..." 
            className={inputClass} 
          />
        </div>
      )}

      <button 
        type="submit" 
        disabled={isLoading || (country === 'spain' && !region)}
        className="w-full flex justify-center items-center gap-2 py-3.5 mt-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-xl text-white font-semibold tracking-wide transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <><Loader2 className="w-5 h-5 animate-spin" /> Sorgulanıyor...</>
        ) : "Sistemi Doğrula"}
      </button>
    </form>
  );
}
