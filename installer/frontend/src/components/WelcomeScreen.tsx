import React from 'react';

interface Props { onNext: () => void; }

const WelcomeScreen: React.FC<Props> = ({ onNext }) => (
  <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '36px 36px 24px' }}>

    <div style={{ marginBottom: 28 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#999999', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
        Getting started
      </div>
      <h1 style={{ fontSize: 24, fontWeight: 700, color: '#111111', letterSpacing: '-0.03em', margin: 0, lineHeight: 1.15 }}>
        Welcome to Vocynx
      </h1>
      <p style={{ color: '#888888', fontSize: 13, marginTop: 8, lineHeight: 1.6, maxWidth: 360 }}>
        This wizard will guide you through a quick installation of Vocynx on your Windows PC.
      </p>
    </div>

    {/* Feature rows — text-only, no icon clutter */}
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
      {[
        ['Local AI Transcription',  'Converts speech to text on your device.'],
        ['Private by Design',       'Audio never leaves your machine.'],
        ['Lightweight & Fast',      'Under 150 MB. Launches in seconds.'],
      ].map(([title, desc]) => (
        <div key={title} style={{
          padding: '14px 16px',
          borderBottom: '1px solid #f2f2f2',
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#111111' }}>{title}</div>
          <div style={{ fontSize: 12, color: '#888888', lineHeight: 1.5 }}>{desc}</div>
        </div>
      ))}
    </div>

    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 24 }}>
      <button className="btn-primary" onClick={onNext}>
        Next &rarr;
      </button>
    </div>
  </div>
);

export default WelcomeScreen;
