/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "wordpress-1592891-6259767.cloudwaysapps.com",
      },
      {
        protocol: "https",
        hostname: "secure.gravatar.com",
      },
    ],
  },
};

export default nextConfig;
