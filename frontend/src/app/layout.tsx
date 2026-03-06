export const metadata = {
  title: 'Leilões Dashboard',
  description: 'Agregador de leilões — Calil, Vegas e mais',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body style={{ margin: 0, fontFamily: 'system-ui, sans-serif', backgroundColor: '#f5f5f5' }}>
        <header style={{ background: '#1a1a2e', color: '#eee', padding: '1rem 2rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Leilões MVP</h1>
          <p style={{ margin: '0.25rem 0 0', opacity: 0.8, fontSize: '0.9rem' }}>Dashboard agregado — Calil, Vegas</p>
        </header>
        <main style={{ padding: '1.5rem 2rem', maxWidth: 1200, margin: '0 auto' }}>
          {children}
        </main>
      </body>
    </html>
  );
}
