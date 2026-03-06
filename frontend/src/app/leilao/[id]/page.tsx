'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Lot = {
  id: number;
  external_id: string;
  title: string;
  description: string | null;
  category: string | null;
  minimum_bid: number | null;
  current_bid: number | null;
  reference_value: number | null;
  url: string | null;
  updated_at: string;
};

type AuctionDetail = {
  id: number;
  external_id: string;
  source: string;
  title: string;
  url: string | null;
  description: string | null;
  starts_at: string | null;
  ends_at: string | null;
  lots_count: number;
  updated_at: string;
  lots: Lot[];
};

function formatMoney(value: number | null): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(value);
}

export default function LeilaoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const [data, setData] = useState<AuctionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetch(`${API_URL}/api/auctions/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error('Leilão não encontrado');
        return res.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p>Carregando...</p>;
  if (error) return <p style={{ color: 'crimson' }}>{error}</p>;
  if (!data) return null;

  return (
    <div>
      <p style={{ marginBottom: '1rem' }}>
        <button
          type="button"
          onClick={() => router.back()}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#1a1a2e', textDecoration: 'underline' }}
        >
          ← Voltar
        </button>
      </p>
      <header style={{ marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid #eee' }}>
        <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#666' }}>{data.source}</span>
        <h1 style={{ margin: '0.25rem 0', fontSize: '1.5rem' }}>{data.title}</h1>
        {data.description && <p style={{ margin: '0.5rem 0', color: '#555', fontSize: '0.9rem' }}>{data.description}</p>}
        <p style={{ margin: 0, fontSize: '0.85rem', color: '#666' }}>
          {data.lots_count} lote(s) · Atualizado: {new Date(data.updated_at).toLocaleString('pt-BR')}
        </p>
        {data.url && (
          <a href={data.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.9rem', color: '#1a1a2e' }}>
            Ver no site original →
          </a>
        )}
      </header>
      <h2 style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>Lotes</h2>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '1rem' }}>
        {data.lots.map((lot) => (
          <li
            key={lot.id}
            style={{
              background: '#fff',
              borderRadius: 8,
              padding: '1rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              border: '1px solid #eee',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
              <strong>{lot.title}</strong>
              <span style={{ fontSize: '0.85rem', color: '#666' }}>#{lot.external_id}</span>
            </div>
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#444', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {lot.current_bid != null && <span>Lance atual: {formatMoney(lot.current_bid)}</span>}
              {lot.minimum_bid != null && lot.minimum_bid !== lot.current_bid && (
                <span>Lance mín.: {formatMoney(lot.minimum_bid)}</span>
              )}
              {lot.reference_value != null && <span>Avaliação: {formatMoney(lot.reference_value)}</span>}
            </div>
            {lot.url && (
              <a href={lot.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', marginTop: '0.5rem', display: 'inline-block' }}>
                Ver detalhes no site →
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
