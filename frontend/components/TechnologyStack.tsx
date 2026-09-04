"use client";

import { LookupResponse, TechnologyInfo, TechnologyDetection } from "@/types";
import {
  Code2,
  Package,
  Server,
  Cloud,
  Globe,
  BarChart,
  MapPin,
  Building2,
  Network,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  XCircle,
  Wifi,
} from "lucide-react";
import { useState } from "react";

// Infrastructure providers and their display names / types
const INFRA_DISPLAY: Record<string, { label: string; type: string }> = {
  "vercel": { label: "Vercel", type: "Edge / PaaS" },
  "netlify": { label: "Netlify", type: "Jamstack Hosting" },
  "hostinger": { label: "Hostinger", type: "Cloud / Web Hosting" },
  "hcdn": { label: "Hostinger CDN", type: "CDN / Edge" },
  "render": { label: "Render", type: "Cloud PaaS" },
  "railway": { label: "Railway", type: "Cloud PaaS" },
  "fly.io": { label: "Fly.io", type: "Edge App Platform" },
  "wp engine": { label: "WP Engine", type: "Managed WordPress" },
  "pantheon": { label: "Pantheon", type: "WebOps Platform" },
  "cloudflare": { label: "Cloudflare", type: "CDN / Edge" },
  "amazon cloudfront": { label: "Amazon CloudFront", type: "CDN" },
  "aws": { label: "Amazon Web Services", type: "Cloud" },
  "amazon web": { label: "Amazon Web Services", type: "Cloud" },
  "google cloud": { label: "Google Cloud", type: "Cloud" },
  "firebase": { label: "Google Firebase", type: "Cloud" },
  "azure": { label: "Microsoft Azure", type: "Cloud" },
  "digitalocean": { label: "DigitalOcean", type: "Cloud VPS" },
  "linode": { label: "Linode / Akamai", type: "Cloud VPS" },
  "hetzner": { label: "Hetzner", type: "Dedicated / VPS" },
  "fastly": { label: "Fastly", type: "CDN" },
  "akamai": { label: "Akamai", type: "CDN" },
  "heroku": { label: "Heroku", type: "PaaS" },
  "ovh": { label: "OVHcloud", type: "Cloud / VPS" },
  "nginx": { label: "Nginx (Self-Hosted)", type: "Self-Hosted" },
  "apache": { label: "Apache (Self-Hosted)", type: "Self-Hosted" },
  "github pages": { label: "GitHub Pages", type: "Static Hosting" },
};

const NS_DISPLAY: Array<{ keywords: string[]; provider: string; type: string }> = [
  { keywords: ["vercel"], provider: "Vercel", type: "Edge / PaaS" },
  { keywords: ["hostinger"], provider: "Hostinger", type: "Cloud / Web Hosting" },
  { keywords: ["cloudflare"], provider: "Cloudflare", type: "CDN / Edge" },
  { keywords: ["awsdns", "amazonaws"], provider: "Amazon Web Services", type: "Cloud" },
  { keywords: ["cloudfront"], provider: "Amazon CloudFront", type: "CDN" },
  { keywords: ["netlify"], provider: "Netlify", type: "Jamstack Hosting" },
  { keywords: ["digitalocean"], provider: "DigitalOcean", type: "Cloud VPS" },
  { keywords: ["linode", "akamai"], provider: "Linode / Akamai", type: "Cloud VPS" },
  { keywords: ["google", "googlehosted"], provider: "Google Cloud", type: "Cloud" },
  { keywords: ["azure", "microsoft"], provider: "Microsoft Azure", type: "Cloud" },
  { keywords: ["godaddy", "secureserver", "domaincontrol"], provider: "GoDaddy", type: "DNS Registrar" },
  { keywords: ["namecheap"], provider: "Namecheap", type: "DNS Registrar" },
  { keywords: ["siteground"], provider: "SiteGround", type: "Web Hosting" },
  { keywords: ["hetzner"], provider: "Hetzner", type: "Dedicated / VPS" },
  { keywords: ["ovh"], provider: "OVHcloud", type: "Cloud / VPS" },
];

