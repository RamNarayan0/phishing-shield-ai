import { useState, useEffect, useRef } from 'react'
import { Shield, ShieldAlert, ShieldCheck, AlertTriangle, Smartphone, Chrome, Mail, Phone, Database, Server, Activity, CheckCircle2 } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('stream')
  const [manualText, setManualText] = useState('')
  const [manualResult, setManualResult] = useState(null)
  
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({ total: 0, safe: 0, suspicious: 0, high: 0, critical: 0 })
  
  // Ref to automatically scroll to the latest event
  const streamEndRef = useRef(null)
  
  const defaultApi = import.meta.env.VITE_API_URL || 
    (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? 'http://127.0.0.1:8000'
      : 'https://phishing-shield-ai-backend.onrender.com')
  const [apiUrl, setApiUrl] = useState(() => localStorage.getItem('phishing_api_url') || defaultApi)
  const [backendOnline, setBackendOnline] = useState(false)

  // Poll the backend for new events every 2 seconds
  useEffect(() => {
    let isMounted = true;
    const fetchEvents = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/events`);
        if (res.ok) {
          const data = await res.json();
          if (!isMounted) return;
          setEvents(data.events || []);
          setBackendOnline(true);
          
          // Recompute stats
          const s = { total: 0, safe: 0, suspicious: 0, high: 0, critical: 0 };
          (data.events || []).forEach(evt => {
            s.total++;
            if (evt.result.risk_score >= 80) s.critical++;
            else if (evt.result.risk_score >= 60) s.high++;
            else if (evt.result.risk_score >= 30) s.suspicious++;
            else s.safe++;
          });
          setStats(s);
        } else {
          if (isMounted) setBackendOnline(false);
        }
      } catch (err) {
        if (isMounted) setBackendOnline(false);
      }
    };
    
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [apiUrl]);

  const analyzeManual = async () => {
    if (!manualText.trim()) return;
    setLoading(true)
    try {
      const endpoint = `${apiUrl}/api/verify-message`
      const payload = { raw_text: manualText, source_platform: 'Manual Paste' }
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!response.ok) throw new Error('API request failed')
      const data = await response.json()
      setManualResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const analyzeEvent = async (rawText, source = 'Android Notification', app = 'WhatsApp', sender = 'Unknown Contact') => {
    setLoading(true)
    try {
      const endpoint = `${apiUrl}/api/verify-message`
      
      const payload = {
        raw_text: rawText,
        source_platform: source,
        sender_id: sender
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) throw new Error('API request failed')
      
      const data = await response.json()
      
      const newEvent = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 5),
        timestamp: new Date().toLocaleTimeString(),
        source_platform: source,
        application_name: app,
        sender_id: sender,
        raw_text: rawText,
        result: data
      }

      setEvents(prev => [...prev, newEvent])
      setSelectedEvent(newEvent)
      
      // Update stats
      setStats(prev => {
        const s = { ...prev, total: prev.total + 1 }
        if (data.risk_score >= 80) s.critical++
        else if (data.risk_score >= 60) s.high++
        else if (data.risk_score >= 30) s.suspicious++
        else s.safe++
        return s
      })

    } catch (err) {
      console.error("Analysis Error: ", err)
    } finally {
      setLoading(false)
      setTimeout(() => {
        streamEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  }

  const presets = [
    { label: "NORMAL MESSAGE (SAFE)", app: "WhatsApp", sender: "+91 98480 12345", text: "Hey, are you coming to college tomorrow? Let's meet near the library at 10 AM." },
    { label: "ELECTRICITY SMISHING (CRITICAL)", app: "SMS", sender: "+91 9876543210", text: "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill. Immediately contact Electricity Officer: +919876543210" },
    { label: "KBC LOTTERY CALL (+92) (CRITICAL)", app: "WhatsApp", sender: "+92 300 1234567", text: "Congratulations! Your mobile number won 25 Lakhs in Kaun Banega Crorepati WhatsApp Lottery. Contact lottery manager on WhatsApp: +923001234567" },
    { label: "UK TOLL TRAP / SHORTCODE (CRITICAL)", app: "SMS", sender: "PRIZE-ALERT", text: "WINNER!! Claim £900 cash reward. Call 09061701461 now or text WIN to 87121 to confirm." },
    { label: "SPOOFED SENDER EMAIL (CRITICAL)", app: "Email", sender: 'State Bank of India <alerts@sbi-kyc-update.top>', text: "URGENT: Your SBI net banking account is blocked. Mandatory PAN card update required." },
    { label: "FREE WEBMAIL BRAND SPOOF (CRITICAL)", app: "Email", sender: "paypal.support@gmail.com", text: "SECURITY WARNING: Unauthorized payment of $499.00 processed. If this was not you, update your password now." },
    { label: "BANK PHISHING URL (CRITICAL)", app: "Chrome", sender: "+234 802 123 4567", text: "URGENT SECURITY ALERT: Your bank account has been suspended. Verify credentials immediately: http://sbi-netbanking-verify.login-portal.com" },
    { label: "KYC WALLET FREEZE (CRITICAL)", app: "WhatsApp", sender: "+44 7911 123456", text: "KYC VERIFICATION PENDING: Your Binance crypto wallet will be frozen within 24 hours. Verify KYC now: https://binance-kyc-verify.io" },
    { label: "DELIVERY SMISHING (HIGH RISK)", app: "SMS", sender: "+1 555 019 2834", text: "FedEx Alert: Your shipment delivery failed due to unpaid customs fee ($2.99). Confirm address and pay fee here: http://fedex-redelivery-notice.info" }
  ]

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-red-500'
    if (score >= 60) return 'text-orange-500'
    if (score >= 30) return 'text-yellow-500'
    return 'text-emerald-500'
  }

  const getRiskBg = (score) => {
    if (score >= 80) return 'bg-red-500'
    if (score >= 60) return 'bg-orange-500'
    if (score >= 30) return 'bg-yellow-500'
    return 'bg-emerald-500'
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans flex flex-col">
      {/* HEADER */}
      <header className="bg-slate-900 border-b border-slate-800 p-4 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-3">
          <Shield size={32} className="text-blue-500" />
          <h1 className="text-2xl font-black tracking-widest text-slate-100">PHISHING SHIELD AI</h1>
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={() => setActiveTab('stream')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded ${activeTab === 'stream' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
          >
            Live Stream
          </button>
          <button 
            onClick={() => setActiveTab('manual')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded ${activeTab === 'manual' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
          >
            Manual Analysis
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 bg-slate-800/90 px-2.5 py-1 rounded text-xs border border-slate-700">
            <span className={`inline-block w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`}></span>
            <select 
              value={apiUrl}
              onChange={(e) => {
                setApiUrl(e.target.value);
                localStorage.setItem('phishing_api_url', e.target.value);
              }}
              className="bg-transparent text-slate-300 font-mono text-[11px] outline-none cursor-pointer"
            >
              <option value="http://127.0.0.1:8000" className="bg-slate-900 text-slate-200">Local (127.0.0.1:8000)</option>
              <option value="https://phishing-shield-ai-backend.onrender.com" className="bg-slate-900 text-slate-200">Cloud Render API</option>
            </select>
          </div>

          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs tracking-widest">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            ACTIVE
          </div>
        </div>
      </header>

      {activeTab === 'manual' ? (
        <div className="flex-1 p-6 max-w-4xl mx-auto w-full">
          <h2 className="text-xl font-bold mb-4 text-slate-100">Original Manual Paste Analyzer</h2>
          <textarea
            className="w-full h-48 bg-slate-900 border border-slate-700 rounded p-4 text-slate-200 mb-4 focus:outline-none focus:border-blue-500"
            placeholder="Paste suspicious text or URL here..."
            value={manualText}
            onChange={(e) => setManualText(e.target.value)}
          ></textarea>
          <button
            onClick={analyzeManual}
            disabled={loading || !manualText}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded mb-8 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Content'}
          </button>

          {manualResult && (
            <div className={`p-6 border-2 rounded shadow-xl ${
              manualResult.risk_score >= 80 ? 'border-red-500/50 bg-red-950/20' : 
              manualResult.risk_score >= 60 ? 'border-orange-500/50 bg-orange-950/20' : 
              manualResult.risk_score >= 30 ? 'border-yellow-500/50 bg-yellow-950/20' : 
              'border-emerald-500/50 bg-emerald-950/20'
            }`}>
              <div className="text-center mb-6">
                <div className={`text-4xl font-black tracking-widest mb-2 ${getRiskColor(manualResult.risk_score)}`}>
                  {manualResult.verdict}
                </div>
                <div className="text-2xl font-mono text-slate-300 font-bold">
                  {manualResult.risk_score} <span className="text-sm text-slate-500">/ 100</span>
                </div>
              </div>
              <div className="bg-slate-950 border border-slate-800 rounded p-4 mb-4">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Detected Signals</h3>
                {manualResult.reasons.length > 0 ? (
                  <ul className="space-y-2">
                    {manualResult.reasons.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <span className={getRiskColor(manualResult.risk_score)}>✓</span> {r}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500 italic">No suspicious signals detected.</p>
                )}
              </div>

              {manualResult.extracted_phones && manualResult.extracted_phones.length > 0 && (
                <div className="bg-slate-950 border border-slate-800 rounded p-4 mb-4">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <Phone size={14} className="text-amber-400" /> Extracted Phone Numbers
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {manualResult.extracted_phones.map((p, i) => (
                      <span key={i} className="px-2 py-1 text-xs font-mono bg-slate-900 border border-amber-800 text-amber-300 rounded">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {manualResult.extracted_emails && manualResult.extracted_emails.length > 0 && (
                <div className="bg-slate-950 border border-slate-800 rounded p-4 mb-4">
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                    <Mail size={14} className="text-purple-400" /> Extracted Email Addresses
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {manualResult.extracted_emails.map((e, i) => (
                      <span key={i} className="px-2 py-1 text-xs font-mono bg-slate-900 border border-purple-800 text-purple-300 rounded">
                        {e}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div className={`p-3 rounded font-bold text-center text-xs tracking-widest uppercase ${getRiskBg(manualResult.risk_score)} text-slate-950`}>
                RECOMMENDED ACTION: {manualResult.recommended_action.replace(/_/g, ' ')}
              </div>
            </div>
          )}
        </div>
      ) : (
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* LEFT PANEL: SOURCES & DEMO CONTROLS */}
        <div className="lg:col-span-3 border-r border-slate-800 bg-slate-900 p-4 flex flex-col gap-6 overflow-y-auto">
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Connected Sources</h3>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-sm font-semibold text-slate-300">
                <Smartphone size={18} className="text-emerald-500" /> Android Notifications
              </li>
              <li className="flex items-center gap-3 text-sm font-semibold text-slate-300">
                <Chrome size={18} className="text-emerald-500" /> Chrome Extension
              </li>
              <li className="flex items-center gap-3 text-sm font-semibold text-slate-500">
                <Mail size={18} /> Gmail / API (Future)
              </li>
            </ul>
          </div>

          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Simulate Phishing Attacks</h3>
            <div className="flex flex-col gap-2">
              {presets.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => analyzeEvent(preset.text, `${preset.app} Interceptor`, preset.app, preset.sender)}
                  disabled={loading}
                  className={`text-left p-2.5 rounded text-xs font-bold transition-all border ${
                    preset.label.includes('BANK') || preset.label.includes('PAYPAL') || preset.label.includes('KYC')
                      ? 'bg-red-950/40 border-red-800/60 text-red-300 hover:bg-red-900/50'
                      : preset.label.includes('DELIVERY') || preset.label.includes('LOTTERY')
                      ? 'bg-orange-950/40 border-orange-800/60 text-orange-300 hover:bg-orange-900/50'
                      : preset.label.includes('NORMAL')
                      ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300 hover:bg-emerald-900/50'
                      : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>{preset.label}</span>
                    <span className="text-[10px] opacity-75 font-mono">[{preset.app}]</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-slate-800">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Live Statistics</h3>
            <div className="grid grid-cols-2 gap-2 text-center text-xs font-bold">
              <div className="bg-slate-950 p-2 rounded border border-slate-800">TOTAL: {stats.total}</div>
              <div className="bg-emerald-950/30 text-emerald-500 p-2 rounded border border-emerald-900/50">SAFE: {stats.safe}</div>
              <div className="bg-yellow-950/30 text-yellow-500 p-2 rounded border border-yellow-900/50">SUSP: {stats.suspicious}</div>
              <div className="bg-red-950/30 text-red-500 p-2 rounded border border-red-900/50">CRIT: {stats.critical}</div>
            </div>
          </div>
        </div>

        {/* CENTER PANEL: LIVE EVENT STREAM */}
        <div className="lg:col-span-5 border-r border-slate-800 bg-slate-950 flex flex-col">
          <div className="p-4 border-b border-slate-800 bg-slate-900/50">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Live Threat Stream</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {events.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600">
                <Activity size={48} className="mb-4 opacity-20" />
                <p className="text-sm font-semibold uppercase tracking-widest">Waiting for events...</p>
              </div>
            ) : (
              events.map((evt) => (
                <div 
                  key={evt.id} 
                  onClick={() => setSelectedEvent(evt)}
                  className={`p-3 rounded border cursor-pointer transition-all ${
                    selectedEvent?.id === evt.id ? 'bg-slate-800 border-blue-500 shadow-lg' : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${getRiskBg(evt.result.risk_score)}`}></div>
                      <span className="text-xs font-bold text-slate-300">{evt.application_name}</span>
                    </div>
                    <span className="text-xs text-slate-500 font-mono">{evt.timestamp}</span>
                  </div>
                  <p className="text-sm text-slate-400 line-clamp-2 italic mb-2">"{evt.raw_text}"</p>
                  <div className="flex justify-between items-center">
                    <span className={`text-xs font-bold tracking-widest ${getRiskColor(evt.result.risk_score)}`}>
                      {evt.result.verdict}
                    </span>
                    <span className="text-xs font-mono text-slate-500">{evt.result.risk_score}/100</span>
                  </div>
                </div>
              ))
            )}
            <div ref={streamEndRef} />
          </div>
        </div>

        {/* RIGHT PANEL: SELECTED EVENT & SYSTEM STATUS */}
        <div className="lg:col-span-4 bg-slate-900 flex flex-col h-full overflow-hidden">
          
          {/* SYSTEM STATUS ROW */}
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">System Status</h3>
            <div className="flex gap-4 text-[10px] font-bold tracking-widest text-emerald-500">
              <span className="flex items-center gap-1"><CheckCircle2 size={12}/> API</span>
              <span className="flex items-center gap-1"><CheckCircle2 size={12}/> ML</span>
              <span className="flex items-center gap-1"><CheckCircle2 size={12}/> URL</span>
            </div>
          </div>

          {/* SELECTED EVENT DETAILS */}
          <div className="flex-1 overflow-y-auto p-6">
            {!selectedEvent ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 text-sm font-semibold uppercase tracking-widest">
                Select an event to view details
              </div>
            ) : (
              <div className="space-y-6">
                
                {/* META */}
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Event Metadata</h3>
                  <div className="bg-slate-950 border border-slate-800 rounded p-3 text-xs font-mono text-slate-400 space-y-1">
                    <div><span className="text-slate-600">Source:</span> {selectedEvent.source_platform}</div>
                    <div><span className="text-slate-600">App:</span> {selectedEvent.application_name}</div>
                    <div><span className="text-slate-600">Time:</span> {selectedEvent.timestamp}</div>
                  </div>
                </div>

                {/* VERDICT BANNER */}
                <div className={`p-4 border-2 rounded flex flex-col items-center justify-center py-6 shadow-xl ${
                  selectedEvent.result.risk_score >= 80 ? 'border-red-500/50 bg-red-950/20' : 
                  selectedEvent.result.risk_score >= 60 ? 'border-orange-500/50 bg-orange-950/20' : 
                  selectedEvent.result.risk_score >= 30 ? 'border-yellow-500/50 bg-yellow-950/20' : 
                  'border-emerald-500/50 bg-emerald-950/20'
                }`}>
                  <div className={`text-4xl font-black tracking-widest mb-2 ${getRiskColor(selectedEvent.result.risk_score)}`}>
                    {selectedEvent.result.verdict}
                  </div>
                  <div className="text-2xl font-mono text-slate-300 font-bold">
                    {selectedEvent.result.risk_score} <span className="text-sm text-slate-500">/ 100</span>
                  </div>
                </div>

                {/* RAW MESSAGE */}
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Intercepted Content</h3>
                  <div className="bg-slate-950 border border-slate-800 rounded p-4 text-sm text-slate-300 whitespace-pre-wrap italic">
                    "{selectedEvent.raw_text}"
                  </div>
                </div>

                {/* REASONS */}
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Detected Signals</h3>
                  <div className="bg-slate-950 border border-slate-800 rounded p-4">
                    {selectedEvent.result.reasons.length > 0 ? (
                      <ul className="space-y-2">
                        {selectedEvent.result.reasons.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                            <span className={getRiskColor(selectedEvent.result.risk_score)}>✓</span> {r}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-slate-500 italic">No suspicious signals detected.</p>
                    )}
                  </div>
                </div>
                
                {/* URLS */}
                {selectedEvent.result.extracted_urls && selectedEvent.result.extracted_urls.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Analyzed URLs</h3>
                    <div className="bg-slate-950 border border-slate-800 rounded p-4 space-y-2">
                      {selectedEvent.result.extracted_urls.map((u, i) => (
                        <div key={i} className="text-xs text-blue-400 font-mono break-all bg-slate-900 p-2 rounded">
                          {u}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* PHONES */}
                {selectedEvent.result.extracted_phones && selectedEvent.result.extracted_phones.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                      <Phone size={14} className="text-amber-400" /> Analyzed Phone Numbers
                    </h3>
                    <div className="bg-slate-950 border border-slate-800 rounded p-4 space-y-2">
                      {selectedEvent.result.extracted_phones.map((p, i) => (
                        <div key={i} className="text-xs text-amber-400 font-mono flex items-center justify-between bg-slate-900 p-2 rounded">
                          <span>{p}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800">Scanned Pattern</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* EMAILS */}
                {selectedEvent.result.extracted_emails && selectedEvent.result.extracted_emails.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                      <Mail size={14} className="text-purple-400" /> Analyzed Email Senders
                    </h3>
                    <div className="bg-slate-950 border border-slate-800 rounded p-4 space-y-2">
                      {selectedEvent.result.extracted_emails.map((e, i) => (
                        <div key={i} className="text-xs text-purple-400 font-mono flex items-center justify-between bg-slate-900 p-2 rounded">
                          <span>{e}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950/60 text-purple-300 border border-purple-800">Spoof Check</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* ML ENGINE / RISK BREAKDOWN */}
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Engine Sub-Scores</h3>
                  <div className="bg-slate-950 border border-slate-800 rounded p-4 text-xs font-mono space-y-3">
                    <div>
                      <div className="flex justify-between mb-1"><span className="text-slate-400">ML (TF-IDF + LogReg)</span><span className="text-blue-400">{Math.round(selectedEvent.result.ml_score * 100)}%</span></div>
                      <div className="w-full bg-slate-900 rounded h-1.5"><div className="bg-blue-500 h-1.5 rounded" style={{width: `${Math.round(selectedEvent.result.ml_score * 100)}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1"><span className="text-slate-400">Heuristics Engine</span><span className="text-purple-400">{selectedEvent.result.heuristic_score}%</span></div>
                      <div className="w-full bg-slate-900 rounded h-1.5"><div className="bg-purple-500 h-1.5 rounded" style={{width: `${selectedEvent.result.heuristic_score}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1"><span className="text-slate-400">URL Analysis</span><span className="text-amber-400">{selectedEvent.result.url_score}%</span></div>
                      <div className="w-full bg-slate-900 rounded h-1.5"><div className="bg-amber-500 h-1.5 rounded" style={{width: `${selectedEvent.result.url_score}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1"><span className="text-slate-400">Sender / Vector Check</span><span className="text-rose-400">{selectedEvent.result.sender_score || 0}%</span></div>
                      <div className="w-full bg-slate-900 rounded h-1.5"><div className="bg-rose-500 h-1.5 rounded" style={{width: `${selectedEvent.result.sender_score || 0}%`}}></div></div>
                    </div>
                  </div>
                </div>

                {/* RECOMMENDATION */}
                <div className={`p-3 rounded font-bold text-center text-xs tracking-widest uppercase ${getRiskBg(selectedEvent.result.risk_score)} text-slate-950`}>
                  RECOMMENDED ACTION: {selectedEvent.result.recommended_action.replace(/_/g, ' ')}
                </div>
                
              </div>
            )}
          </div>
        </div>
      </div>
      )}
    </div>
  )
}

export default App
