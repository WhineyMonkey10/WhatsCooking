/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Serve HTML files directly with preserved query parameters
  async rewrites() {
    return [
      {
        source: '/index.html:path*',
        destination: '/index.html:path*',
      },
      {
        source: '/delete.html:path*',
        destination: '/delete.html:path*',
      },
    ];
  },
};

module.exports = nextConfig;
