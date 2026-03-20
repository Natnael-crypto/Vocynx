import React from 'react';

interface Props { installPath: string; onLaunch: () => void; onClose: () => void; }

const CompletionScreen: React.FC<Props> = ({ installPath, onLaunch, onClose }) => (
  <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '36px 36px 24px' }}>

    {/* Header */}
    <div style={{ marginBottom: 28 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#999999', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
        Step 5 — Complete
      </div>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111111', letterSpacing: '-0.03em', margin: 0 }}>
        Installation complete
      </h1>
      <p style={{ color: '#888888', fontSize: 13, marginTop: 6, lineHeight: 1.6 }}>
        Vocynx has been installed and is ready to use.
      </p>
    </div>

    {/* Summary */}
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>

      {/* Install path */}
      <div style={{ padding: '12px 0', borderBottom: '1px solid #f2f2f2' }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#aaaaaa', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>
          Installed to
        </div>
        <div style={{ fontSize: 12, fontFamily: "'Consolas','Courier New',monospace", color: '#333333' }}>
          {installPath}
        </div>
      </div>

      {/* What was done */}
      {[
        'Application files installed',
        'Desktop shortcut created',
        'Start Menu entry added',
        'Registered in Add / Remove Programs',
      ].map(line => (
        <div key={line} style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '10px 0',
          borderBottom: '1px solid #f2f2f2',
        }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#111111" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span style={{ fontSize: 13, color: '#333333' }}>{line}</span>
        </div>
      ))}
    </div>

    {/* Actions */}
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 24 }}>
      <button className="btn-ghost" onClick={onClose}>Close</button>
      <button className="btn-primary" onClick={onLaunch}>Launch Vocynx →</button>
    </div>
  </div>
);

export default CompletionScreen;
