import React, { useState } from 'react';

interface Props {
  onNext: (path: string, autoStart: boolean) => void;
  onBack: () => void;
  defaultPath: string;
}

const LocationSelection: React.FC<Props> = ({ onNext, onBack, defaultPath }) => {
  const [path, setPath]           = useState(defaultPath);
  const [autoStart, setAutoStart] = useState(true);
  const [shortcut, setShortcut]   = useState(true);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '36px 36px 24px' }}>

      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#999999', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Step 3 — Location
        </div>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: '#111111', letterSpacing: '-0.02em', margin: 0 }}>
          Install Location
        </h1>
        <p style={{ color: '#888888', fontSize: 12, marginTop: 5 }}>
          Choose where Vocynx will be installed on your computer.
        </p>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 20 }}>

        {/* Path field */}
        <div>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#333333', marginBottom: 6 }}>
            Destination folder
          </label>
          <input
            type="text"
            value={path}
            onChange={e => setPath(e.target.value)}
            style={{
              width: '100%',
              border: '1px solid #e0e0e0',
              borderRadius: 6,
              padding: '9px 12px',
              fontSize: 12,
              fontFamily: "'Consolas', 'Courier New', monospace",
              color: '#333333',
              background: '#ffffff',
              outline: 'none',
              transition: 'border-color 0.15s',
            }}
            onFocus={e => (e.currentTarget.style.borderColor = '#111111')}
            onBlur={e  => (e.currentTarget.style.borderColor = '#e0e0e0')}
          />
          <div style={{ fontSize: 11, color: '#aaaaaa', marginTop: 5 }}>Required disk space: ~150 MB</div>
        </div>

        {/* Options */}
        <div style={{
          border: '1px solid #eeeeee',
          borderRadius: 8,
          padding: '16px 18px',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#999999', letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: 2 }}>
            Options
          </div>
          {([
            { id: 'autostart', label: 'Launch Vocynx automatically on Windows startup', checked: autoStart, set: setAutoStart },
            { id: 'shortcut',  label: 'Create a Desktop shortcut',                     checked: shortcut,   set: setShortcut  },
          ] as const).map(({ id, label, checked, set }) => (
            <div key={id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <input id={id} type="checkbox" className="check" checked={checked} onChange={e => set(e.target.checked)} />
              <label htmlFor={id} style={{ fontSize: 13, color: '#444444', cursor: 'pointer', userSelect: 'none' }}>{label}</label>
            </div>
          ))}
        </div>
      </div>

      {/* Nav */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
        <button className="btn-ghost" onClick={onBack}>← Back</button>
        <button className="btn-primary" onClick={() => onNext(path, autoStart)}>
          Install →
        </button>
      </div>
    </div>
  );
};

export default LocationSelection;
