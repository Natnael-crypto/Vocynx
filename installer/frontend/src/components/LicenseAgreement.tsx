import React, { useState } from 'react';

interface Props { onNext: () => void; onBack: () => void; }

const LICENSE_TEXT = `VOCYNX END USER LICENSE AGREEMENT — Last Updated: March 2026

1. GRANT OF LICENSE
Vocynx grants you a non-exclusive, non-transferable license to install and use the Vocynx software ("Software") solely for your own personal or internal business purposes.

2. RESTRICTIONS
You may not: (a) copy the Software except for backup purposes; (b) modify, adapt, or create derivative works; (c) reverse engineer or attempt to extract source code; (d) sell, sublicense, rent, or transfer the Software to any third party.

3. PRIVACY & DATA
Vocynx processes all audio locally on your device. No audio data is sent to external servers unless you have explicitly opted in to optional cloud features. Only anonymised crash diagnostics are collected, with your consent.

4. INTELLECTUAL PROPERTY
All rights in the Software, including copyrights, remain with Vocynx and its licensors.

5. NO WARRANTY
THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. VOCYNX DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING FITNESS FOR A PARTICULAR PURPOSE.

6. LIMITATION OF LIABILITY
IN NO EVENT SHALL VOCYNX BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING FROM THE USE OF THIS SOFTWARE.

7. TERMINATION
This license terminates automatically if you fail to comply with any of its terms.

By continuing you confirm you have read and accept these terms.`;

const LicenseAgreement: React.FC<Props> = ({ onNext, onBack }) => {
  const [accepted, setAccepted] = useState(false);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '36px 36px 24px' }}>

      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#999999', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
          Step 2 — License
        </div>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: '#111111', letterSpacing: '-0.02em', margin: 0 }}>
          License Agreement
        </h1>
        <p style={{ color: '#888888', fontSize: 12, marginTop: 5 }}>
          Read and accept the terms before continuing.
        </p>
      </div>

      {/* EULA scroll box */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        border: '1px solid #e8e8e8',
        borderRadius: 6,
        padding: '14px 18px',
        background: '#fafafa',
        fontSize: 12,
        lineHeight: 1.75,
        color: '#444444',
        whiteSpace: 'pre-wrap',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}>
        {LICENSE_TEXT}
      </div>

      {/* Accept */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 14 }}>
        <input
          id="accept"
          type="checkbox"
          className="check"
          checked={accepted}
          onChange={e => setAccepted(e.target.checked)}
        />
        <label htmlFor="accept" style={{ fontSize: 13, color: '#444444', cursor: 'pointer', userSelect: 'none' }}>
          I have read and agree to the License Agreement
        </label>
      </div>

      {/* Nav */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 18 }}>
        <button className="btn-ghost" onClick={onBack}>← Back</button>
        <button className="btn-primary" onClick={onNext} disabled={!accepted}>
          Accept &amp; Continue →
        </button>
      </div>
    </div>
  );
};

export default LicenseAgreement;
