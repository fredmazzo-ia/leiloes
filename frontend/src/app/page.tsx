'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Auction = {
  id: number;
  external_id: string;
  source: string;
  title: string;
  url: string | null;
  lots_count: number;
  updated_at: string;
};

type Stats = { total_auctions: number; total_lots: number } | null;

type ScrapeResult = {
  status: string;
  total_auctions: number;
  total_lots: number;
  by_source?: Record<string, { auctions: number; lots: number }>;
  errors?: Array<{ source: string; error: string }>;
};

export default function Home() {
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [stats, setStats] = useState<Stats>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<string>('');
  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [scrapeResult, setScrapeResult] = useState<ScrapeResult | null>(null);
  const [scrapeError, setScrapeError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    Promise.all([
      fetch(`${API_URL}/api/auctions?${params}`).then((r) => (r.ok ? r.json() : Promise.reject(new Error('Falha ao carregar')))),
      fetch(`${API_URL}/api/stats`).then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([data, statsData]) => {
        setAuctions(data);
        setStats(statsData);
        setError(null);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [source]);

  const formatDate = (s: string) => {
    try {
      return new Date(s).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
    } catch {
      return s;
    }
  };

  const runScrape = async () => {
    setScrapeLoading(true);
    setScrapeResult(null);
    setScrapeError(null);
    try {
      const res = await fetch(`${API_URL}/api/run-scrape`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Falha ao rodar scrape');
      setScrapeResult(data);
      setLoading(true);
      const [auctionsData, statsData] = await Promise.all([
        fetch(`${API_URL}/api/auctions${source ? `?source=${source}` : ''}`).then((r) => (r.ok ? r.json() : [])),
        fetch(`${API_URL}/api/stats`).then((r) => (r.ok ? r.json() : null)),
      ]);
      setAuctions(auctionsData);
      setStats(statsData);
    } catch (e) {
      setScrapeError(e instanceof Error ? e.message : 'Erro ao rodar scrape');
    } finally {
      setScrapeLoading(false);
      setLoading(false);
    }
  };

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>Fonte:</span>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            style={{ padding: '0.5rem 0.75rem', borderRadius: 6, border: '1px solid #ccc' }}
          >
            <option value="">Todas</option>
            <option value="calil">Calil</option>
            <option value="vegas">Vegas</option>
          </select>
        </label>
        <button
          type="button"
          onClick={runScrape}
          disabled={scrapeLoading}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 6,
            border: '1px solid #1a1a2e',
            background: scrapeLoading ? '#ccc' : '#1a1a2e',
            color: '#fff',
            fontWeight: 600,
            cursor: scrapeLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {scrapeLoading ? 'Rodando scrape...' : 'Rodar scrape agora'}
        </button>
        <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer" style={{ color: '#1a1a2e', fontSize: '0.9rem' }}>
          API Docs →
        </a>
      </div>

      {scrapeError && <p style={{ color: 'crimson', marginBottom: '1rem' }}>{scrapeError}</p>}
      {scrapeResult && (
        <p style={{ marginBottom: '1rem', padding: '0.75rem 1rem', background: '#e8f5e9', borderRadius: 8, color: '#1b5e20' }}>
          Scrape concluído: <strong>{scrapeResult.total_auctions}</strong> leilão(ões), <strong>{scrapeResult.total_lots}</strong> lote(s).
          {scrapeResult.by_source && Object.entries(scrapeResult.by_source).map(([name, v]) => (
            <span key={name} style={{ marginLeft: '0.5rem' }}> {name}: {v.auctions}/{v.lots}</span>
          ))}
        </p>
      )}

      {loading && <p>Carregando leilões...</p>}
      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {!loading && !error && auctions.length === 0 && (
        <p style={{ color: '#666' }}>
          Nenhum leilão no banco. Use o botão <strong>Rodar scrape agora</strong> acima para buscar leilões (Calil e Vegas).
        </p>
      )}

      {!loading && stats && (
        <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
          <strong>{stats.total_auctions}</strong> leilão(ões) · <strong>{stats.total_lots}</strong> lote(s) no banco
        </p>
      )}

      {!loading && !error && auctions.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '1rem' }}>
          {auctions.map((a) => (
            <li
              key={a.id}
              style={{
                background: '#fff',
                borderRadius: 8,
                padding: '1rem 1.25rem',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                border: '1px solid #eee',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#666', marginRight: '0.5rem' }}>
                    {a.source}
                  </span>
                  <strong>{a.title}</strong>
                </div>
                <span style={{ fontSize: '0.85rem', color: '#666' }}>{a.lots_count} lote(s)</span>
              </div>
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#666', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
                <span>Atualizado: {formatDate(a.updated_at)}</span>
                {a.lots_count > 0 && (
                  <Link href={`/leilao/${a.id}`} style={{ color: '#1a1a2e', fontWeight: 500 }}>
                    Ver lotes →
                  </Link>
                )}
                {a.url && (
                  <a href={a.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1a1a2e' }}>
                    Ver no site
                  </a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
