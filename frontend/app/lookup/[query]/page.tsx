import { Metadata } from "next";
import { LookupClient } from "./LookupClient";

export async function generateMetadata({ params }: { params: Promise<{ query: string }> }): Promise<Metadata> {
  const resolvedParams = await params;
  return {
    title: `${decodeURIComponent(resolvedParams.query)} | Domain-Dora Intelligence`,
  };
}

export default async function LookupPage({ params }: { params: Promise<{ query: string }> }) {
  const resolvedParams = await params;
  const query = decodeURIComponent(resolvedParams.query);

  return <LookupClient query={query} />;
}
