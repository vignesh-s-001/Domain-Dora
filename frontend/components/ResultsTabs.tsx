"use client";

import { LookupResponse } from "@/types";
import { format, differenceInDays } from "date-fns";
import { AlertCircle, CheckCircle2, Shield, ShieldAlert, Server, Globe, Network, Lock } from "lucide-react";
import { useState } from "react";

export function ResultsTabs({ data }: { data: LookupResponse }) {
  const [activeTab, setActiveTab] = useState("overview");

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "dns", label: "DNS" },
    { id: "ssl", label: "SSL" },
    { id: "network", label: "Network" },
    { id: "raw", label: "Raw Data" },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto mt-8">
      <div className="border-b border-neutral-200 dark:border-neutral-800 mb-6 overflow-x-auto">
        <nav className="flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${activeTab === tab.id
                  ? "border-blue-500 text-blue-600 dark:text-blue-500"
                  : "border-transparent text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200 hover:border-neutral-300 dark:hover:border-neutral-700"
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-6">
        {activeTab === "overview" && <OverviewTab data={data} />}
        {activeTab === "dns" && <DNSTab data={data} />}
        {activeTab === "ssl" && <SSLTab data={data} />}
        {activeTab === "network" && <NetworkTab data={data} />}
        {activeTab === "raw" && <RawDataTab data={data} />}
      </div>
    </div>
  );
}

