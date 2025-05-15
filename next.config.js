/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    PRIVATE_KEY: process.env.PRIVATE_KEY,
    RPC_URL: process.env.RPC_URL,
    CHAIN_ID: process.env.CHAIN_ID,
    ROUTER_ADDRESS: process.env.ROUTER_ADDRESS,
    TOKEN_IN: process.env.TOKEN_IN,
    TOKEN_OUT: process.env.TOKEN_OUT
  }
}

module.exports = nextConfig
