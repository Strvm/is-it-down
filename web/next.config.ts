import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Next.js 15 lowered the default staleTimes.dynamic from 30s → 0s, which means
  // prefetched dynamic routes are treated as immediately stale and re-fetched on
  // every navigation. Restoring 30s keeps the prefetch payload usable for the
  // typical browse-back-and-click flow without requiring a full server round-trip.
  staleTimes: {
    dynamic: 30,
  },
};

export default nextConfig;
