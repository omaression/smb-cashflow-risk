import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Demo app — keep every response (pages, route handlers, assets) out of
  // search indexes. Header applies on Vercel and in the standalone/Docker
  // server alike; the <meta name="robots"> in layout.tsx is the HTML fallback.
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex" }],
      },
    ];
  },
};

export default nextConfig;