function OverviewTab({ data }: { data: LookupResponse }) {
  if (!data.domain) {
    return <ErrorPlaceholder service="Domain RDAP" errors={data.errors} />;
  }

  const d = data.domain;
  
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Unknown";
    return format(new Date(dateStr), "MMM d, yyyy");
  };

  const getAge = (dateStr: string | null) => {
    if (!dateStr) return null;
    return differenceInDays(new Date(), new Date(dateStr));
  };

  const age = getAge(d.created_at);

  // Robust Hosting Provider Detection
  const detectHostingProvider = () => {
    if (data.dns?.cname) {
      for (const cname of data.dns.cname) {
        const val = cname.value.toLowerCase();
        if (val.includes("vercel")) return { name: "Vercel", type: "PaaS / Hosting" };
        if (val.includes("netlify")) return { name: "Netlify", type: "PaaS / Hosting" };
        if (val.includes("github.io")) return { name: "GitHub Pages", type: "Static Hosting" };
        if (val.includes("herokuapp.com")) return { name: "Heroku", type: "PaaS" };
        if (val.includes("wpengine")) return { name: "WP Engine", type: "WordPress Hosting" };
        if (val.includes("myshopify")) return { name: "Shopify", type: "eCommerce Hosting" };
        if (val.includes("cloudfront.net")) return { name: "Amazon CloudFront", type: "CDN" };
        if (val.includes("azureedge.net") || val.includes("trafficmanager.net")) return { name: "Microsoft Azure", type: "Cloud Provider" };
        if (val.includes("fastly")) return { name: "Fastly", type: "CDN" };
        if (val.includes("ghs.googlehosted.com") || val.includes("google.com")) return { name: "Google", type: "Hosting" };
      }
    }

    if (d.nameservers) {
      for (const ns of d.nameservers) {
        const val = ns.toLowerCase();
        if (val.includes("cloudflare.com")) return { name: "Cloudflare", type: "CDN / Web Security" };
        if (val.includes("awsdns")) return { name: "Amazon Web Services (AWS)", type: "Cloud Provider" };
        if (val.includes("digitalocean.com")) return { name: "DigitalOcean", type: "Cloud Provider" };
        if (val.includes("domaincontrol.com")) return { name: "GoDaddy", type: "Hosting / DNS" };
        if (val.includes("namecheap.com")) return { name: "Namecheap", type: "Hosting / DNS" };
        if (val.includes("hostgator.com")) return { name: "HostGator", type: "Web Hosting" };
        if (val.includes("bluehost.com")) return { name: "Bluehost", type: "Web Hosting" };
        if (val.includes("linode.com")) return { name: "Linode / Akamai", type: "Cloud Provider" };
        if (val.includes("vercel-dns.com")) return { name: "Vercel", type: "PaaS / Hosting" };
        if (val.includes("googledomains.com") || val.includes("google.com")) return { name: "Google", type: "Infrastructure / DNS" };
      }
    }

    if (data.network && data.network.resolved_ips.length > 0) {
      const firstIp = data.network.resolved_ips[0];
      const netDetails = data.network.details?.[firstIp];
      const org = (netDetails?.organization || netDetails?.name || "").toLowerCase();
      
      if (org) {
        if (org.includes("amazon") || org.includes("aws")) return { name: "Amazon Web Services (AWS)", type: "Cloud Infrastructure" };
        if (org.includes("google")) return { name: "Google Cloud Platform", type: "Cloud Infrastructure" };
        if (org.includes("microsoft") || org.includes("azure")) return { name: "Microsoft Azure", type: "Cloud Infrastructure" };
        if (org.includes("digitalocean")) return { name: "DigitalOcean", type: "Cloud Provider" };
        if (org.includes("cloudflare")) return { name: "Cloudflare", type: "CDN / Infrastructure" };
        if (org.includes("fastly")) return { name: "Fastly", type: "CDN" };
        if (org.includes("akamai")) return { name: "Akamai", type: "CDN" };
        if (org.includes("godaddy")) return { name: "GoDaddy", type: "Web Hosting" };
        if (org.includes("hetzner")) return { name: "Hetzner", type: "Dedicated/Cloud Hosting" };
        if (org.includes("ovh")) return { name: "OVHcloud", type: "Cloud Provider" };
        if (org.includes("choopa") || org.includes("vultr")) return { name: "Vultr / Choopa", type: "Cloud Provider" };
        if (org.includes("ntt ")) return { name: "NTT Communications", type: "Enterprise Infrastructure" };
        
        return { name: netDetails?.organization || netDetails?.name || "Unknown", type: "Network Provider" };
      }
    }

    return { name: "Unknown", type: "Unknown" };
  };

  const hosting = detectHostingProvider();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 md:col-span-2 shadow-sm">
        <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center">
          <Server className="mr-2 text-blue-500" size={18} /> Hosting Information
        </h3>
        <div className="flex flex-col sm:flex-row sm:justify-between py-4 border-b border-neutral-100 dark:border-neutral-800/50">
          <span className="text-neutral-500 text-sm">Detected Provider</span>
          <div className="flex flex-col sm:items-end">
            <span className="text-neutral-900 dark:text-white font-semibold text-lg text-right break-all">{hosting.name}</span>
            <span className="text-blue-600 dark:text-blue-400 text-xs mt-1 bg-blue-100 dark:bg-blue-900/30 px-2 py-0.5 rounded border border-blue-200 dark:border-blue-800/30">
              {hosting.type}
            </span>
          </div>
        </div>
        {data.network && data.network.resolved_ips.length > 0 && (
          <>
            <DetailRow 
              label="Primary Server IP" 
              value={data.network.resolved_ips[0]} 
            />
            <DetailRow 
              label="Hosting Location" 
              value={
                data.network.details?.[data.network.resolved_ips[0]]?.country 
                  ? `${data.network.details[data.network.resolved_ips[0]].country}` 
                  : "Not Provided by Registry"
              } 
            />
            <DetailRow 
              label="Raw Network ID" 
              value={
                data.network.details?.[data.network.resolved_ips[0]]?.name || "Unknown"
              } 
            />
          </>
        )}
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm self-start">
        <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center">
          <Globe className="mr-2" size={18} /> Registration Details
        </h3>
        <div className="space-y-4">
          <DetailRow label="Domain" value={d.name} />
          <DetailRow label="Registrar" value={d.registrar?.name || "Unknown"} />
          {d.registrar?.contact_email && <DetailRow label="Registrar Email" value={d.registrar.contact_email} />}
          {d.registrar?.contact_phone && <DetailRow label="Registrar Phone" value={d.registrar.contact_phone} />}
          <DetailRow label="Created" value={formatDate(d.created_at)} subValue={age ? `${Math.floor(age/365)} years old` : undefined} />
          <DetailRow label="Expires" value={formatDate(d.expires_at)} />
        </div>
      </div>
      <div className="space-y-6">
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center"><Server className="mr-2" size={18} /> Nameservers</h3>
          {d.nameservers.length > 0 ? (
            <ul className="space-y-2">
              {d.nameservers.map((ns, i) => <li key={i} className="text-sm font-mono bg-neutral-100 dark:bg-black p-2 rounded text-neutral-700 dark:text-neutral-300">{ns}</li>)}
            </ul>
          ) : <p className="text-sm text-neutral-500">No nameservers found.</p>}
        </div>
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center">
            {d.dnssec === "signedDelegation" ? <Shield className="mr-2 text-green-500" size={18} /> : <ShieldAlert className="mr-2 text-yellow-500" size={18} />} DNSSEC
          </h3>
          <p className="text-sm text-neutral-700 dark:text-neutral-300 capitalize">{d.dnssec || "Unknown"}</p>
        </div>
      </div>
    </div>
  );
}

