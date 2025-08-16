/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // This configures Next.js to treat HTML files as static assets
  webpack: (config) => {
    config.module.rules.push({
      test: /\.html$/,
      type: 'asset/resource',
      generator: {
        filename: 'static/[hash][ext]',
      },
    });
    return config;
  },
};

module.exports = nextConfig;
