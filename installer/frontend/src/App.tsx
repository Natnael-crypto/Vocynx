import { useState, useEffect } from 'react';
import WelcomeScreen from './components/WelcomeScreen';
import LicenseAgreement from './components/LicenseAgreement';
import LocationSelection from './components/LocationSelection';
import InstallProgress from './components/InstallProgress';
import CompletionScreen from './components/CompletionScreen';
import { StartInstallation, LaunchApp, CloseInstaller, GetDefaultPath } from '../wailsjs/go/backend/Installer';
import { EventsOn } from '../wailsjs/runtime/runtime';

// The vocynx icon lives in the frontend public/ folder (copied at build time)
import vocynxIcon from './assets/vocynx_icon.png';

enum Step { Welcome, License, Location, Progress, Completion }

const STEPS = [
  { id: Step.Welcome, label: 'Welcome' },
  { id: Step.License, label: 'License' },
  { id: Step.Location, label: 'Location' },
  { id: Step.Progress, label: 'Installing' },
  { id: Step.Completion, label: 'Finish' },
];

export default function App() {
  const [step, setStep] = useState<Step>(Step.Welcome);
  const [installPath, setInstallPath] = useState('C:\\Program Files\\Vocynx');
  const [progress, setProgress] = useState(0);
  const [progressTitle, setProgressTitle] = useState('Preparing...');
  const [progressStatus, setProgressStatus] = useState('Initializing...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    GetDefaultPath().then(setInstallPath);
    EventsOn('progress_update', (d: any) => { setProgress(d.progress); setProgressTitle(d.title); setProgressStatus(d.status); });
    EventsOn('installation_finished', () => setStep(Step.Completion));
    EventsOn('installation_error', (msg: string) => setError(msg));
  }, []);

  const next = () => setStep(p => p + 1);
  const back = () => setStep(p => p - 1);
  const startInstall = (path: string, autoStart: boolean) => {
    setInstallPath(path);
    setStep(Step.Progress);
    StartInstallation({ path, autoStart });
  };

  return (
    <div style={{
      display: 'flex',
      width: 780,
      height: 520,
      borderRadius: 10,
      overflow: 'hidden',
      border: '1px solid #e0e0e0',
      boxShadow: '0 8px 40px rgba(0,0,0,0.12)',
      background: '#ffffff',
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>

      {/* ── Sidebar ── */}
      <div style={{
        width: 200,
        flexShrink: 0,
        background: '#111111',
        display: 'flex',
        flexDirection: 'column',
        padding: '28px 0',
      }}>
        {/* Logo */}
        <div style={{ padding: '0 24px', marginBottom: 32, display: 'flex', alignItems: 'center', gap: 10 }}>
          <img src={vocynxIcon} alt="Vocynx" style={{ width: 32, height: 32, borderRadius: 6, objectFit: 'contain' }} />
          <div>
            <div style={{ color: '#ffffff', fontWeight: 700, fontSize: 15, letterSpacing: '-0.02em' }}>Vocynx</div>
            <div style={{ color: '#555555', fontSize: 10, fontWeight: 500, marginTop: 1 }}>Setup Wizard</div>
          </div>
        </div>

        {/* Steps */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2, padding: '0 12px' }}>
          {STEPS.map((s, i) => {
            const done = step > s.id;
            const active = step === s.id;
            return (
              <div key={s.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '8px 12px',
                borderRadius: 6,
                background: active ? 'rgba(255,255,255,0.08)' : 'transparent',
                transition: 'background 0.15s',
              }}>
                {/* Step number / check */}
                <div style={{
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  flexShrink: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 10,
                  fontWeight: 700,
                  background: done ? '#ffffff' : active ? '#ffffff' : 'transparent',
                  color: done || active ? '#111111' : 'transparent',
                  border: done || active ? 'none' : '1px solid #333333',
                  transition: 'all 0.2s',
                }}>
                  {done ? (
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : (
                    <span style={{ color: active ? '#111111' : '#444444', fontSize: 10, fontWeight: 700 }}>{i + 1}</span>
                  )}
                </div>
                <span style={{
                  fontSize: 12,
                  fontWeight: active ? 600 : 400,
                  color: active ? '#ffffff' : done ? '#888888' : '#444444',
                  transition: 'color 0.15s',
                }}>
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Version */}
        <div style={{ padding: '0 24px', fontSize: 10, color: '#333333' }}>v1.0.0 · Windows x64</div>
      </div>

      {/* ── Content area ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', background: '#ffffff' }}>

        {/* Error overlay */}
        {error && (
          <div style={{
            position: 'absolute', inset: 0, zIndex: 50,
            background: 'rgba(255,255,255,0.97)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: 40, textAlign: 'center',
          }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
            <h2 style={{ fontSize: 17, fontWeight: 700, color: '#111111', marginBottom: 8 }}>Installation Failed</h2>
            <p style={{ color: '#666666', fontSize: 13, maxWidth: 300, marginBottom: 24, lineHeight: 1.6 }}>{error}</p>
            <button className="btn-primary" onClick={() => window.location.reload()}>Restart</button>
          </div>
        )}

        {/* Page */}
        <div className="page-enter" key={step} style={{ flex: 1, overflow: 'hidden' }}>
          {step === Step.Welcome && <WelcomeScreen onNext={next} />}
          {step === Step.License && <LicenseAgreement onNext={next} onBack={back} />}
          {step === Step.Location && <LocationSelection onNext={startInstall} onBack={back} defaultPath={installPath} />}
          {step === Step.Progress && <InstallProgress progress={progress} title={progressTitle} status={progressStatus} />}
          {step === Step.Completion && <CompletionScreen installPath={installPath} onLaunch={() => LaunchApp()} onClose={() => CloseInstaller()} />}
        </div>

        {/* Footer */}
        <div style={{
          height: 34,
          borderTop: '1px solid #f0f0f0',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 28px',
          background: '#fafafa',
        }}>
          <span style={{ fontSize: 11, color: '#bbbbbb' }}>© 2026 Vocynx</span>
          <span style={{ fontSize: 11, color: '#cccccc' }}>Step {Math.min(step + 1, STEPS.length)} / {STEPS.length}</span>
        </div>
      </div>
    </div>
  );
}
