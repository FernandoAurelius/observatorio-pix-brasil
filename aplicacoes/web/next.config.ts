import type { NextConfig } from "next";
// O navegador fala com a mesma origem. O Next apenas encaminha; não calcula estatísticas.
const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  async rewrites() {
    const destination = process.env.API_INTERNA ?? "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${destination}/api/:path*` }];
  },
  async headers() {
    return [{source: "/:path*", headers: [
      {key: "X-Content-Type-Options", value: "nosniff"},
      {key: "Referrer-Policy", value: "strict-origin-when-cross-origin"},
      {key: "X-Frame-Options", value: "DENY"}
    ]}];
  }
};
export default nextConfig;
