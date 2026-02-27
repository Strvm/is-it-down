import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    // Next.js 15+ changed staleTimes.dynamic to 0, meaning visited dynamic routes
    // are never reused from the client router cache — Next.js always waits for a
    // fresh server response before transitioning (React 19 startTransition keeps
    // the old UI frozen for ~0.5s). Setting this to 30s keeps the visited route
    // entry in cache long enough for the typical back-and-click flow.
    staleTimes: {
      dynamic: 30,
    },
  },
};

export default nextConfig;
