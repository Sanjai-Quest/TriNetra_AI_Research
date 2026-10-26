import React from 'react';
import { ClaimDetail } from '../services/api';
import { Activity, AlertTriangle, Camera, Mic, Package, Scale } from 'lucide-react';

interface ClaimDetailViewProps {
  claim: ClaimDetail | null;
  onOpenOverride: () => void;
}

export const ClaimDetailView: React.FC<ClaimDetailViewProps> = ({ claim, onOpenOverride }) => {
  if (!claim) {
    return (
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500 h-full flex flex-col items-center justify-center space-y-3">
        <Package className="w-12 h-12 text-slate-600 animate-bounce" />
        <h3 className="text-sm font-semibold text-slate-400">Select a Claim to Inspect</h3>
        <p className="text-xs text-slate-500 max-w-xs">
          Inspect multi-modal artifacts, detected fraud patterns, and submit investigator override decisions.
        </p>
      </div>
    );
  }

  const getSeverityStyle = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500/10 border-rose-500/30 text-rose-300';
      case 'high':
        return 'bg-orange-500/10 border-orange-500/30 text-orange-300';
      case 'medium':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-300';
      default:
        return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300';
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col h-full overflow-y-auto space-y-6">
      <header className="border-b border-slate-800 pb-4 flex items-start justify-between">
        <div>
          <span className="text-[11px] font-mono text-indigo-400 font-bold uppercase">Claim Detail</span>
          <h2 className="text-lg font-bold text-white font-mono">{claim.orderId}</h2>
          <p className="text-xs text-slate-400">Case {claim.caseId || claim.claimId} · {claim.product || 'Smartphone'}</p>
          {claim.sourceCaseId && <p className="text-[11px] text-cyan-300">xscrapper: {claim.sourceCaseId} · {claim.sourcePlatform} · {claim.sourceComplaintType}</p>}
        </div>
        <button onClick={onOpenOverride} className="text-xs px-3 py-2 rounded-lg bg-amber-500/15 text-amber-300 border border-amber-500/30">
          Investigator decision
        </button>
      </header>

      <section className="grid grid-cols-2 gap-3">
        <Metric label="Expected serial" value={claim.expectedSerial || 'Not captured'} />
        <Metric label="Observed serial" value={claim.observedSerial || 'Not captured'} />
        <Metric label="Expected IMEI" value={claim.expectedImei || 'N/A'} />
        <Metric label="Observed IMEI" value={claim.observedImei || 'N/A'} />
      </section>

      <section className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
        <div className="flex items-center gap-2 text-amber-300 font-bold"><AlertTriangle className="w-4 h-4" /> {claim.state || 'INVESTIGATE'}</div>
        <p className="mt-2 text-sm text-slate-300">{claim.reasoning || 'Persisted V3 investigation data loaded.'}</p>
      </section>

      {claim.sourceCaseId && (
        <section className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-300">Real complaint source</h3>
          <p className="mt-2 text-xs text-slate-300">Dataset record {claim.sourceCaseId} from {claim.sourcePlatform}; classified as {claim.sourceComplaintType}.</p>
        </section>
      )}

      {claim.investigations?.map(investigation => (
        <section key={investigation.investigationId} className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-rose-300">Investigation {investigation.status}</h3>
          <p className="mt-2 text-xs text-slate-300">Reason: {investigation.reason}</p>
          <p className="mt-1 text-xs text-slate-400">Last matching checkpoint: {investigation.lastMatchingCheckpointId || 'None'}</p>
          <p className="mt-1 text-xs text-slate-400">First known divergence: {investigation.firstDivergenceCheckpointId || 'None'}</p>
        </section>
      ))}

      <section className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Checkpoints</h3>
        {claim.checkpoints?.map(checkpoint => (
          <div key={checkpoint.checkpointId} className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-xs">
            <div className="flex justify-between text-white"><span>Checkpoint {checkpoint.sequenceNumber}</span><strong>{checkpoint.decision}</strong></div>
            <div className="mt-1 text-slate-400">Serial: {checkpoint.observedSerial} · IMEI: {checkpoint.observedImei || 'N/A'}</div>
            <div className="mt-1 text-slate-500">{checkpoint.location || 'Location unavailable'}{checkpoint.checkpointType ? ` · ${checkpoint.checkpointType}` : ''}</div>
          </div>
        ))}
      </section>

      <section className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Custody and audit</h3>
        <div className="text-xs text-slate-300">{claim.custody?.length || 0} custody events · {claim.audit?.length || 0} audit events</div>
        {claim.custody?.map(event => <div key={event.custodyEventId} className="text-xs text-slate-400">{event.fromActor || 'Origin'} → {event.toActor} · {event.action}</div>)}
      </section>

      <section className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Evidence sources</h3>
        {claim.evidence?.map(item => (
          <div key={item.evidenceId} className="rounded-xl border border-slate-800 bg-slate-950/70 p-3">
            <div className="flex items-center gap-2 text-sm text-white"><SourceIcon source={item.source} /> {item.source}</div>
            <pre className="mt-2 text-[11px] text-slate-400 whitespace-pre-wrap">{item.payloadJson}</pre>
            <div className="mt-2 text-[10px] text-slate-500">{new Date(item.createdAt).toLocaleString()}</div>
          </div>
        ))}
        <div className="text-xs text-slate-400">{claim.evidence?.length || 0} persisted evidence records linked to this verification.</div>
      </section>
    </div>
  );
};

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div className="rounded-xl bg-slate-950/70 border border-slate-800 p-3">
    <span className="block text-[10px] uppercase font-bold text-slate-500">{label}</span>
    <span className="block mt-1 text-lg font-bold text-white">{value}</span>
  </div>
);

const SourceIcon = ({ source }: { source: string }) => {
  if (source.includes('SCALE')) return <Scale className="w-4 h-4 text-cyan-300" />;
  if (source.includes('VOICE')) return <Mic className="w-4 h-4 text-violet-300" />;
  if (source.includes('CAMERA') || source.includes('CV')) return <Camera className="w-4 h-4 text-emerald-300" />;
  return <Activity className="w-4 h-4 text-slate-300" />;
};
