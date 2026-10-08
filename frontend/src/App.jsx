import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import {
  Search,
  Activity,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2,
  ShieldAlert,
  Sun,
  Moon,
  Download,
  Sparkles,
  Copy,
  Check,
  ExternalLink,
  Filter,
  Layers,
  Eye,
  FileCode,
  Accessibility,
  Zap,
  Globe,
  Printer,
  Scale,
  BadgeAlert,
  Share2,
  X,
  Volume2,
  VolumeX,
  Play,
  Square,
  Network,
  ArrowRight,
  Image as ImageIcon,
  ImageOff,
  Code,
  Target,
  Link2
} from 'lucide-react';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const API_BASE = 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState('');
  const [auditMode, setAuditMode] = useState('single'); // 'single' | 'domain'
  const [engine, setEngine] = useState('fast'); // 'fast' | 'dynamic'
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [siteResult, setSiteResult] = useState(null);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [isDark, setIsDark] = useState(false);
  const [activeTab, setActiveTab] = useState('report'); // 'report' | 'screenreader' | 'xray' | 'sarif'
  const [pourFilter, setPourFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedKey, setCopiedKey] = useState(null);
  const [aiLoading, setAiLoading] = useState({});
  const [aiData, setAiData] = useState({});
  const [colorVision, setColorVision] = useState('normal');
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [imgGalleryFilter, setImgGalleryFilter] = useState('all');
  const [showCode, setShowCode] = useState({});

  const toggleCode = (key) => setShowCode(prev => ({ ...prev, [key]: !prev[key] }));

  // Screen Reader Audio Simulator State
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.2);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const runAudit = async (targetUrl, selectedEngine = engine, mode = auditMode) => {
    const finalUrl = (targetUrl || url).trim();
    if (!finalUrl) return;

    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setSiteResult(null);
    setAiData({});

    try {
      if (mode === 'domain') {
        const response = await axios.post(`${API_BASE}/api/audit/site`, {
          url: finalUrl,
          max_pages: 5,
          engine: selectedEngine
        });
        setSiteResult(response.data);
      } else {
        const response = await axios.post(`${API_BASE}/api/audit`, {
          url: finalUrl,
          engine: selectedEngine
        });
        setResult(response.data);

        const expanded = {};
        Object.entries(response.data.results || {}).forEach(([cat, issues]) => {
          if (issues && issues.length > 0) expanded[cat] = true;
        });
        setExpandedCategories(expanded);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Unable to audit this website. Please verify the URL is reachable and allows public requests.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAuditSubmit = (e) => {
    e.preventDefault();
    runAudit(url, engine, auditMode);
  };

  const toggleCategory = (cat) => {
    setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Screen Reader Speech Synthesis Handlers
  const handlePlaySpeech = () => {
    if (!result?.screen_reader?.full_speech) return;
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(result.screen_reader.full_speech);
      utterance.rate = speechRate;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleStopSpeech = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const requestAiRemediation = async (issueKey, issue) => {
    setAiLoading(prev => ({ ...prev, [issueKey]: true }));
    try {
      const res = await axios.post(`${API_BASE}/api/remediate`, {
        html: issue.html,
        rule_id: issue.rule_id,
        wcag: issue.wcag,
        message: issue.message,
        suggestion: issue.suggestion
      });
      setAiData(prev => ({ ...prev, [issueKey]: res.data }));
    } catch (err) {
      console.error('AI Remediation failed:', err);
    } finally {
      setAiLoading(prev => ({ ...prev, [issueKey]: false }));
    }
  };

  const handleExportSarif = async () => {
    if (!result) return;
    try {
      const res = await axios.post(`${API_BASE}/api/audit/sarif`, {
        url: result.url,
        engine
      });
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      const dlUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = dlUrl;
      a.download = `a11ylens-${Date.now()}.sarif`;
      a.click();
      URL.revokeObjectURL(dlUrl);
    } catch (err) {
      alert('Failed to generate SARIF report.');
    }
  };

  const handleExportJson = () => {
    const dataToExport = siteResult || result;
    if (!dataToExport) return;
    const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
    const dlUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = dlUrl;
    a.download = `a11ylens-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(dlUrl);
  };

  const handlePrint = () => {
    window.print();
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'var(--success)';
    if (score >= 75) return 'var(--warning)';
    return 'var(--danger)';
  };

  const getFilteredCategoryIssues = (category, issues) => {
    if (!issues) return [];
    return issues.filter(issue => {
      if (pourFilter !== 'all' && issue.pour !== pourFilter) return false;
      if (severityFilter !== 'all' && issue.severity !== severityFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const inMsg = (issue.message || '').toLowerCase().includes(q);
        const inRule = (issue.rule_id || '').toLowerCase().includes(q);
        const inHtml = (issue.html || '').toLowerCase().includes(q);
        if (!inMsg && !inRule && !inHtml) return false;
      }
      return true;
    });
  };

  const radarData = result ? {
    labels: ['Perceivable', 'Operable', 'Understandable', 'Robust'],
    datasets: [
      {
        label: 'Current Website Score',
        data: [
          result.pour_scores?.perceivable ?? 100,
          result.pour_scores?.operable ?? 100,
          result.pour_scores?.understandable ?? 100,
          result.pour_scores?.robust ?? 100
        ],
        backgroundColor: 'rgba(229, 50, 45, 0.2)',
        borderColor: '#e5322d',
        pointBackgroundColor: '#e5322d',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#e5322d',
        borderWidth: 2
      },
      {
        label: 'WCAG AA Benchmark Target',
        data: [100, 100, 100, 100],
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        borderColor: '#10b981',
        borderDash: [4, 4],
        pointRadius: 0,
        borderWidth: 1.5
      }
    ]
  } : null;

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: { color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)' },
        grid: { color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)' },
        pointLabels: {
          color: isDark ? '#cbd5e1' : '#334155',
          font: { size: 11, weight: '600' }
        },
        suggestedMin: 0,
        suggestedMax: 100,
        ticks: { stepSize: 25, display: false }
      }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 12,
          color: isDark ? '#94a3b8' : '#64748b',
          font: { size: 10 }
        }
      }
    }
  };

  return (
    <div className="container">
      {/* Skip to Main Content Link (WCAG 2.4.1 Bypass Blocks) */}
      <a href="#main-search-input" className="skip-link">
        Skip to accessibility audit controls
      </a>

      {/* SVG Color Blindness Filter Definitions */}
      <svg style={{ position: 'absolute', width: 0, height: 0 }} aria-hidden="true">
        <defs>
          <filter id="protanopia">
            <feColorMatrix
              type="matrix"
              values="0.567, 0.433, 0, 0, 0
                      0.558, 0.442, 0, 0, 0
                      0,     0.242, 0.758, 0, 0
                      0,     0,     0,     1, 0"
            />
          </filter>
          <filter id="deuteranopia">
            <feColorMatrix
              type="matrix"
              values="0.625, 0.375, 0, 0, 0
                      0.7,   0.3,   0, 0, 0
                      0,     0.3,   0.7, 0, 0
                      0,     0,     0,   1, 0"
            />
          </filter>
          <filter id="tritanopia">
            <feColorMatrix
              type="matrix"
              values="0.95, 0.05,  0,     0, 0
                      0,    0.433, 0.567, 0, 0
                      0,    0.475, 0.525, 0, 0
                      0,    0,     0,     1, 0"
            />
          </filter>
          <filter id="achromatopsia">
            <feColorMatrix
              type="matrix"
              values="0.299, 0.587, 0.114, 0, 0
                      0.299, 0.587, 0.114, 0, 0
                      0.299, 0.587, 0.114, 0, 0
                      0,     0,     0,     1, 0"
            />
          </filter>
        </defs>
      </svg>

      {/* Top Navigation & Brand Header */}
      <header className="site-header">
        <div className="brand-group">
          <div className="logo-badge" aria-hidden="true">
            <Accessibility size={28} className="logo-icon" />
          </div>
          <div>
            <div className="brand-title-row">
              <h1 className="brand-title">A11yLens</h1>
            </div>
            <p className="subtitle">Every tool you need to audit, understand, and fix web accessibility, in one place.</p>
          </div>
        </div>

        <div className="header-actions">
          {(result || siteResult) && (
            <div className="export-actions">
              {result && (
                <button onClick={() => setShowBadgeModal(true)} className="btn-secondary" aria-label="Get embeddable compliance badge" title="Get embeddable compliance badge">
                  <Share2 size={15} /> Badge
                </button>
              )}
              <button onClick={handlePrint} className="btn-secondary" aria-label="Print Executive Compliance PDF report" title="Print Executive Compliance PDF">
                <Printer size={15} /> PDF
              </button>
              {result && (
                <button onClick={handleExportSarif} className="btn-secondary" aria-label="Export SARIF 2.1 for CI/CD Security" title="Export SARIF 2.1 for CI/CD Security">
                  <Download size={15} /> SARIF
                </button>
              )}
              <button onClick={handleExportJson} className="btn-secondary" aria-label="Export complete audit JSON report" title="Export complete audit JSON">
                <FileCode size={15} /> JSON
              </button>
            </div>
          )}

          <button
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {/* URL Audit Search Bar & Controls */}
      <section className="search-section" aria-label="Website Audit Form">
        <form onSubmit={handleAuditSubmit} className="search-form">
          <div className="input-wrapper">
            <input
              id="main-search-input"
              type="text"
              className="search-input"
              placeholder="Enter target website URL (e.g., https://example.com)"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              aria-label="Target website URL to audit"
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
            />
          </div>

          {/* Audit Mode Toggle (Single Page vs Multi-Page Domain Crawl) */}
          <div className="engine-toggle-group">
            <button
              type="button"
              className={`engine-btn ${auditMode === 'single' ? 'active' : ''}`}
              onClick={() => setAuditMode('single')}
              title="Audit single URL"
            >
              Single Page
            </button>
            <button
              type="button"
              className={`engine-btn ${auditMode === 'domain' ? 'active' : ''}`}
              onClick={() => setAuditMode('domain')}
              title="Crawl internal pages across entire domain"
            >
              <Network size={14} /> Domain Crawl
            </button>
          </div>

          {/* Engine Selector */}
          <div className="engine-toggle-group">
            <button
              type="button"
              className={`engine-btn ${engine === 'fast' ? 'active' : ''}`}
              onClick={() => setEngine('fast')}
              title="Static HTTP parser (<500ms, ultra-fast pre-flight)"
            >
              <Zap size={14} /> Fast
            </button>
            <button
              type="button"
              className={`engine-btn ${engine === 'dynamic' ? 'active' : ''}`}
              onClick={() => setEngine('dynamic')}
              title="Headless Chromium (Deep JS Hydration, SPAs & React/Vue)"
            >
              <Globe size={14} /> Headless
            </button>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <div className="spinner"></div>
                {auditMode === 'domain' ? 'Crawling Domain Routes...' : (engine === 'dynamic' ? 'Rendering in Chromium...' : 'Auditing DOM...')}
              </>
            ) : (
              <>
                <Search size={18} /> {auditMode === 'domain' ? 'Crawl Domain' : 'Audit Website'}
              </>
            )}
          </button>
        </form>
      </section>

      {/* Error Banner */}
      {error && (
        <div className="card error-card" role="alert">
          <AlertCircle size={22} color="var(--danger)" />
          <div>
            <strong>Audit Failed:</strong> {error}
          </div>
        </div>
      )}

      {/* Empty State / iLovePDF Tool Grid Showcase */}
      {!loading && !result && !siteResult && !error && (
        <section className="empty-state">
          <div className="hero-tagline">
            <Zap size={14} /> The All-in-One Web Accessibility Platform
          </div>
          <h2>Every tool you need for web accessibility, in one place</h2>
          <p className="empty-state-subtitle">
            100% automated WCAG 2.2 auditing, multi-page crawling, screen reader audio simulation, 
            and instant legal risk compliance — with the clean, fast utility you love.
          </p>

          <div className="tool-grid">
            {/* Tool 1: Single Page Audit */}
            <div
              className="tool-card"
              onClick={() => {
                setAuditMode('single');
                document.getElementById('main-search-input')?.focus();
              }}
              role="button"
              tabIndex={0}
              aria-label="Launch Single Page Auditor"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Search size={22} />
                  </div>
                  <span className="tool-pill">WCAG 2.2</span>
                </div>
                <div className="tool-card-body">
                  <h3>Single Page Auditor</h3>
                  <p>Audit any URL against 14+ W3C criteria including contrast ratios, touch targets, and ARIA tree compliance.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Audit Page</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 2: Domain Crawler */}
            <div
              className="tool-card"
              onClick={() => {
                setAuditMode('domain');
                document.getElementById('main-search-input')?.focus();
              }}
              role="button"
              tabIndex={0}
              aria-label="Launch Domain Crawler"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Network size={22} />
                  </div>
                  <span className="tool-pill">Multi-Page</span>
                </div>
                <div className="tool-card-body">
                  <h3>Domain Crawler</h3>
                  <p>Spider internal navigation routes across your entire domain to aggregate site-wide compliance and find systemic bugs.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Crawl Domain</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 3: Headless SPA Engine */}
            <div
              className="tool-card"
              onClick={() => {
                setEngine('dynamic');
                document.getElementById('main-search-input')?.focus();
              }}
              role="button"
              tabIndex={0}
              aria-label="Switch to Headless Chromium Engine"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Globe size={22} />
                  </div>
                  <span className="tool-pill">Headless Engine</span>
                </div>
                <div className="tool-card-body">
                  <h3>Headless SPA Scanner</h3>
                  <p>Execute client-side JavaScript via headless Chromium to audit dynamic React, Next.js, and Vue applications.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Select Engine</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 4: Screen Reader Simulator */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://example.com');
                runAudit('https://example.com', 'fast', 'single');
                setActiveTab('screenreader');
              }}
              role="button"
              tabIndex={0}
              aria-label="Launch Screen Reader Audio Simulator"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Volume2 size={22} />
                  </div>
                  <span className="tool-pill">Audio Simulator</span>
                </div>
                <div className="tool-card-body">
                  <h3>Screen Reader Sim</h3>
                  <p>Hear sequential VoiceOver & NVDA announcement feeds with speech synthesis, exposing traps and missing names.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Listen Audio</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 5: Color Vision Simulator */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://example.com');
                runAudit('https://example.com', 'fast', 'single');
                setActiveTab('xray');
              }}
              role="button"
              tabIndex={0}
              aria-label="Launch Color Vision Simulator"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Eye size={22} />
                  </div>
                  <span className="tool-pill">Vision Matrix</span>
                </div>
                <div className="tool-card-body">
                  <h3>Color Vision Filters</h3>
                  <p>Simulate Protanopia, Deuteranopia, Tritanopia, and Achromatopsia with live SVG color matrix filters.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>View Filters</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 6: Legal & Regulatory Risk Matrix */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://example.com');
                runAudit('https://example.com', 'fast', 'single');
                setActiveTab('report');
              }}
              role="button"
              tabIndex={0}
              aria-label="Open Regulatory Risk Matrix"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Scale size={22} />
                  </div>
                  <span className="tool-pill">Legal Radar</span>
                </div>
                <div className="tool-card-body">
                  <h3>Regulatory Risk Matrix</h3>
                  <p>Instant legal exposure calculation under ADA Title III, Section 508, and the European Accessibility Act (EAA 2025).</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Calculate Risk</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 7: Images & Media Gallery */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://en.wikipedia.org');
                runAudit('https://en.wikipedia.org', 'fast', 'single');
                setActiveTab('images');
              }}
              role="button"
              tabIndex={0}
              aria-label="Inspect Real Webpage Images & Media"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <ImageIcon size={22} />
                  </div>
                  <span className="tool-pill">Real Assets</span>
                </div>
                <div className="tool-card-body">
                  <h3>Images & Media Gallery</h3>
                  <p>Extract all live images from any website, view real thumbnails, verify alt tags, and copy accessible tags.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>View Real Images</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 8: OASIS SARIF 2.1 */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://example.com');
                runAudit('https://example.com', 'fast', 'single');
                setActiveTab('sarif');
              }}
              role="button"
              tabIndex={0}
              aria-label="View SARIF 2.1 Export"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <FileCode size={22} />
                  </div>
                  <span className="tool-pill">CI/CD DevOps</span>
                </div>
                <div className="tool-card-body">
                  <h3>OASIS SARIF 2.1</h3>
                  <p>Standardized Static Analysis Results Interchange Format for automated CI/CD security scanning.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Export SARIF</span>
                <ArrowRight size={15} />
              </div>
            </div>

            {/* Tool 9: Live Compliance Badge */}
            <div
              className="tool-card"
              onClick={() => {
                setUrl('https://example.com');
                runAudit('https://example.com', 'fast', 'single');
                setShowBadgeModal(true);
              }}
              role="button"
              tabIndex={0}
              aria-label="Generate Compliance Badge"
            >
              <div>
                <div className="tool-card-top">
                  <div className="tool-icon-wrap">
                    <Share2 size={22} />
                  </div>
                  <span className="tool-pill">Status Badge</span>
                </div>
                <div className="tool-card-body">
                  <h3>Live Compliance Badge</h3>
                  <p>Embed real-time SVG accessibility score and compliance letter grade badges in your project documentation.</p>
                </div>
              </div>
              <div className="tool-card-footer">
                <span>Get Badge</span>
                <ArrowRight size={15} />
              </div>
            </div>
          </div>
        </section>
      )}

      {/* DOMAIN CRAWL RESULTS VIEW */}
      {siteResult && (
        <main className="dashboard-content">
          <section className="card site-summary-card">
            <div className="site-summary-header">
              <div>
                <h2>Domain Accessibility Health Report</h2>
                <span className="text-muted">Target Host: {siteResult.base_url} ({siteResult.pages_audited_count} Pages Crawled)</span>
              </div>
              <div className="site-score-pill" style={{ borderColor: getScoreColor(siteResult.site_average_score) }}>
                <span className="site-score-num" style={{ color: getScoreColor(siteResult.site_average_score) }}>
                  {siteResult.site_average_score}
                </span>
                <span className="site-score-grade">Grade {siteResult.site_grade}</span>
              </div>
            </div>

            {/* Page Comparison Table */}
            <h3 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>Page-by-Page Breakdown</h3>
            <div className="table-responsive">
              <table className="pages-table">
                <thead>
                  <tr>
                    <th>URL Route</th>
                    <th>Page Title</th>
                    <th>Score</th>
                    <th>Grade</th>
                    <th>Violations</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {siteResult.pages?.map((p, i) => (
                    <tr key={i}>
                      <td><a href={p.url} target="_blank" rel="noopener noreferrer" className="page-route-link">{p.url}</a></td>
                      <td>{p.page_title}</td>
                      <td>
                        <span className="score-badge" style={{ color: getScoreColor(p.score) }}>
                          {p.score}/100
                        </span>
                      </td>
                      <td><strong>{p.grade}</strong></td>
                      <td>{p.total_issues}</td>
                      <td>
                        <button
                          className="btn-secondary"
                          onClick={() => {
                            setUrl(p.url);
                            setAuditMode('single');
                            runAudit(p.url, engine, 'single');
                          }}
                        >
                          Deep Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Top Systemic Violations Across Domain */}
            {siteResult.systemic_violations && siteResult.systemic_violations.length > 0 && (
              <div style={{ marginTop: '2rem' }}>
                <h3>Top Systemic Defects Across Domain</h3>
                <p className="text-muted text-sm">Recurring violations affecting multiple routes across this website:</p>
                <div className="systemic-grid">
                  {siteResult.systemic_violations.map((item, idx) => (
                    <div key={idx} className="systemic-card">
                      <div className="systemic-top">
                        <span className="badge badge-wcag">WCAG {item.wcag}</span>
                        <span className="systemic-count">{item.count} occurrences</span>
                      </div>
                      <p className="systemic-msg">{item.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </main>
      )}

      {/* SINGLE-PAGE AUDIT RESULTS VIEW */}
      {result && (
        <main className="dashboard-content">
          {/* Real Target Website Identity & Live Assets Banner */}
          <section className="card site-identity-card">
            <div className="site-identity-main">
              <div className="site-identity-icon-wrap">
                {result.page_meta?.favicon ? (
                  <img
                    src={result.page_meta.favicon}
                    alt=""
                    className="site-favicon"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div
                  className="site-favicon-fallback"
                  style={{ display: result.page_meta?.favicon ? 'none' : 'flex' }}
                >
                  <Globe size={22} />
                </div>
              </div>
              <div className="site-identity-text">
                <div className="site-title-row">
                  <h2 className="site-identity-title">{result.page_title || result.url}</h2>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="site-external-badge"
                    title="Open live website in new tab"
                  >
                    <span>{result.url}</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
                {result.page_meta?.description && (
                  <p className="site-identity-desc">{result.page_meta.description}</p>
                )}
              </div>
            </div>

            <div className="site-identity-stats">
              <div className="site-stat-chip">
                <ImageIcon size={14} color="var(--primary)" />
                <span><strong>{result.page_meta?.images_count ?? result.page_images?.length ?? 0}</strong> Images</span>
              </div>
              <div className="site-stat-chip">
                <Globe size={14} color="var(--primary)" />
                <span><strong>{result.page_meta?.links_count ?? 0}</strong> Links</span>
              </div>
              <div className="site-stat-chip">
                <Layers size={14} color="var(--primary)" />
                <span><strong>{result.page_meta?.headings_count ?? 0}</strong> Headings</span>
              </div>
              <div className="site-stat-chip">
                <Activity size={14} color="var(--primary)" />
                <span><strong>{result.stats?.total_elements_scanned ?? 0}</strong> DOM Nodes</span>
              </div>
            </div>
          </section>

          {/* Executive KPI Overview Grid */}
          <section className="executive-grid">
            {/* Score Card */}
            <div className="card score-card">
              <div
                className="score-circle"
                style={{
                  '--score-color': getScoreColor(result.score),
                  '--score-pct': `${result.score}%`
                }}
              >
                <span className="score-value">{result.score}</span>
                <span className="score-denominator">/ 100</span>
              </div>
              <div className="grade-badge" style={{ borderColor: getScoreColor(result.score) }}>
                Grade: <strong>{result.grade}</strong>
              </div>
              <p className="score-status-text">{result.status}</p>
              <div className="score-meta">
                <span className="engine-tag">{result.engine_used}</span>
                <span>•</span>
                <span>{result.stats?.total_elements_scanned || 0} Nodes</span>
                <span>•</span>
                <span>{result.stats?.duration_ms || 0} ms</span>
              </div>
            </div>

            {/* POUR Radar Chart Card */}
            <div className="card radar-card">
              <div className="radar-header">
                <h3>POUR Compliance Radar</h3>
                <span className="text-muted text-sm">W3C 4 Pillars Diagnostic</span>
              </div>
              <div className="radar-canvas-wrap">
                {radarData && <Radar data={radarData} options={radarOptions} />}
              </div>
            </div>

            {/* Violations & Legal Risk Card */}
            <div className="card stats-card">
              <h3>Legal & Regulatory Radar</h3>
              
              <div className="regulatory-badges">
                <div className="reg-badge-item">
                  <span className="reg-name"><Scale size={14} /> ADA Title III Risk</span>
                  <span className={`reg-status reg-status-${(result.regulatory?.ada_risk || '').toLowerCase().replace(/\s+/g, '-')}`}>
                    {result.regulatory?.ada_risk || 'Low Risk'}
                  </span>
                </div>
                <div className="reg-badge-item">
                  <span className="reg-name"><BadgeAlert size={14} /> Section 508</span>
                  <span className="reg-status reg-status-neutral">
                    {result.regulatory?.section_508 || 'Likely Compliant'}
                  </span>
                </div>
                <div className="reg-badge-item">
                  <span className="reg-name"><Globe size={14} /> EAA 2025</span>
                  <span className="reg-status reg-status-neutral">
                    {result.regulatory?.eaa_2025 || 'Ready'}
                  </span>
                </div>
              </div>

              <div className="severity-row">
                <div className="sev-box sev-critical">
                  <span className="sev-count">{result.stats?.severity?.critical || 0}</span>
                  <span className="sev-title">Critical</span>
                </div>
                <div className="sev-box sev-serious">
                  <span className="sev-count">{result.stats?.severity?.serious || 0}</span>
                  <span className="sev-title">Serious</span>
                </div>
                <div className="sev-box sev-moderate">
                  <span className="sev-count">{result.stats?.severity?.moderate || 0}</span>
                  <span className="sev-title">Moderate</span>
                </div>
                <div className="sev-box sev-minor">
                  <span className="sev-count">{result.stats?.severity?.minor || 0}</span>
                  <span className="sev-title">Minor</span>
                </div>
              </div>

              <div className="target-url-info">
                <span className="text-muted text-sm">Target:</span>
                <a href={result.url} target="_blank" rel="noopener noreferrer" className="url-link">
                  {result.page_title || result.url} <ExternalLink size={14} />
                </a>
              </div>
            </div>
          </section>

          {/* Navigation Tabs */}
          <div className="tab-bar">
            <button
              className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
              onClick={() => setActiveTab('report')}
            >
              <Layers size={18} /> Findings & Diffs ({result.stats?.total_issues || 0})
            </button>
            <button
              className={`tab-btn ${activeTab === 'images' ? 'active' : ''}`}
              onClick={() => setActiveTab('images')}
            >
              <ImageIcon size={18} /> Images & Media ({result.page_images?.length || 0})
            </button>
            <button
              className={`tab-btn ${activeTab === 'screenreader' ? 'active' : ''}`}
              onClick={() => setActiveTab('screenreader')}
            >
              <Volume2 size={18} /> Screen Reader Audio Sim
            </button>
            <button
              className={`tab-btn ${activeTab === 'xray' ? 'active' : ''}`}
              onClick={() => setActiveTab('xray')}
            >
              <Eye size={18} /> X-Ray & Vision Simulator
            </button>
            <button
              className={`tab-btn ${activeTab === 'sarif' ? 'active' : ''}`}
              onClick={() => setActiveTab('sarif')}
            >
              <FileCode size={18} /> SARIF CI/CD Spec
            </button>
          </div>

          {/* TAB 1: Audit Report & Interactive Diffs */}
          {activeTab === 'report' && (
            <section className="report-section">
              {/* Filter and Search Toolbar */}
              <div className="card filter-bar">
                <div className="filter-input-wrap">
                  <Filter size={16} className="filter-icon" />
                  <input
                    type="text"
                    className="filter-search-input"
                    placeholder="Search violations by keyword or rule ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                <div className="filter-group">
                  <span className="filter-label">POUR:</span>
                  {['all', 'Perceivable', 'Operable', 'Understandable', 'Robust'].map((p) => (
                    <button
                      key={p}
                      className={`filter-pill ${pourFilter === p ? 'active' : ''}`}
                      onClick={() => setPourFilter(p)}
                    >
                      {p === 'all' ? 'All' : p}
                    </button>
                  ))}
                </div>

                <div className="filter-group">
                  <span className="filter-label">Severity:</span>
                  {['all', 'critical', 'serious', 'moderate', 'minor'].map((s) => (
                    <button
                      key={s}
                      className={`filter-pill ${severityFilter === s ? 'active' : ''}`}
                      onClick={() => setSeverityFilter(s)}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Categorized Issues List */}
              <div className="categories-list">
                {Object.entries(result.results || {}).map(([category, rawIssues]) => {
                  const filteredIssues = getFilteredCategoryIssues(category, rawIssues);
                  const totalInCat = rawIssues.length;
                  const isExpanded = expandedCategories[category];

                  if (pourFilter !== 'all' || severityFilter !== 'all' || searchQuery.trim()) {
                    if (filteredIssues.length === 0) return null;
                  }

                  return (
                    <div key={category} className="card category-card">
                      <div className="category-header" onClick={() => toggleCategory(category)}>
                        <div className="category-title">
                          {totalInCat === 0 ? (
                            <CheckCircle2 size={22} color="var(--success)" />
                          ) : (
                            <ShieldAlert
                              size={22}
                              color={totalInCat > 3 ? 'var(--danger)' : 'var(--warning)'}
                            />
                          )}
                          <span className="cat-name">{category}</span>
                        </div>

                        <div className="cat-actions">
                          <span
                            className={`badge ${
                              totalInCat === 0
                                ? 'badge-success'
                                : totalInCat < 4
                                ? 'badge-warning'
                                : 'badge-danger'
                            }`}
                          >
                            {filteredIssues.length} / {totalInCat} {totalInCat === 1 ? 'Issue' : 'Issues'}
                          </span>
                          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </div>
                      </div>

                      {isExpanded && filteredIssues.length > 0 && (
                        <div className="issue-list">
                          {filteredIssues.map((issue, idx) => {
                            const issueKey = `${category}-${idx}`;
                            const isAiLoading = aiLoading[issueKey];
                            const aiResult = aiData[issueKey];

                            return (
                              <div key={idx} className="issue-card">
                                {/* Badges Header */}
                                <div className="issue-meta-row">
                                  <span className={`badge sev-badge-${issue.severity}`}>
                                    {issue.severity?.toUpperCase()}
                                  </span>
                                  <span className="badge badge-wcag">WCAG {issue.wcag}</span>
                                  <span className="badge badge-level">Level {issue.level || 'A'}</span>
                                  <span className="badge badge-pour">{issue.pour || 'POUR'}</span>
                                  <span className="rule-id-text">{issue.rule_id}</span>
                                </div>

                                <h4 className="issue-message">{issue.message}</h4>

                                {/* PROMINENT HIGHLIGHTED MAIN CAUSE SPOTLIGHT */}
                                <div className="issue-main-cause-spotlight">
                                  <div className="spotlight-header-row">
                                    <div className="spotlight-badge-group">
                                      <span className="spotlight-tag-badge">
                                        <Target size={14} /> MAIN CAUSE
                                      </span>
                                      {issue.cause_badge && (
                                        <span className="spotlight-sub-badge">{issue.cause_badge}</span>
                                      )}
                                    </div>
                                    {issue.target_detail && (
                                      <div className="spotlight-target-badge" title={issue.target_href || issue.target_detail}>
                                        <Link2 size={13} /> {issue.target_detail}
                                      </div>
                                    )}
                                  </div>

                                  {/* Main Cause Explanation */}
                                  <div className="spotlight-cause-body">
                                    <p className="spotlight-cause-text">
                                      {issue.main_cause || issue.message}
                                    </p>
                                  </div>

                                  {/* Screen Reader Experience Callout */}
                                  {issue.screen_reader_impact && (
                                    <div className="spotlight-impact-callout">
                                      <div className="impact-callout-header">
                                        <Volume2 size={14} />
                                        <span>Screen Reader & Assistive Impact:</span>
                                      </div>
                                      <p className="impact-callout-text">{issue.screen_reader_impact}</p>
                                    </div>
                                  )}

                                  {/* Quick Solution Action Bar */}
                                  <div className="spotlight-solution-row">
                                    <div className="solution-content">
                                      <span className="solution-label">
                                        <Sparkles size={13} /> Recommended Direct Fix:
                                      </span>
                                      <div className="solution-code-preview">
                                        <code>{issue.recommended_fix || issue.suggestion}</code>
                                      </div>
                                    </div>
                                    <button
                                      type="button"
                                      className="btn-copy-solution"
                                      onClick={() => copyToClipboard(issue.recommended_fix || issue.suggestion, `sol-${issueKey}`)}
                                      title="Copy recommended accessible fix"
                                    >
                                      {copiedKey === `sol-${issueKey}` ? <Check size={14} /> : <Copy size={14} />}
                                      {copiedKey === `sol-${issueKey}` ? 'Copied' : 'Copy Fix'}
                                    </button>
                                  </div>
                                </div>

                                {/* Visual Image Hero Card (100% Visual, Clean, No Code Spam) */}
                                {(issue.img_src || issue.element === 'img' || (issue.rule_id && issue.rule_id.startsWith('IMG'))) && (
                                  <div className="image-issue-visual-hero">
                                    <div className="image-visual-display">
                                      {issue.img_src ? (
                                        <img
                                          src={issue.img_src}
                                          alt={issue.img_alt || 'Audited website image preview'}
                                          className="image-visual-img"
                                          onError={(e) => {
                                            e.target.style.display = 'none';
                                            if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                                          }}
                                        />
                                      ) : null}
                                      <div
                                        className="image-visual-fallback"
                                        style={{ display: issue.img_src ? 'none' : 'flex' }}
                                      >
                                        <ImageOff size={32} />
                                        <span>{issue.is_dynamic ? 'Dynamic UI Element' : 'Preview Unavailable'}</span>
                                      </div>
                                    </div>

                                    <div className="image-visual-info">
                                      <div className="image-visual-top">
                                        <h4 className="image-visual-title">
                                          Asset: {issue.img_filename || 'Image Element'}
                                        </h4>
                                        {issue.img_src && (
                                          <a
                                            href={issue.img_src}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="image-visual-url"
                                            title="Open full image in new tab"
                                          >
                                            View Asset <ExternalLink size={12} />
                                          </a>
                                        )}
                                      </div>

                                      <div className="issue-img-chips">
                                        <span className={`badge ${issue.rule_id === 'IMG_ALT_MISSING' ? 'badge-danger' : 'badge-warning'}`}>
                                          {issue.rule_id === 'IMG_ALT_MISSING' ? '❌ No Alt Attribute' : `⚠️ Non-Descriptive Alt: "${issue.img_alt}"`}
                                        </span>
                                        {issue.width && issue.height && (
                                          <span className="badge badge-neutral">{issue.width} × {issue.height}</span>
                                        )}
                                      </div>

                                      <p className="issue-suggestion" style={{ margin: 0 }}>
                                        {issue.rule_id === 'IMG_ALT_MISSING'
                                          ? 'This image is rendered on the page without alternative text. Screen reader users will hear nothing or an uninformative file path.'
                                          : `This image uses generic text ("${issue.img_alt}"). Replace it with what the image depicts so screen reader users know what is shown.`}
                                      </p>

                                      {/* Highlighted Human-Friendly Recommended Alt Text */}
                                      <div className="recommended-alt-box">
                                        <div>
                                          <span className="recommended-alt-label">Recommended Accessible Description</span>
                                          <div className="recommended-alt-val">"{issue.suggested_alt || 'Organization Emblem / Logo'}"</div>
                                        </div>
                                        <button
                                          type="button"
                                          className="btn-copy-alt"
                                          onClick={() => copyToClipboard(issue.suggested_alt || 'Organization Emblem', `alt-${issueKey}`)}
                                        >
                                          {copiedKey === `alt-${issueKey}` ? <Check size={14} /> : <Copy size={14} />}
                                          {copiedKey === `alt-${issueKey}` ? 'Copied Description' : 'Copy Description'}
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {/* Visual Color Contrast Swatches */}
                                {issue.fg_color && issue.bg_color && (
                                  <div className="issue-contrast-preview-box">
                                    <div
                                      className="contrast-swatch-sample"
                                      style={{ color: issue.fg_color, backgroundColor: issue.bg_color }}
                                    >
                                      <span>Sample Text Preview (This text has {issue.contrast_ratio}:1 contrast)</span>
                                    </div>
                                    <div className="contrast-swatches-info">
                                      <div className="swatch-detail">
                                        <span className="text-muted text-xs">Foreground:</span>
                                        <div className="swatch-bubble">
                                          <span className="swatch-dot" style={{ backgroundColor: issue.fg_color }} />
                                          <code>{issue.fg_color}</code>
                                        </div>
                                      </div>
                                      <div className="swatch-detail">
                                        <span className="text-muted text-xs">Background:</span>
                                        <div className="swatch-bubble">
                                          <span className="swatch-dot" style={{ backgroundColor: issue.bg_color }} />
                                          <code>{issue.bg_color}</code>
                                        </div>
                                      </div>
                                      <div className="swatch-detail">
                                        <span className="text-muted text-xs">Ratio:</span>
                                        <span className="badge badge-danger">{issue.contrast_ratio}:1</span>
                                        <span className="text-muted text-xs">(Requires 4.5:1)</span>
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {/* Collapsible Code Snippet Toggle (Code hidden by default!) */}
                                <div style={{ marginTop: '0.75rem' }}>
                                  <button
                                    type="button"
                                    className="btn-toggle-code"
                                    onClick={() => toggleCode(issueKey)}
                                  >
                                    <Code size={13} />
                                    <span>{showCode[issueKey] ? 'Hide Developer HTML Diff' : 'View Developer HTML Diff'}</span>
                                    {showCode[issueKey] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                                  </button>
                                </div>

                                {/* Collapsed Code Diff (Only shown when explicitly toggled) */}
                                {showCode[issueKey] && (
                                  <div style={{ marginTop: '0.75rem' }}>
                                    <div className="diff-grid">
                                      {/* Left: Original Code */}
                                      <div className="diff-panel diff-panel-original">
                                        <div className="diff-header">
                                          <span className="diff-title diff-title-original">❌ Original Violating Code</span>
                                          <button
                                            className="copy-btn"
                                            onClick={() => copyToClipboard(issue.html, `viol-${issueKey}`)}
                                            title="Copy original code"
                                          >
                                            {copiedKey === `viol-${issueKey}` ? (
                                              <Check size={13} color="var(--success)" />
                                            ) : (
                                              <Copy size={13} />
                                            )}
                                            {copiedKey === `viol-${issueKey}` ? 'Copied' : 'Copy'}
                                          </button>
                                        </div>
                                        <pre className="diff-code diff-code-original">{issue.html}</pre>
                                      </div>

                                      {/* Right: Suggested Fix */}
                                      <div className="diff-panel diff-panel-fixed">
                                        <div className="diff-header">
                                          <span className="diff-title diff-title-fixed">✅ Suggested Accessible Fix</span>
                                          <button
                                            className="copy-btn"
                                            onClick={() => copyToClipboard(issue.remediation, `fix-${issueKey}`)}
                                            title="Copy accessible fix"
                                          >
                                            {copiedKey === `fix-${issueKey}` ? (
                                              <Check size={13} color="var(--success)" />
                                            ) : (
                                              <Copy size={13} />
                                            )}
                                            {copiedKey === `fix-${issueKey}` ? 'Copied' : 'Copy Fix'}
                                          </button>
                                        </div>
                                        <pre className="diff-code diff-code-fixed">{issue.remediation}</pre>
                                      </div>
                                    </div>

                                    {/* AI Context & Deep Remediation Trigger */}
                                    <div className="ai-remediate-bar">
                                      {!aiResult ? (
                                        <button
                                          className="btn-ai"
                                          onClick={() => requestAiRemediation(issueKey, issue)}
                                          disabled={isAiLoading}
                                        >
                                          <Sparkles size={16} />
                                          {isAiLoading ? 'Synthesizing Patch...' : 'Auto-Remediate with AI'}
                                        </button>
                                      ) : (
                                        <div className="ai-result-panel">
                                          <div className="ai-result-header">
                                            <span className="ai-pill">
                                              <Sparkles size={14} /> {aiResult.mode}
                                            </span>
                                          </div>
                                          <p className="ai-explanation">{aiResult.explanation}</p>
                                          <div className="remediation-container">
                                            <pre className="remediation-code">{aiResult.remediated_code}</pre>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* TAB: Images & Media Visual Gallery */}
          {activeTab === 'images' && (
            <section className="card images-gallery-section">
              <div className="gallery-header">
                <div>
                  <h3>Extracted Webpage Images & Media ({result.page_images?.length || 0})</h3>
                  <p className="text-muted text-sm">
                    Inspect every real visual asset discovered on {result.url} and verify alternative text accessibility.
                  </p>
                </div>
                <div className="gallery-filter-pills">
                  {['all', 'missing', 'accessible', 'decorative'].map((filterMode) => (
                    <button
                      key={filterMode}
                      className={`filter-pill ${imgGalleryFilter === filterMode ? 'active' : ''}`}
                      onClick={() => setImgGalleryFilter(filterMode)}
                    >
                      {filterMode === 'all' && `All Images (${result.page_images?.length || 0})`}
                      {filterMode === 'missing' && `⚠️ Missing Alt (${(result.page_images || []).filter(i => i.status === 'missing').length})`}
                      {filterMode === 'accessible' && `✅ Accessible (${(result.page_images || []).filter(i => i.status === 'accessible').length})`}
                      {filterMode === 'decorative' && `🎨 Decorative (${(result.page_images || []).filter(i => i.status === 'decorative').length})`}
                    </button>
                  ))}
                </div>
              </div>

              {((result.page_images || []).filter(img => imgGalleryFilter === 'all' || img.status === imgGalleryFilter)).length === 0 ? (
                <div className="gallery-empty">
                  <p className="text-muted">No images found matching this filter on {result.url}.</p>
                </div>
              ) : (
                <div className="gallery-grid">
                  {(result.page_images || [])
                    .filter(img => imgGalleryFilter === 'all' || img.status === imgGalleryFilter)
                    .map((img, i) => (
                      <div key={i} className="gallery-card">
                        <div className="gallery-img-wrap">
                          <img
                            src={img.src}
                            alt={img.alt || 'Web asset preview'}
                            className="gallery-img"
                            loading="lazy"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                          <div className="gallery-img-fallback" style={{ display: 'none' }}>
                            <ImageOff size={28} />
                            <span>Preview unavailable</span>
                          </div>
                          <span
                            className={`gallery-badge ${
                              img.status === 'accessible'
                                ? 'badge-success'
                                : img.status === 'missing'
                                ? 'badge-danger'
                                : 'badge-warning'
                            }`}
                          >
                            {img.status_label}
                          </span>
                        </div>
                        <div className="gallery-card-body">
                          <div className="gallery-card-top">
                            <strong className="gallery-filename" title={img.filename}>{img.filename}</strong>
                            <a href={img.src} target="_blank" rel="noopener noreferrer" className="gallery-link" title="Open original image">
                              <ExternalLink size={13} />
                            </a>
                          </div>
                          <div className="gallery-alt-box">
                            <span className="gallery-alt-label">Alt Attribute:</span>
                            <p className="gallery-alt-text">
                              {img.status === 'missing' ? (
                                <span className="text-danger font-semibold">❌ None (Attribute missing)</span>
                              ) : img.status === 'decorative' ? (
                                <span className="text-muted"><code>alt=""</code> (Marked decorative)</span>
                              ) : (
                                <code>"{img.alt}"</code>
                              )}
                            </p>
                          </div>
                          <button
                            className="btn-secondary btn-copy-img"
                            onClick={() => copyToClipboard(
                              `<img src="${img.src}" alt="${img.alt || 'Descriptive description'}" />`,
                              `gallery-${i}`
                            )}
                          >
                            {copiedKey === `gallery-${i}` ? <Check size={13} color="var(--success)" /> : <Copy size={13} />}
                            {copiedKey === `gallery-${i}` ? 'Copied HTML' : 'Copy Accessible Tag'}
                          </button>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </section>
          )}

          {/* TAB 2: Screen Reader Audio Simulator */}
          {activeTab === 'screenreader' && (
            <section className="card screen-reader-section">
              <div className="screen-reader-header">
                <div>
                  <h3>VoiceOver & NVDA Audio Simulator</h3>
                  <p className="text-muted text-sm">
                    Experience how screen readers announce elements sequentially, exposing hidden traps, missing labels, and missing alt text.
                  </p>
                </div>

                <div className="speech-controls">
                  <div className="rate-selector">
                    <span className="rate-label">Speed:</span>
                    <button
                      className={`rate-btn ${speechRate === 1.0 ? 'active' : ''}`}
                      onClick={() => setSpeechRate(1.0)}
                    >
                      1.0x
                    </button>
                    <button
                      className={`rate-btn ${speechRate === 1.2 ? 'active' : ''}`}
                      onClick={() => setSpeechRate(1.2)}
                    >
                      1.2x
                    </button>
                    <button
                      className={`rate-btn ${speechRate === 1.6 ? 'active' : ''}`}
                      onClick={() => setSpeechRate(1.6)}
                    >
                      1.6x (Pro)
                    </button>
                  </div>

                  {isSpeaking ? (
                    <button onClick={handleStopSpeech} className="btn-primary btn-speech-stop">
                      <Square size={16} /> Stop Voice
                    </button>
                  ) : (
                    <button onClick={handlePlaySpeech} className="btn-primary btn-speech-play">
                      <Play size={16} /> Play Audio Simulation
                    </button>
                  )}
                </div>
              </div>

              {/* Announcement Transcript Feed */}
              <div className="transcript-box">
                <div className="transcript-header">
                  <span>Sequential Announcement Transcript ({result.screen_reader?.total_announced || 0} Nodes)</span>
                </div>
                <div className="transcript-list">
                  {result.screen_reader?.items?.map((item, idx) => (
                    <div
                      key={idx}
                      className={`transcript-item ${item.accessible ? 'item-accessible' : 'item-defective'}`}
                    >
                      <div className="transcript-meta">
                        <span className="transcript-idx">#{idx + 1}</span>
                        <span className={`badge ${item.accessible ? 'badge-success' : 'badge-danger'}`}>
                          {item.type.toUpperCase()}
                        </span>
                        {!item.accessible && (
                          <span className="badge badge-warning">A11Y DEFECT</span>
                        )}
                      </div>
                      <p className="transcript-text">"{item.announcement}"</p>
                      {item.html && <code className="transcript-code">{item.html}</code>}
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* TAB 3: Live X-Ray & Vision Simulator */}
          {activeTab === 'xray' && (
            <section className="card xray-section">
              <div className="xray-header">
                <div>
                  <h3>Interactive Live Sandbox & Vision Simulator</h3>
                  <p className="text-muted text-sm">
                    Simulate how color-blind and visually impaired users perceive {result.url}
                  </p>
                </div>

                <div className="vision-controls">
                  <span className="vision-label">Vision Filter:</span>
                  <select
                    className="vision-select"
                    value={colorVision}
                    onChange={(e) => setColorVision(e.target.value)}
                  >
                    <option value="normal">Normal Vision (100%)</option>
                    <option value="protanopia">Protanopia (Red-Blind / 1% males)</option>
                    <option value="deuteranopia">Deuteranopia (Green-Blind / 6% males)</option>
                    <option value="tritanopia">Tritanopia (Blue-Blind / Rare)</option>
                    <option value="achromatopsia">Achromatopsia (Total Monochromacy)</option>
                  </select>

                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary"
                  >
                    <ExternalLink size={15} /> Open Site
                  </a>
                </div>
              </div>

              <div
                className="iframe-wrapper"
                style={{
                  filter:
                    colorVision === 'normal'
                      ? 'none'
                      : `url(#${colorVision})`
                }}
              >
                <iframe
                  src={result.url}
                  title="A11yLens Live Sandbox"
                  className="sandbox-iframe"
                  sandbox="allow-scripts allow-same-origin"
                />
              </div>
            </section>
          )}

          {/* TAB 4: SARIF 2.1.0 Inspector */}
          {activeTab === 'sarif' && (
            <section className="card sarif-section">
              <div className="sarif-header">
                <div>
                  <h3>OASIS SARIF 2.1.0 Export Preview</h3>
                  <p className="text-muted text-sm">
                    Standard Static Analysis Results Interchange Format for GitHub Actions (<code>actions/upload-sarif</code>).
                  </p>
                </div>
                <button onClick={handleExportSarif} className="btn-primary">
                  <Download size={16} /> Download .sarif File
                </button>
              </div>
              <pre className="sarif-preview-box">
                {JSON.stringify(
                  {
                    $schema: 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
                    version: '2.1.0',
                    tool: {
                      driver: {
                        name: 'A11yLens',
                        semanticVersion: '2.2.0',
                        informationUri: 'https://a11ylens.org'
                      }
                    },
                    url: result.url,
                    engine: result.engine_used,
                    totalIssues: result.stats?.total_issues,
                    complianceGrade: result.grade,
                    adaRisk: result.regulatory?.ada_risk,
                    hint: 'Click Download .sarif File above to inspect full OASIS format with all driver rules.'
                  },
                  null,
                  2
                )}
              </pre>
            </section>
          )}
        </main>
      )}

      {/* Embed Badge Modal */}
      {showBadgeModal && result && (
        <div className="modal-backdrop" onClick={() => setShowBadgeModal(false)}>
          <div className="card modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Embed A11yLens Compliance Badge</h3>
              <button className="modal-close-btn" onClick={() => setShowBadgeModal(false)}>
                <X size={20} />
              </button>
            </div>
            <p className="text-muted text-sm" style={{ marginBottom: '1.25rem' }}>
              Add live compliance verification badge to your project documentation:
            </p>

            <div className="badge-preview-box">
              <img
                src={`${API_BASE}/api/badge?score=${result.score}&grade=${result.grade}`}
                alt="A11yLens Score Badge"
              />
            </div>

            <div className="badge-code-block">
              <div className="code-header">
                <span>Markdown Snippet</span>
                <button
                  className="copy-btn"
                  onClick={() =>
                    copyToClipboard(
                      `[![A11yLens Compliance](${API_BASE}/api/badge?score=${result.score}&grade=${result.grade})](https://a11ylens.org)`,
                      'modal-badge'
                    )
                  }
                >
                  {copiedKey === 'modal-badge' ? <Check size={14} color="var(--success)" /> : <Copy size={14} />}
                  {copiedKey === 'modal-badge' ? 'Copied' : 'Copy'}
                </button>
              </div>
              <pre className="issue-code">{`[![A11yLens Compliance](${API_BASE}/api/badge?score=${result.score}&grade=${result.grade})](https://a11ylens.org)`}</pre>
            </div>
          </div>
        </div>
      )}

      {/* Site Footer */}
      <footer className="site-footer">
        <div className="site-footer-links">
          <a href="https://www.w3.org/WAI/standards-guidelines/wcag/" target="_blank" rel="noopener noreferrer" className="site-footer-link">
            W3C WCAG 2.2 Standard
          </a>
          <span>•</span>
          <a href="https://www.ada.gov/resources/web-guidance/" target="_blank" rel="noopener noreferrer" className="site-footer-link">
            ADA Title III Regulations
          </a>
          <span>•</span>
          <a href="https://www.section508.gov/" target="_blank" rel="noopener noreferrer" className="site-footer-link">
            Section 508 Standards
          </a>
        </div>
        <p>
          A11yLens • The Complete All-in-One Web Accessibility Platform • Built with ❤️ for inclusive digital experiences.
        </p>
      </footer>
    </div>
  );
}

export default App;
