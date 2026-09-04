import re
from typing import Dict, List, Any

# ---------------------------------------------------------------------------
# Signature schema
# ---------------------------------------------------------------------------
# Each entry has:
#   name: display name
#   rules: dict of detection signals
#     html:           regex patterns matched against full HTML text
#     inline_js:      regex patterns matched against inline <script> tag content
#     js_bundle:      regex patterns matched against fetched JS bundle content
#     headers:        list of (header_name, value_regex) tuples
#     cookies:        regex patterns matched against cookie names
#     scripts:        regex patterns matched against script src URLs
#     meta:           list of (meta_name, content_regex) tuples
# ---------------------------------------------------------------------------

TECHNOLOGY_SIGNATURES: Dict[str, List[Dict[str, Any]]] = {

    # -----------------------------------------------------------------------
    # FRONTEND FRAMEWORKS
    # -----------------------------------------------------------------------
    "frontend": [
        {
            "name": "Next.js",
            "rules": {
                "html": [
                    r'id="__next"',
                    r'__NEXT_DATA__',
                    r'__next_css__',
                    r'data-nextjs-scroll-focus-boundary',
                ],
                "inline_js": [
                    r'__NEXT_DATA__',
                    r'__NEXT_PUBLIC_',
                    r'next/dist/client',
                    r'"buildId"',
                ],
                "js_bundle": [
                    r'next/dist/client',
                    r'__webpack_require__.*_nextjs',
                    r'"next":"[\d\.]+',
                    r'next\.router\.push',
                    r'NextjsRouteMatcherError',
                    r'nextjs',
                ],
                "headers": [
                    ("X-Powered-By", r'next\.js'),
                    ("x-nextjs-cache", r'.*'),
                ],
                "scripts": [
                    r'/_next/static/',
                ],
            }
        },
        {
            "name": "React",
            "rules": {
                "html": [
                    r'data-reactroot',
                    r'data-reactid',
                    r'__reactFiber',
                    r'__reactProps',
                ],
                "inline_js": [
                    r'React\.createElement',
                    r'ReactDOM\.render',
                    r'ReactDOM\.createRoot',
                    r'react-dom',
                ],
                "js_bundle": [
                    r'react\.development\.js',
                    r'react\.production\.min\.js',
                    r'"react":"[\d\.]+',
                    r'React\.createElement',
                    r'ReactDOM\.createRoot',
                    r'__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED',
                    r'react-dom',
                ],
                "scripts": [
                    r'react\.min\.js',
                    r'react-dom\.min\.js',
                ],
            }
        },
        {
            "name": "Vue.js",
            "rules": {
                "html": [
                    r'data-v-[a-f0-9]{7,8}',
                    r'__vue_app__',
                    r'v-cloak',
                ],
                "inline_js": [
                    r'createApp\(',
                    r'Vue\.createApp',
                    r'new Vue\(',
                ],
                "js_bundle": [
                    r'"vue":"[\d\.]+',
                    r'Vue\.createApp',
                    r'__VUE_DEVTOOLS_GLOBAL_HOOK__',
                    r'__vue_app__',
                    r'@vue/runtime-dom',
                ],
                "scripts": [
                    r'vue\.global\.js',
                    r'vue\.esm-browser\.js',
                ],
            }
        },
        {
            "name": "Nuxt.js",
            "rules": {
                "html": [
                    r'id="__nuxt"',
                    r'__NUXT_DATA__',
                    r'data-n-head',
                ],
                "inline_js": [
                    r'window\.__nuxt',
                    r'window\.__NUXT__',
                ],
                "js_bundle": [
                    r'nuxt/dist/app',
                    r'nuxt-app',
                ],
                "scripts": [
                    r'/_nuxt/',
                ],
            }
        },
        {
            "name": "Angular",
            "rules": {
                "html": [
                    r'ng-version="',
                    r'ng-app',
                    r'<app-root',
                    r'_nghost-',
                    r'_ngcontent-',
                ],
                "js_bundle": [
                    r'@angular/core',
                    r'platformBrowserDynamic',
                    r'BrowserModule',
                    r'NgModule',
                ],
            }
        },
        {
            "name": "Svelte",
            "rules": {
                "html": [
                    r'svelte-',
                    r'class="s-[A-Za-z0-9_-]{8}"',
                ],
                "js_bundle": [
                    r'"svelte":"[\d\.]+',
                    r'SvelteComponent',
                    r'svelte/internal',
                ],
            }
        },
        {
            "name": "SvelteKit",
            "rules": {
                "html": [
                    r'data-sveltekit',
                    r'sveltekit:',
                ],
                "js_bundle": [
                    r'@sveltejs/kit',
                ],
            }
        },
        {
            "name": "Astro",
            "rules": {
                "html": [
                    r'astro-island',
                    r'data-astro-cid',
                ],
                "js_bundle": [
                    r'astro:',
                    r'astroIntegration',
                ],
                "headers": [
                    ("x-astro-cache", r'.*'),
                ],
            }
        },
        {
            "name": "Gatsby",
            "rules": {
                "html": [
                    r'id="___gatsby"',
                    r'gatsby-image-wrapper',
                ],
                "headers": [
                    ("X-Powered-By", r'gatsby'),
                ],
                "meta": [
                    ("generator", r'gatsby'),
                ],
                "js_bundle": [
                    r'"gatsby":"[\d\.]+',
                    r'gatsby-plugin',
                    r'gatsby/dist/public-page-renderer',
                ],
                "scripts": [
                    r'/page-data/',
                ],
            }
        },
        {
            "name": "Remix",
            "rules": {
                "html": [
                    r'__remixContext',
                    r'data-remix-run',
                ],
                "inline_js": [
                    r'window\.__remixContext',
                    r'RemixBrowser',
                ],
                "js_bundle": [
                    r'@remix-run/react',
                    r'remix-run',
                ],
                "scripts": [
                    r'/build/_shared/',
                ],
            }
        },
        {
            "name": "Tailwind CSS",
            "rules": {
                "html": [
                    # Tailwind utility class patterns (very reliable)
                    r'\bclass="[^"]*\b(?:flex|grid|hidden|block|inline-flex|items-center|justify-between|gap-\d|p-\d|px-\d|py-\d|m-\d|mx-\d|my-\d|text-(?:sm|base|lg|xl|2xl|3xl)|font-(?:bold|semibold|medium)|rounded(?:-\w+)?|border(?:-\w+)?|bg-(?:white|black|gray|slate|blue|red|green|yellow|purple|indigo|orange|pink|sky|cyan|teal|lime|amber|emerald|violet|fuchsia|rose)-\d+|text-(?:gray|slate|blue|red|green|yellow|purple|indigo|orange|pink|sky|cyan|teal|lime|amber|emerald|violet|fuchsia|rose)-\d+|hover:|focus:|dark:|lg:|md:|sm:|xl:)\b',
                    r'tailwindcss',
                ],
                "js_bundle": [
                    r'tailwindcss',
                ],
            }
        },
        {
            "name": "Bootstrap",
            "rules": {
                "html": [
                    r'class="[^"]*(?:container|row|col-(?:xs|sm|md|lg|xl)-\d+|btn btn-|navbar|navbar-|modal fade|d-flex|d-none)',
                    r'bootstrap\.min\.css',
                    r'bootstrap\.css',
                ],
                "scripts": [
                    r'bootstrap(?:\.bundle)?(?:\.min)?\.js',
                ],
                "js_bundle": [
                    r'"bootstrap":"[\d\.]+',
                ],
            }
        },
        {
            "name": "Material UI (MUI)",
            "rules": {
                "html": [
                    r'class="[^"]*Mui[A-Z][a-zA-Z]+-',
                ],
                "js_bundle": [
                    r'@mui/material',
                    r'"@mui/material":"[\d\.]+',
                    r'MuiButton',
                    r'MuiThemeProvider',
                ],
            }
        },
        {
            "name": "WordPress",
            "rules": {
                "html": [
                    r'/wp-content/',
                    r'/wp-includes/',
                    r'<link[^>]+/wp-content/',
                ],
                "meta": [
                    ("generator", r'wordpress'),
                ],
                "cookies": [r'wordpress_', r'wp-settings-'],
            }
        },
        {
            "name": "Shopify",
            "rules": {
                "html": [
                    r'cdn\.shopify\.com',
                    r'Shopify\.shop',
                    r'myshopify\.com',
                ],
                "inline_js": [
                    r'Shopify\.theme',
                    r'window\.Shopify',
                ],
            }
        },
    ],

    # -----------------------------------------------------------------------
    # JAVASCRIPT PACKAGES (detected via bundle content)
    # -----------------------------------------------------------------------
    "packages": [
        {
            "name": "Three.js",
            "rules": {
                "js_bundle": [
                    r'"three":"[\d\.]+',
                    r'THREE\.WebGLRenderer',
                    r'THREE\.Scene',
                    r'three/build/three',
                ],
                "scripts": [r'three(?:\.min)?\.js'],
            }
        },
        {
            "name": "GSAP",
            "rules": {
                "js_bundle": [
                    r'"gsap":"[\d\.]+',
                    r'gsap\.to\(',
                    r'gsap\.timeline',
                    r'TweenMax',
                    r'TweenLite',
                    r'ScrollTrigger',
                ],
                "scripts": [r'gsap(?:\.min)?\.js', r'TweenMax', r'ScrollTrigger'],
            }
        },
        {
            "name": "Framer Motion",
            "rules": {
                "js_bundle": [
                    r'framer-motion',
                    r'AnimatePresence',
                    r'\.motion\.div',
                    r'\.motion\.button',
                    r'\.motion\.span',
                    r'\.motion\.a',
                    r'useAnimation\(',
                    r'useMotionValue',
                    r'motionValue\(',
                ],
            }
        },
        {
            "name": "Axios",
            "rules": {
                "js_bundle": [
                    r'"axios":"[\d\.]+',
                    r'axios\.create\(',
                    r'axios\.get\(',
                    r'axios\.post\(',
                ],
                "scripts": [r'axios(?:\.min)?\.js'],
            }
        },
        {
            "name": "Lodash",
            "rules": {
                "js_bundle": [
                    r'"lodash":"[\d\.]+',
                    r'lodash/lodash',
                    r'var _=require\("lodash"\)',
                ],
                "scripts": [r'lodash(?:\.min)?\.js'],
            }
        },
        {
            "name": "jQuery",
            "rules": {
                "html": [
                    r'jQuery\(',
                    r'\$\(document\)\.ready',
                ],
                "js_bundle": [
                    r'"jquery":"[\d\.]+',
                    r'jQuery\.fn\.jquery',
                ],
                "scripts": [r'jquery(?:-\d[\d\.]*)?(?:\.min)?\.js'],
            }
        },
        {
            "name": "Swiper",
            "rules": {
                "js_bundle": [r'"swiper":"[\d\.]+', r'new Swiper\('],
                "html": [r'class="[^"]*swiper(?:-container|-wrapper|-slide)"'],
                "scripts": [r'swiper(?:\.min)?\.js'],
            }
        },
        {
            "name": "Chart.js",
            "rules": {
                "js_bundle": [r'"chart\.js":"[\d\.]+', r'new Chart\('],
                "scripts": [r'chart(?:\.min)?\.js'],
            }
        },
        {
            "name": "D3.js",
            "rules": {
                "js_bundle": [r'"d3":"[\d\.]+', r'd3\.select\(', r'd3\.selectAll\('],
                "scripts": [r'd3(?:\.min)?\.js'],
            }
        },
        {
            "name": "Zustand",
            "rules": {
                "js_bundle": [r'"zustand":"[\d\.]+', r'zustand/vanilla', r'createStore.*zustand'],
            }
        },
        {
            "name": "Redux",
            "rules": {
                "js_bundle": [r'"redux":"[\d\.]+', r'createStore\(', r'Redux\.createStore'],
            }
        },
        {
            "name": "Redux Toolkit",
            "rules": {
                "js_bundle": [r'"@reduxjs/toolkit":"[\d\.]+', r'configureStore\(', r'createSlice\('],
            }
        },
        {
            "name": "TanStack Query",
            "rules": {
                "js_bundle": [r'"@tanstack/react-query":"[\d\.]+', r'useQuery\(', r'QueryClient'],
            }
        },
        {
            "name": "SWR",
            "rules": {
                "js_bundle": [r'"swr":"[\d\.]+', r'useSWR\('],
            }
        },
        {
            "name": "Lucide React",
            "rules": {
                "js_bundle": [
                    r'lucide-react',
                    r'"lucide-react":"[\d\.]+',
                ],
            }
        },
        {
            "name": "React Icons",
            "rules": {
                "js_bundle": [
                    r'react-icons',
                    r'"react-icons":"[\d\.]+',
                ],
            }
        },
        {
            "name": "Recharts",
            "rules": {
                "js_bundle": [
                    r'recharts',
                    r'"recharts":"[\d\.]+',
                    r'ComposedChart',
                    r'BarChart',
                ],
            }
        },
        {
            "name": "Embla Carousel",
            "rules": {
                "js_bundle": [
                    r'embla-carousel',
                    r'EmblaCarousel',
                ],
            }
        },
        {
            "name": "Radix UI",
            "rules": {
                "js_bundle": [
                    r'@radix-ui',
                    r'radix-ui',
                ],
            }
        },
        {
            "name": "React Hook Form",
            "rules": {
                "js_bundle": [
                    r'react-hook-form',
                    r'useForm\(',
                    r'"react-hook-form":"[\d\.]+',
                ],
            }
        },
        {
            "name": "Zod",
            "rules": {
                "js_bundle": [
                    r'zod',
                    r'\.safeParse\(',
                    r'z\.object\(',
                    r'z\.string\(',
                ],
            }
        },
    ],

    # -----------------------------------------------------------------------
    # BACKEND (passive inference from headers/cookies)
    # -----------------------------------------------------------------------
    "backend": [
        {
            "name": "Node.js (Next.js SSR / Serverless)",
            "rules": {
                "headers": [
                    ("x-nextjs-prerender", r'.*'),
                    ("x-matched-path", r'.*'),
                    ("vary", r'rsc|next-router'),
                ],
                "inline_js": [
                    r'__NEXT_DATA__',
                    r'__NEXT_PUBLIC_',
                ],
                "js_bundle": [
                    r'next/dist/server',
                    r'NextjsRouteMatcherError',
                ],
                "scripts": [
                    r'/_next/static/',
                ],
            }
        },
        {
            "name": "Node.js (Nuxt SSR)",
            "rules": {
                "inline_js": [
                    r'window\.__NUXT__',
                    r'__NUXT_DATA__',
                ],
                "scripts": [
                    r'/_nuxt/',
                ],
            }
        },
        {
            "name": "Node.js (Remix SSR)",
            "rules": {
                "inline_js": [
                    r'window\.__remixContext',
                    r'RemixBrowser',
                ],
                "scripts": [
                    r'/build/_shared/',
                ],
            }
        },
        {
            "name": "Node.js",
            "rules": {
                "headers": [
                    ("X-Powered-By", r'node\.?js|express|nestjs'),
                ],
                "cookies": [
                    r'connect\.sid',
                ],
                "js_bundle": [
                    r'require\("node:',
                ],
            }
        },
        {
            "name": "Express.js",
            "rules": {
                "headers": [("X-Powered-By", r'express')],
            }
        },
        {
            "name": "NestJS",
            "rules": {
                "headers": [("X-Powered-By", r'nestjs')],
                "js_bundle": [r'@nestjs/core', r'@nestjs/common'],
            }
        },
        {
            "name": "PHP",
            "rules": {
                "headers": [("X-Powered-By", r'php'), ("server", r'litespeed')],
                "cookies": [r'PHPSESSID'],
                "html": [r'/wp-content/', r'/wp-includes/'],
            }
        },
        {
            "name": "Laravel (PHP)",
            "rules": {
                "cookies": [r'laravel_session', r'XSRF-TOKEN'],
                "html": [r'csrf-token.*Laravel'],
            }
        },
        {
            "name": "WordPress (PHP Backend)",
            "rules": {
                "html": [r'/wp-content/', r'/wp-includes/', r'/wp-json/'],
                "meta": [("generator", r'wordpress')],
                "cookies": [r'wordpress_', r'wp-settings-'],
            }
        },
        {
            "name": "Django (Python)",
            "rules": {
                "cookies": [r'csrftoken', r'django_language', r'sessionid'],
                "html": [r'name="csrfmiddlewaretoken"'],
            }
        },
        {
            "name": "FastAPI / Python",
            "rules": {
                "headers": [("server", r'uvicorn|gunicorn|werkzeug'), ("x-process-time", r'.*')],
            }
        },
        {
            "name": "Ruby on Rails",
            "rules": {
                "headers": [("X-Powered-By", r'phusion passenger'), ("X-Runtime", r'.*')],
                "cookies": [r'_.*_session'],
                "html": [r'csrf-param.*authenticity_token'],
            }
        },
        {
            "name": "Java (Spring Boot)",
            "rules": {
                "cookies": [r'JSESSIONID'],
                "headers": [("X-Application-Context", r'.*')],
            }
        },
        {
            "name": "ASP.NET (C#)",
            "rules": {
                "headers": [("X-Powered-By", r'asp\.net'), ("X-AspNet-Version", r'.*'), ("server", r'kestrel')],
                "cookies": [r'ASP\.NET_SessionId', r'\.ASPXAUTH'],
            }
        },
        {
            "name": "GraphQL API",
            "rules": {
                "js_bundle": [r'__typename', r'gql`', r'@apollo/client', r'urql'],
                "html": [r'graphql'],
            }
        },
        {
            "name": "Supabase / PostgreSQL",
            "rules": {
                "js_bundle": [r'@supabase/supabase-js', r'supabase-js', r'supabase\.co'],
                "inline_js": [r'supabase\.co', r'SUPABASE_URL'],
            }
        },
        {
            "name": "Firebase / Firestore",
            "rules": {
                "js_bundle": [r'firebase/app', r'firebase/firestore', r'firebase\.google\.com'],
                "inline_js": [r'firebaseConfig', r'firebase\.initializeApp'],
            }
        },
    ],

    # -----------------------------------------------------------------------
    # INFRASTRUCTURE & HOSTING
    # -----------------------------------------------------------------------
    "infrastructure": [
        {
            "name": "Hostinger",
            "rules": {
                "headers": [
                    ("server", r'hcdn'),
                    ("platform", r'hostinger'),
                    ("panel", r'hpanel'),
                    ("x-hcdn-request-id", r'.*'),
                    ("x-hcdn-cache-status", r'.*'),
                ],
            }
        },
        {
            "name": "Render",
            "rules": {
                "headers": [("x-render-origin-server", r'.*')],
            }
        },
        {
            "name": "Railway",
            "rules": {
                "headers": [("x-railway-routing", r'.*')],
            }
        },
        {
            "name": "Fly.io",
            "rules": {
                "headers": [("server", r'fly'), ("via", r'fly\.io')],
            }
        },
        {
            "name": "WP Engine",
            "rules": {
                "headers": [("wpe-backend", r'.*'), ("x-powered-by", r'wp engine')],
            }
        },
        {
            "name": "Pantheon",
            "rules": {
                "headers": [("x-pantheon-styx-hostname", r'.*')],
            }
        },
        {
            "name": "Cloudflare",
            "rules": {
                "headers": [
                    ("server", r'cloudflare'),
                    ("cf-ray", r'.*'),
                    ("cf-cache-status", r'.*'),
                    ("cf-request-id", r'.*'),
                ],
                "cookies": [r'__cfduid', r'cf_clearance', r'__cf_bm'],
            }
        },
        {
            "name": "Vercel",
            "rules": {
                "headers": [
                    ("server", r'vercel'),
                    ("x-vercel-id", r'.*'),
                    ("x-vercel-cache", r'.*'),
                ],
                "scripts": [r'/_next/'],
            }
        },
        {
            "name": "Netlify",
            "rules": {
                "headers": [
                    ("server", r'netlify'),
                    ("x-nf-request-id", r'.*'),
                ],
            }
        },
        {
            "name": "AWS / ELB",
            "rules": {
                "headers": [("server", r'awselb'), ("x-amz-request-id", r'.*')],
                "cookies": [r'AWSELB', r'AWSALB'],
            }
        },
        {
            "name": "Amazon CloudFront",
            "rules": {
                "headers": [
                    ("via", r'cloudfront'),
                    ("x-amz-cf-id", r'.*'),
                    ("x-cache", r'cloudfront'),
                ],
            }
        },
        {
            "name": "Google Cloud / Firebase",
            "rules": {
                "headers": [
                    ("server", r'gws|firebase'),
                    ("x-goog-request-id", r'.*'),
                    ("x-firebase-appcheck", r'.*'),
                ],
            }
        },
        {
            "name": "Azure",
            "rules": {
                "headers": [
                    ("server", r'microsoft-iis'),
                    ("x-ms-request-id", r'.*'),
                    ("x-powered-by", r'asp\.net'),
                ],
                "cookies": [r'ARRAffinity'],
            }
        },
        {
            "name": "Nginx",
            "rules": {
                "headers": [("server", r'nginx')],
            }
        },
        {
            "name": "Apache",
            "rules": {
                "headers": [("server", r'apache')],
            }
        },
        {
            "name": "Fastly",
            "rules": {
                "headers": [
                    ("x-fastly-request-id", r'.*'),
                    ("x-served-by", r'cache'),
                    ("fastly-debug-digest", r'.*'),
                ],
            }
        },
        {
            "name": "Akamai",
            "rules": {
                "headers": [
                    ("x-akamai-transformed", r'.*'),
                    ("x-check-cacheable", r'.*'),
                ],
            }
        },
        {
            "name": "GitHub Pages",
            "rules": {
                "html": [r'github\.io'],
                "headers": [("server", r'github\.com')],
            }
        },
    ],

    # -----------------------------------------------------------------------
    # CDN (separate from infra for clarity)
    # -----------------------------------------------------------------------
    "cdn": [
        {
            "name": "Cloudflare CDN",
            "rules": {
                "headers": [("cf-ray", r'.*'), ("cf-cache-status", r'.*')],
            }
        },
        {
            "name": "jsDelivr",
            "rules": {
                "scripts": [r'cdn\.jsdelivr\.net'],
                "html": [r'cdn\.jsdelivr\.net'],
            }
        },
        {
            "name": "cdnjs",
            "rules": {
                "scripts": [r'cdnjs\.cloudflare\.com'],
                "html": [r'cdnjs\.cloudflare\.com'],
            }
        },
        {
            "name": "Google CDN",
            "rules": {
                "scripts": [r'ajax\.googleapis\.com'],
                "html": [r'ajax\.googleapis\.com|fonts\.googleapis\.com'],
            }
        },
        {
            "name": "unpkg",
            "rules": {
                "scripts": [r'unpkg\.com'],
            }
        },
    ],

    # -----------------------------------------------------------------------
    # ANALYTICS & THIRD-PARTY SERVICES
    # -----------------------------------------------------------------------
    "analytics": [
        {
            "name": "Google Analytics 4",
            "rules": {
                "scripts": [r'googletagmanager\.com/gtag/js'],
                "inline_js": [r"gtag\('config',", r'G-[A-Z0-9]{6,10}'],
                "cookies": [r'_ga', r'_gid', r'_gac_'],
            }
        },
        {
            "name": "Google Analytics (Universal)",
            "rules": {
                "scripts": [r'google-analytics\.com/analytics\.js'],
                "inline_js": [r"ga\('create',", r'UA-\d+-\d+'],
                "cookies": [r'_ga', r'_gid'],
            }
        },
        {
            "name": "Google Tag Manager",
            "rules": {
                "scripts": [r'googletagmanager\.com/gtm\.js'],
                "inline_js": [r'GTM-[A-Z0-9]{4,8}'],
                "html": [r'googletagmanager\.com/ns\.html'],
            }
        },
        {
            "name": "Meta Pixel",
            "rules": {
                "scripts": [r'connect\.facebook\.net/[^/]+/fbevents\.js'],
                "inline_js": [r"fbq\('init',"],
                "cookies": [r'_fbp', r'_fbc'],
            }
        },
        {
            "name": "Hotjar",
            "rules": {
                "scripts": [r'static\.hotjar\.com/c/hotjar-'],
                "inline_js": [r'hjid:', r'hotjar'],
                "cookies": [r'_hjSessionUser_', r'_hjSession_'],
            }
        },
        {
            "name": "Microsoft Clarity",
            "rules": {
                "scripts": [r'clarity\.ms/tag/'],
                "inline_js": [r'clarity\("set"', r'window\.clarity'],
                "cookies": [r'_clck', r'_clsk'],
            }
        },
        {
            "name": "Sentry",
            "rules": {
                "scripts": [r'browser\.sentry-cdn\.com', r'js\.sentry-cdn\.com'],
                "js_bundle": [r'"@sentry/browser":"[\d\.]+', r'Sentry\.init\('],
            }
        },
        {
            "name": "Intercom",
            "rules": {
                "scripts": [r'widget\.intercom\.io', r'js\.intercomcdn\.com'],
                "inline_js": [r'window\.intercomSettings', r'Intercom\("boot"'],
                "cookies": [r'intercom-'],
            }
        },
        {
            "name": "Stripe",
            "rules": {
                "scripts": [r'js\.stripe\.com/v\d'],
                "js_bundle": [r'"@stripe/stripe-js"', r'Stripe\('],
            }
        },
        {
            "name": "HubSpot",
            "rules": {
                "scripts": [r'js\.hs-scripts\.com', r'js\.hsforms\.net'],
                "cookies": [r'__hstc', r'hubspotutk', r'__hssc'],
            }
        },
    ],
}
