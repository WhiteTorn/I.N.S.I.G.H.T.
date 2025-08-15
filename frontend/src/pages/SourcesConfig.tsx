import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import type { SourceConfig } from '../types';
import { Loader2, Save, Plus, Trash2, ChevronLeft, Rss, Youtube, Send, MessageSquare, FileText } from 'lucide-react';
import { toast } from 'sonner';

type PlatformKey = keyof SourceConfig['platforms'];

type SourcesConfigProps = {
  embedded?: boolean;
  onClose?: () => void;
};

export default function SourcesConfig({ embedded = false, onClose }: SourcesConfigProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<SourceConfig | null>(null);
  const [dirty, setDirty] = useState(false);
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [pulsing] = useState<Record<string, boolean>>({});
  const [bulkEdit, setBulkEdit] = useState<{ platform: string; text: string } | null>(null);

  const EXPANDED_KEY = 'insight.sources.expanded';

  const loadExpanded = (keys: string[]): Record<string, boolean> => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem(EXPANDED_KEY) : null;
      const parsed: Record<string, boolean> | null = raw ? JSON.parse(raw) : null;
      const obj: Record<string, boolean> = {};
      keys.forEach((k) => {
        obj[k] = parsed && typeof parsed[k] === 'boolean' ? parsed[k] : true; // default expanded
      });
      return obj;
    } catch {
      const obj: Record<string, boolean> = {};
      keys.forEach((k) => (obj[k] = true));
      return obj;
    }
  };

  const saveExpanded = (obj: Record<string, boolean>) => {
    try {
      if (typeof window !== 'undefined') localStorage.setItem(EXPANDED_KEY, JSON.stringify(obj));
    } catch {}
  };

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      const res = await apiService.getSources();
      if (mounted) {
        if (res.success && res.data) {
          setConfig(res.data as SourceConfig);
        } else {
          toast.error(res.error || 'Failed to load sources configuration');
        }
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const platforms = useMemo(() => Object.keys(config?.platforms || {}), [config]) as PlatformKey[];

  useEffect(() => {
    // Initialize expanded state when config loads
    if (platforms.length) {
      const init = loadExpanded(platforms as string[]);
      setExpanded(init);
    }
  }, [platforms.length]);

  const platformIcon: Record<string, ReactNode> = {
    rss: <Rss className="w-5 h-5" />,
    youtube: <Youtube className="w-5 h-5" />,
    telegram: <Send className="w-5 h-5" />,
    reddit: <MessageSquare className="w-5 h-5" />,
  };

  const totalSources = useMemo(() => {
    if (!config) return 0;
    return Object.values(config.platforms).reduce((acc, p) => acc + (p.sources?.length || 0), 0);
  }, [config]);

  const enabledSourcesCount = useMemo(() => {
    if (!config) return 0;
    return Object.values(config.platforms).reduce((acc, p) => acc + (p.enabled ? (p.sources?.length || 0) : 0), 0);
  }, [config]);

  const togglePlatform = (platform: PlatformKey) => {
    if (!config) return;
    const next = {
      ...config,
      platforms: {
        ...config.platforms,
        [platform]: {
          ...config.platforms[platform],
          enabled: !config.platforms[platform].enabled,
        },
      },
    };
    setConfig(next);
    setDirty(true);
  };

  const addSource = (platform: PlatformKey) => {
    if (!config) return;
    const value = prompt(`Add new source to ${platform}`);
    if (!value) return;
    const next = {
      ...config,
      platforms: {
        ...config.platforms,
        [platform]: {
          ...config.platforms[platform],
          sources: [...config.platforms[platform].sources, value.trim()],
        },
      },
    };
    setConfig(next);
    setDirty(true);
  };

  const updateSource = (platform: PlatformKey, index: number, value: string) => {
    if (!config) return;
    const list = [...config.platforms[platform].sources];
    list[index] = value;
    const next = {
      ...config,
      platforms: {
        ...config.platforms,
        [platform]: {
          ...config.platforms[platform],
          sources: list,
        },
      },
    };
    setConfig(next);
    setDirty(true);
  };

  const removeSource = (platform: PlatformKey, index: number) => {
    if (!config) return;
    const list = config.platforms[platform].sources.filter((_, i) => i !== index);
    const next = {
      ...config,
      platforms: {
        ...config.platforms,
        [platform]: {
          ...config.platforms[platform],
          sources: list,
        },
      },
    };
    setConfig(next);
    setDirty(true);
  };

  const onSave = async () => {
    if (!config) return;
    setSaving(true);
    const res = await apiService.updateSources(config);
    setSaving(false);
    if (res.success) {
      toast.success('Sources configuration saved');
      setDirty(false);
    } else {
      toast.error(res.error || 'Failed to save configuration');
    }
  };

  if (loading) {
    return (
      <div className={`flex ${embedded ? 'h-48' : 'h-screen'} items-center justify-center text-gray-600`}>
        <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Loading configuration...
      </div>
    );
  }

  if (!config) {
    return (
      <div className={`flex ${embedded ? 'h-48' : 'h-screen'} items-center justify-center text-red-600`}>
        Failed to load configuration
      </div>
    );
  }

  return (
    <div className={embedded ? "bg-gray-100" : "min-h-screen bg-gray-100"}>
      <div className={embedded ? "max-w-5xl mx-auto p-6" : "max-w-5xl mx-auto p-8"}>
        {/* Back link (hidden when embedded) */}
  {!embedded && (
          <div className="mb-3">
            <button
              type="button"
              onClick={() => {
                if (window.history.length > 1) navigate(-1);
                else navigate('/briefing');
              }}
              className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ChevronLeft className="w-4 h-4 mr-1" /> Back to Briefing
            </button>
          </div>
        )}

        {/* Title and Save */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Sources Configuration</h1>
          <div className="flex items-center gap-2">
            <button
              onClick={onSave}
              disabled={!dirty || saving}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Save Changes
            </button>
          </div>
        </div>

        {/* Global Actions */}
        <div className="flex items-center gap-2 mb-3">
          <button
            onClick={() => {
              if (!config) return;
              const next = { ...config, platforms: { ...config.platforms } } as SourceConfig;
              (Object.keys(next.platforms) as string[]).forEach((p) => {
                next.platforms[p].enabled = true;
              });
              setConfig(next);
              setDirty(true);
            }}
            className="px-3 py-1.5 text-sm rounded-md border border-gray-300 bg-white hover:bg-gray-50"
          >
            Enable All
          </button>
          <button
            onClick={() => {
              if (!config) return;
              const next = { ...config, platforms: { ...config.platforms } } as SourceConfig;
              (Object.keys(next.platforms) as string[]).forEach((p) => {
                next.platforms[p].enabled = false;
              });
              setConfig(next);
              setDirty(true);
            }}
            className="px-3 py-1.5 text-sm rounded-md border border-gray-300 bg-white hover:bg-gray-50"
          >
            Disable All
          </button>
        </div>

        {/* Summary Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-4">
          <div className="grid md:grid-cols-3 gap-6 items-start">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Project</h3>
              <p className="text-sm text-gray-700">{config.metadata.name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">Version</h3>
              <p className="text-sm text-gray-700">{config.metadata.version}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-2 text-sm bg-gray-50 text-gray-700 px-3 py-2 rounded-md border border-gray-200">
                All:
                <strong className="text-gray-900 text-base">{totalSources}</strong>
              </span>
              <span className="inline-flex items-center gap-2 text-sm bg-green-50 text-green-700 px-3 py-2 rounded-md border border-green-200">
                Enabled:
                <strong className="text-green-900 text-base">{enabledSourcesCount}</strong>
              </span>
            </div>
          </div>
        </div>

        {/* Platform Dock (macOS-like) */}
        <div className="flex justify-center mb-4">
      <div className="flex items-center gap-3 px-4 py-2 rounded-2xl bg-white/80 backdrop-blur border border-gray-200 shadow-md">
            {platforms.map((platform) => {
              const enabled = config.platforms[platform].enabled;
              const ringClass = enabled ? 'ring ring-green-400 bg-green-50' : 'ring ring-gray-200 bg-gray-50';
        const pulseClass = '';
              return (
                <button
                  key={`dock-${platform}`}
                  onClick={() => {
                    // Expand and persist
                    const next = { ...expanded, [platform]: true };
                    setExpanded(next);
                    saveExpanded(next);
                    // Scroll to card
                    const el = document.getElementById(`platform-${platform}`);
                    el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
          className={`relative h-10 w-10 rounded-xl flex items-center justify-center ${ringClass} ${pulseClass} shadow-sm hover:shadow-lg transition-shadow duration-150`}
                  title={String(platform)}
                >
                  <span className={`${enabled ? 'text-green-700' : 'text-gray-600'}`}>
                    {platformIcon[platform] || <MessageSquare className="w-5 h-5" />}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Platforms */}
        <div className="space-y-6">
          {platforms.map((platform) => (
            <div key={platform} id={`platform-${platform}`} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div
                role="button"
                tabIndex={0}
                aria-expanded={!!expanded[platform]}
                onClick={() => setExpanded((prev) => { const next = { ...prev, [platform]: !prev[platform] }; saveExpanded(next); return next; })}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setExpanded((prev) => { const next = { ...prev, [platform]: !prev[platform] }; saveExpanded(next); return next; });
                  }
                }}
                className={`flex items-center justify-between p-4 border-b border-gray-200 transition-colors hover:bg-gray-50 ${expanded[platform] ? 'bg-gray-50' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-md bg-gray-100 text-gray-700 flex items-center justify-center">
                    {platformIcon[platform] || <MessageSquare className="w-5 h-5" />}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 capitalize">{platform}</h3>
                    <p className="text-xs text-gray-500">Enable platform and manage its sources</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Export removed per request */}
                  <button
                    onClick={(e) => { e.stopPropagation(); setBulkEdit({ platform: String(platform), text: config.platforms[platform].sources.join('\n') }); }}
                    className="inline-flex items-center gap-1 px-2 py-1.5 rounded-md text-sm border border-gray-300 hover:bg-gray-50"
                    title="Bulk edit sources"
                  >
                    <FileText className="w-4 h-4" />
                    Bulk Edit
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); togglePlatform(platform); }}
                    className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm border ${
                      config.platforms[platform].enabled
                        ? 'bg-green-50 text-green-700 border-green-300'
                        : 'bg-gray-50 text-gray-700 border-gray-300'
                    }`}
                  >
                    {config.platforms[platform].enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
              </div>

              {expanded[platform] && (
                <div className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-medium text-gray-900">Sources</h4>
                    <button
                      onClick={() => addSource(platform)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-gray-300 text-sm hover:bg-gray-50"
                    >
                      <Plus className="w-4 h-4" /> Add Source
                    </button>
                  </div>
                  <div className="space-y-2">
                    {config.platforms[platform].sources.map((src, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <span className="inline-flex items-center justify-center w-7 h-9 rounded-md bg-gray-100 text-gray-700 border border-gray-200 font-mono text-xs">
                          {idx + 1}
                        </span>
                        <input
                          value={src}
                          onChange={(e) => updateSource(platform, idx, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                          placeholder="Enter source identifier or URL"
                        />
                        <button
                          onClick={() => removeSource(platform, idx)}
                          className="inline-flex items-center justify-center w-9 h-9 rounded-md border border-red-300 text-red-600 hover:bg-red-50"
                          title="Remove"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    {config.platforms[platform].sources.length === 0 && (
                      <div className="text-xs text-gray-500">No sources added yet.</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      {/* Bulk Editor Modal */}
      {bulkEdit && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-2xl rounded-lg border border-gray-200 shadow-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Bulk Edit – {bulkEdit.platform}</h3>
              <button className="text-gray-600 hover:text-gray-900" onClick={() => setBulkEdit(null)}>✕</button>
            </div>
            <textarea
              className="w-full h-64 border border-gray-300 rounded-md p-3 font-mono text-sm"
              value={bulkEdit.text}
              onChange={(e) => setBulkEdit({ ...bulkEdit, text: e.target.value })}
              placeholder="One source per line"
            />
            <div className="mt-3 flex items-center justify-end gap-2">
              <button className="px-3 py-1.5 rounded-md border border-gray-300" onClick={() => setBulkEdit(null)}>Cancel</button>
              <button
                className="px-3 py-1.5 rounded-md bg-indigo-600 text-white"
                onClick={() => {
                  if (!config) return;
                  const lines = bulkEdit.text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
                  const next = { ...config } as SourceConfig;
                  next.platforms[bulkEdit.platform].sources = lines;
                  setConfig(next);
                  setDirty(true);
                  setBulkEdit(null);
                  toast.success('Sources updated');
                }}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
