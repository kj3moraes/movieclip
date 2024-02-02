/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        remotePatterns: [
            {
                hostname: "localhost",
                port: "8000"
            }
        ]
    }
};

export default nextConfig;