function DNSTab({ data }: { data: LookupResponse }) {
  if (!data.dns) return <ErrorPlaceholder service="DNS" errors={data.errors} />;
  
  const d = data.dns;
  const sections = [
    { title: "A Records", data: d.a },
    { title: "AAAA Records", data: d.aaaa },
    { title: "MX Records", data: d.mx },
    { title: "TXT Records", data: d.txt },
    { title: "CNAME Records", data: d.cname },
    { title: "NS Records", data: d.ns },
  ];

  return (
    <div className="space-y-6">
      {sections.map(sec => sec.data && sec.data.length > 0 && (
        <div key={sec.title} className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 overflow-x-auto shadow-sm">
          <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4">{sec.title}</h3>
          <table className="w-full text-left text-sm text-neutral-600 dark:text-neutral-400">
            <thead className="text-xs uppercase bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg">Value</th>
                <th className="px-4 py-3 rounded-tr-lg">TTL</th>
              </tr>
            </thead>
            <tbody>
              {sec.data.map((rec, i) => (
                <tr key={i} className="border-b border-neutral-100 dark:border-neutral-800 last:border-0">
                  <td className="px-4 py-3 font-mono break-all">{rec.value}</td>
                  <td className="px-4 py-3">{rec.ttl || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

function SSLTab({ data }: { data: LookupResponse }) {
  if (!data.ssl) return <ErrorPlaceholder service="SSL" errors={data.errors} />;
  const s = data.ssl;
  
  if (!s.available) {
    return (
      <div className="p-8 text-center text-neutral-500 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm">
        <ShieldAlert className="mx-auto mb-4 text-neutral-400" size={32} />
        <p>SSL Certificate could not be retrieved or is unavailable.</p>
      </div>
    );
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Unknown";
    return format(new Date(dateStr), "MMM d, yyyy");
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center">
          <Lock className="mr-2 text-green-500" size={18} /> Subject Details
        </h3>
        <div className="space-y-4">
          <DetailRow label="Common Name" value={s.subject.commonName || "-"} />
          <DetailRow label="Organization" value={s.subject.organizationName || "-"} />
          <DetailRow label="Country" value={s.subject.countryName || "-"} />
        </div>
      </div>
      
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4 flex items-center">
          <Shield className="mr-2 text-blue-500" size={18} /> Issuer Details
        </h3>
        <div className="space-y-4">
          <DetailRow label="Common Name" value={s.issuer.commonName || "-"} />
          <DetailRow label="Organization" value={s.issuer.organizationName || "-"} />
          <DetailRow label="Country" value={s.issuer.countryName || "-"} />
        </div>
      </div>

      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 md:col-span-2 shadow-sm">
        <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4">Validity & SANs</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <DetailRow label="Valid From" value={formatDate(s.valid_from)} />
            <DetailRow label="Valid To" value={formatDate(s.valid_to)} subValue={s.days_remaining ? `Expires in ${s.days_remaining} days` : undefined} />
            <DetailRow label="Serial Number" value={s.serial_number || "-"} />
          </div>
          <div>
            <span className="text-neutral-500 text-sm block mb-2">Subject Alternative Names</span>
            <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
              {s.san.map((san, i) => (
                <span key={i} className="px-2 py-1 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 rounded text-xs font-mono">{san}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function NetworkTab({ data }: { data: LookupResponse }) {
  if (!data.network) return <ErrorPlaceholder service="Network" errors={data.errors} />;
  const net = data.network;
  
  if (net.resolved_ips.length === 0) {
    return (
      <div className="p-8 text-center text-neutral-500 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm">
        <Network className="mx-auto mb-4 text-neutral-400" size={32} />
        <p>No IPs resolved for this domain.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {net.resolved_ips.map(ip => {
        const details = net.details?.[ip];
        return (
          <div key={ip} className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-mono text-neutral-900 dark:text-white mb-4 border-b border-neutral-100 dark:border-neutral-800 pb-4">{ip}</h3>
            {details ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                <DetailRow label="Network Name" value={details.name || "-"} />
                <DetailRow label="Organization" value={details.organization || "-"} />
                <DetailRow label="CIDR" value={details.cidr || "-"} />
                <DetailRow label="Country" value={details.country || "-"} />
              </div>
            ) : (
              <p className="text-sm text-neutral-500">No RDAP information found for this IP.</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

function ErrorPlaceholder({ service, errors }: { service: string, errors: any[] }) {
  const serviceErrors = errors.filter(e => e.service.toLowerCase() === service.toLowerCase());
  return (
    <div className="p-8 text-center text-neutral-500 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 shadow-sm">
      <AlertCircle className="mx-auto mb-4 text-neutral-400" size={32} />
      <p>{service} data could not be retrieved.</p>
      {serviceErrors.map((err, i) => (
        <p key={i} className="text-red-500 dark:text-red-400 mt-2 text-sm">{err.message}</p>
      ))}
    </div>
  );
}

function DetailRow({ label, value, subValue }: { label: string, value: string, subValue?: string }) {
  return (
    <div className="flex flex-col sm:flex-row sm:justify-between py-2 border-b border-neutral-100 dark:border-neutral-800/50 last:border-0">
      <span className="text-neutral-500 text-sm">{label}</span>
      <div className="flex flex-col sm:items-end">
        <span className="text-neutral-900 dark:text-neutral-200 font-medium text-sm text-right break-all">{value}</span>
        {subValue && <span className="text-neutral-400 dark:text-neutral-500 text-xs mt-1">{subValue}</span>}
      </div>
    </div>
  );
}

function RawDataTab({ data }: { data: any }) {
  return (
    <div className="bg-neutral-900 dark:bg-black rounded-xl border border-neutral-800 overflow-hidden relative group shadow-sm">
      <pre className="p-6 overflow-x-auto text-xs text-green-400 font-mono">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
