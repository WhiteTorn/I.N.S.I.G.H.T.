import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';
import type { SourceConfig } from '../types';
import { CheckCircle2, ChevronLeft, Loader2, Plus, Save, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

type PlatformKey = keyof SourceConfig['platforms'];

export default function SourcesConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<SourceConfig | null>(null);
  const [dirty, setDirty] = useState(false);

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
      <div className="flex h-screen items-center justify-center text-gray-600">
        <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Loading configuration...
      </div>
    );
  }

  if (!config) {
    return (
      <div className="flex h-screen items-center justify-center text-red-600">
        Failed to load configuration
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Link to="/" className="text-gray-600 hover:text-gray-900 inline-flex items-center">
              <ChevronLeft className="w-4 h-4 mr-1" /> Back
            </Link>
            <h1 className="text-2xl font-semibold text-gray-900">Sources Configuration</h1>
          </div>
          <button
            onClick={onSave}
            disabled={!dirty || saving}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Changes
          </button>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-900">Project</h3>
              <p className="text-xs text-gray-500">{config.metadata.name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">Version</h3>
              <p className="text-xs text-gray-500">{config.metadata.version}</p>
            </div>
            <div className="flex items-center gap-2 text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-2">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-sm">Validated configuration</span>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {platforms.map((platform) => (
            <div key={platform} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div>
                  <h3 className="font-medium text-gray-900 capitalize">{platform}</h3>
                  <p className="text-xs text-gray-500">Enable platform and manage its sources</p>
                </div>
                <button
                  onClick={() => togglePlatform(platform)}
                  className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm border ${
                    config.platforms[platform].enabled
                      ? 'bg-green-50 text-green-700 border-green-300'
                      : 'bg-gray-50 text-gray-700 border-gray-300'
                  }`}
                >
                  {config.platforms[platform].enabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>

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
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
