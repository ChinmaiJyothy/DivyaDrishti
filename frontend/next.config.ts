import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.example.com",
      },
    ],
  },
};

export default nextConfig;
