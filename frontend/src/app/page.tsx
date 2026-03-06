'use client';

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

export default function Home() {
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<string>('');

  useEffect(() => {
    const params = new URLSearchParams();
    if (source) params.set('source', source);
    fetch(`${API_URL}/api/auctions?${params}`)
      .then((res) => {
        if (!res.ok) throw new Error('Falha ao carregar leilões');
        return res.json();
      })
      .then((data) => {
        setAuctions(data);
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
        <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer" style={{ color: '#1a1a2e', fontSize: '0.9rem' }}>
          API Docs →
        </a>
      </div>

      {loading && <p>Carregando leilões...</p>}
      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {!loading && !error && auctions.length === 0 && (
        <p style={{ color: '#666' }}>
          Nenhum leilão encontrado. Execute o scraper: <code style={{ background: '#eee', padding: '2px 6px', borderRadius: 4 }}>docker compose --profile scrape run scraper</code>
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
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#666' }}>
                Atualizado: {formatDate(a.updated_at)}
                {a.url && (
                  <>
                    {' · '}
                    <a href={a.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1a1a2e' }}>
                      Ver no site
                    </a>
                  </>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
