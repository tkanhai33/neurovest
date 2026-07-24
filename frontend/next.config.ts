import type {
  NextConfig,
} from "next";

const isProduction =
  process.env.NODE_ENV === "production";

const contentSecurityPolicy = [
  "default-src 'self'",
  (
    "script-src 'self' 'unsafe-inline'"
    + (
      isProduction
        ? ""
        : " 'unsafe-eval'"
    )
  ),
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join("; ");

const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: contentSecurityPolicy,
  },
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  {
    key: "Referrer-Policy",
    value: "strict-origin-when-cross-origin",
  },
  {
    key: "Permissions-Policy",
    value:
      "camera=(), microphone=(), " +
      "geolocation=(), payment=(), usb=()",
  },
  {
    key: "X-Frame-Options",
    value: "DENY",
  },
  ...(isProduction
    ? [
        {
          key:
            "Strict-Transport-Security",
          value:
            "max-age=31536000; " +
            "includeSubDomains",
        },
      ]
    : []),
];

const nextConfig: NextConfig = {
  poweredByHeader: false,

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
      {
        source: "/dashboard/:path*",
        headers: [
          {
            key: "Cache-Control",
            value:
              "no-store, no-cache, " +
              "must-revalidate",
          },
        ],
      },
      {
        source: "/admin/:path*",
        headers: [
          {
            key: "Cache-Control",
            value:
              "no-store, no-cache, " +
              "must-revalidate",
          },
        ],
      },
      {
        source: "/api/:path*",
        headers: [
          {
            key: "Cache-Control",
            value:
              "no-store, no-cache, " +
              "must-revalidate",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
