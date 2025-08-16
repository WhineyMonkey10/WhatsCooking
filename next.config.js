/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Serve HTML files directly
  async rewrites() {
    return [
      {
        source: '/index.html',
        destination: '/index.html',
      },
      {
        source: '/delete.html',
        destination: '/delete.html',
      },
    ];
  },
};

module.exports = nextConfig;