function detectHostingBanner(data: LookupResponse): {
  provider: string; type: string; ip: string; location: string; network: string;
  dnsProvider?: string;
} | null {

  const firstIp = data.network?.resolved_ips?.[0];
  const netDetails = firstIp ? data.network?.details?.[firstIp] : undefined;
  const infraTechs = data.technology?.infrastructure ?? [];

  // ── PRIORITY 1: Specific Cloud Host from HTTP headers (e.g. Vercel, Netlify, Cloudflare, AWS) ──
  const specificTech = infraTechs.find(t =>
    !["nginx", "apache", "iis", "cpanel"].includes(t.name.toLowerCase())
  );

  if (specificTech) {
    const key = Object.keys(INFRA_DISPLAY).find(k =>
      specificTech.name.toLowerCase().includes(k)
    );
    const display = key ? INFRA_DISPLAY[key] : null;
    return {
      provider: display?.label ?? specificTech.name,
      type: display?.type ?? "Cloud Host",
      ip: firstIp ?? "—",
      location: netDetails?.country ?? "—",
      network: netDetails?.cidr ?? netDetails?.name ?? "—",
    };
  }

  // ── PRIORITY 2: CNAME records (e.g. *.vercel.app, *.vercel-dns-016.com, *.netlify.app) ─────────
  if (data.dns?.cname) {
    for (const cname of data.dns.cname) {
      const val = (cname.value || "").toLowerCase();
      const match = NS_DISPLAY.find(h => h.keywords.some(k => val.includes(k)));
      if (match && !["godaddy", "namecheap"].includes(match.provider.toLowerCase())) {
        return {
          provider: match.provider, type: match.type,
          ip: firstIp ?? "—",
          location: netDetails?.country ?? "—",
          network: netDetails?.cidr ?? netDetails?.name ?? "—",
        };
      }
    }
  }

  // ── PRIORITY 3: IP / ASN organisation ────────────────────────────────────
  if (netDetails) {
    const orgRaw = netDetails.organization || netDetails.name || "";
    const orgLower = orgRaw.toLowerCase();
    const match = NS_DISPLAY.find(h => h.keywords.some(k => orgLower.includes(k)));
    if (match && !["godaddy", "namecheap"].includes(match.provider.toLowerCase())) {
      return {
        provider: match.provider, type: match.type,
        ip: firstIp ?? "—",
        location: netDetails?.country ?? "—",
        network: netDetails?.cidr ?? netDetails?.name ?? "—",
      };
    }
  }

  // ── PRIORITY 4: Generic Web Server from headers (e.g. Apache, Nginx) ─────
  const genericTech = infraTechs.find(t =>
    ["nginx", "apache", "iis", "cpanel"].includes(t.name.toLowerCase())
  );
  if (genericTech) {
    const key = Object.keys(INFRA_DISPLAY).find(k =>
      genericTech.name.toLowerCase().includes(k)
    );
    const display = key ? INFRA_DISPLAY[key] : null;
    return {
      provider: display?.label ?? genericTech.name,
      type: display?.type ?? "Self-Hosted",
      ip: firstIp ?? "—",
      location: netDetails?.country ?? "—",
      network: netDetails?.cidr ?? netDetails?.name ?? "—",
    };
  }

  // Fallback: Org string if available
  if (netDetails?.organization || netDetails?.name) {
    const orgRaw = netDetails.organization || netDetails.name || "";
    return {
      provider: orgRaw.split(" - ")[0].trim().split(",")[0].trim(),
      type: "Network Provider",
      ip: firstIp ?? "—",
      location: netDetails?.country ?? "—",
      network: netDetails?.cidr ?? netDetails?.name ?? "—",
    };
  }

  if (!firstIp) return null;
  return { provider: "Unknown", type: "—", ip: firstIp, location: "—", network: "—" };
}

// ---------------------------------------------------------------------------
// Main exported component
// ---------------------------------------------------------------------------
interface TechnologyStackProps {
  data: TechnologyInfo;
  lookupData?: LookupResponse;
}

export function TechnologyStack({ data, lookupData }: TechnologyStackProps) {
  const hosting = lookupData ? detectHostingBanner(lookupData) : null;

  const sections = [
    { id: "frontend", title: "Frontend", icon: <Code2 size={18} />, items: data.frontend },
    { id: "packages", title: "JavaScript Packages", icon: <Package size={18} />, items: data.packages },
    { id: "backend", title: "Backend", icon: <Server size={18} />, items: data.backend },
    { id: "infrastructure", title: "Infrastructure", icon: <Cloud size={18} />, items: data.infrastructure },
    { id: "cdn", title: "CDN", icon: <Wifi size={18} />, items: data.cdn },
    { id: "analytics", title: "Analytics & Tracking", icon: <BarChart size={18} />, items: data.analytics },
  ];

  const hasAnyTech = sections.some(s => s.items && s.items.length > 0);

  return (
    <div className="space-y-6">
      {/* ---- WHERE HOSTED BANNER ---- */}
      {hosting && (
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center bg-neutral-50/50 dark:bg-neutral-900/50">
            <Building2 size={18} className="text-blue-500 mr-2" />
            <h3 className="text-lg font-medium text-neutral-900 dark:text-white">Where Hosted</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-y sm:divide-y-0 divide-neutral-100 dark:divide-neutral-800">
            <HostingCell icon={<Globe size={14} />} label="Provider" value={hosting.provider} accent />
            <HostingCell icon={<Server size={14} />} label="Type" value={hosting.type} />
            <HostingCell icon={<MapPin size={14} />} label="Primary IP" value={hosting.ip} mono />
            <HostingCell icon={<Network size={14} />} label="Location / Network" value={`${hosting.location}  ${hosting.network}`} />
          </div>
        </div>
      )}

      {/* ---- TECHNOLOGY SECTIONS ---- */}
      {!hasAnyTech ? (
        <div className="p-8 text-center text-neutral-500 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm">
          <AlertCircle className="mx-auto mb-4 text-neutral-400" size={32} />
          <p>No technologies were detected for this domain.</p>
          <p className="text-xs mt-2 text-neutral-400">The site may block scrapers, use heavy obfuscation, or serve very little public JS.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sections.map(section => {
            if (!section.items || section.items.length === 0) return null;
            return (
              <div key={section.id} className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
                <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center bg-neutral-50/50 dark:bg-neutral-900/50">
                  <span className="text-blue-500 mr-2">{section.icon}</span>
                  <h3 className="text-base font-semibold text-neutral-900 dark:text-white">{section.title}</h3>
                  <span className="ml-auto text-xs text-neutral-400">{section.items.length} detected</span>
                </div>
                <div className="p-4 space-y-3 flex-grow">
                  {section.items.map((tech, idx) => (
                    <TechnologyItem key={idx} tech={tech} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Small hosting info cell
// ---------------------------------------------------------------------------
function HostingCell({ icon, label, value, accent = false, mono = false }: {
  icon: React.ReactNode; label: string; value: string; accent?: boolean; mono?: boolean;
}) {
  return (
    <div className="px-5 py-4">
      <div className="flex items-center gap-1.5 text-neutral-400 text-xs mb-1">{icon} {label}</div>
      <p className={`text-sm font-semibold truncate ${accent ? "text-blue-600 dark:text-blue-400" : "text-neutral-900 dark:text-neutral-100"} ${mono ? "font-mono" : ""}`}>
        {value || "—"}
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Individual technology detection row
// ---------------------------------------------------------------------------
function TechnologyItem({ tech }: { tech: TechnologyDetection }) {
  const [expanded, setExpanded] = useState(false);

  const statusConfig: Record<string, { color: string; icon: React.ReactNode }> = {
    "confirmed": {
      color: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800",
      icon: <CheckCircle2 size={10} className="mr-0.5" />,
    },
    "high confidence": {
      color: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
      icon: <CheckCircle2 size={10} className="mr-0.5" />,
    },
    "possible": {
      color: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800",
      icon: <HelpCircle size={10} className="mr-0.5" />,
    },
  };

  const cfg = statusConfig[tech.status.toLowerCase()] ?? {
    color: "text-neutral-500 bg-neutral-100 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700",
    icon: <XCircle size={10} className="mr-0.5" />,
  };

  const pct = Math.round(tech.confidence * 100);

  return (
    <div className="border border-neutral-100 dark:border-neutral-800 rounded-lg overflow-hidden">
      <div
        className="px-4 py-2.5 flex items-center justify-between cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800/40 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="font-medium text-sm text-neutral-900 dark:text-neutral-100 truncate">{tech.name}</span>
          <span className={`inline-flex items-center text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border whitespace-nowrap ${cfg.color}`}>
            {cfg.icon}{tech.status}
          </span>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-2">
          {/* Confidence bar */}
          <div className="hidden sm:flex items-center gap-2">
            <div className="w-20 h-1.5 bg-neutral-100 dark:bg-neutral-800 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${pct >= 85 ? "bg-emerald-500" : pct >= 65 ? "bg-blue-500" : "bg-amber-500"}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-xs font-mono text-neutral-500 w-8 text-right">{pct}%</span>
          </div>
          {expanded ? <ChevronUp size={14} className="text-neutral-400" /> : <ChevronDown size={14} className="text-neutral-400" />}
        </div>
      </div>

      {expanded && tech.evidence.length > 0 && (
        <div className="px-4 py-3 bg-neutral-50 dark:bg-neutral-800/30 border-t border-neutral-100 dark:border-neutral-800">
          <p className="text-[10px] uppercase font-semibold text-neutral-400 mb-2 tracking-wider">Why was this detected?</p>
          <ul className="space-y-1">
            {tech.evidence.map((ev, i) => (
              <li key={i} className="flex items-start gap-2 text-xs font-mono text-neutral-600 dark:text-neutral-400">
                <span className="text-emerald-500 mt-0.5">✓</span>
                <span className="break-all">{ev}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
