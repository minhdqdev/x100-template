# Next.js Best Practices (2025 Edition)

## 0. Baseline tech & structure

- **Versions:** Next 15.x, React 19, TypeScript strict, ESLint (next/core-web-vitals), Ruff-equivalent for JS? Use **Biome** (fast) or ESLint+Prettier.
- **Folders:**
    `repo/   apps/web/ (Next.js)   packages/ui/ (design system, headless + Tailwind)   packages/config/ (tsconfig, eslint, shared types)   deploy/ (docker, deploy, terraform)`
    If single app, keep `/src` with `app/`, `lib/`, `components/`, `styles/`, `server/`, `db/`.
- **Module boundaries:** `app/` for routing & server components, `components/` for client components, `lib/` for pure utils, `server/` for actions/services (server-only), `db/` for Prisma.

## 1. TypeScript & config hygiene

- **tsconfig:** `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`, `moduleDetection: force`.
- Add **ambient types** for env (see §7). Export **public types** from a `@types` package to keep contracts consistent between UI and API.

## 2. Routing, layouts & conventions (App Router)

- Use **nested layouts** (`app/(marketing)/...`, `app/(app)/...`) for clear UX shells.
- Keep **route handlers** in `app/api/*/route.ts` for simple cases; push complex logic into `server/services/*`.
- Co-locate **loading.tsx** and **error.tsx** per route; avoid global catch-alls swallowing useful errors.

## 3. Data fetching & server-first thinking

- Default to **Server Components**. They’re fast, bundle-free, and cache-friendly.
- Use **Server Actions** for mutations (form posts, button clicks) when you don’t need a separate API client. Validate with **Zod** on the server boundary.
- Prefer **fetch()** on the server with **Response caching**:
    - Static data → `fetch(url, { next: { revalidate: 3600 } })`
        
    - Per-request fresh → `{ cache: 'no-store' }`
        
    - Tag invalidation → `revalidateTag('user:123')` from server action after writes.
        
- For DB access (Prisma), call in server components or server actions only. Never ship secrets client-side.

## 4. Caching strategy that actually works

- **Static Generation** where possible (marketing, docs).
- **Incremental Revalidation** for semi-static pages; set a sane TTL + tag invalidation on write.
- **Route Segment Caching**: let Next cache RSC payloads; avoid client-only waterfalls.
- **CDN**: put a CDN in front (Vercel Edge or Cloudflare). Serve images, fonts, and static assets from edge.

## 5. Client components & state

- Use client components **sparingly** (forms, interactive charts, drag-n-drop).
- Local state → React useState/useReducer; global app state → **Zustand** or **Redux Toolkit** only if you truly need cross-tree writes. Don’t hold server data in client state longer than necessary.
- For client data fetching (when needed): **React Query** + `{ staleTime }` + **suspense** mode; hydrate from server via `dehydrate()` to avoid double-fetch.

## 6. Styling & design system

- **Tailwind** + a small **headless UI kit** (Radix/HeadlessUI) and a local **`packages/ui`** design system (tokens, primitives, compound components).
- Use **CSS variables** for theming; co-locate component styles; avoid global CSS beyond base resets and tokens.

## 7. Environment & secrets

- Split envs: `.env.local` (dev), `.env` for CI, runtime secrets via platform. Never commit secrets.
- **Validate env at startup** using Zod:
    `// server/env.ts import { z } from 'zod'; export const Env = z.object({   DATABASE_URL: z.string().url(),   NEXTAUTH_SECRET: z.string().min(32),   NEXT_PUBLIC_APP_NAME: z.string(), }); export const env = Env.parse(process.env);`
- Only expose `NEXT_PUBLIC_*` to the client. Everything else is server-only.

## 8. AuthN/Z

- **Auth**: NextAuth.js (Auth.js) with passwordless or OAuth, or your JWT provider. Store sessions in DB/Redis; rotate tokens.
- **Authorization**: centralize policies in `server/authorization/*` (ABAC-style functions). Use these inside server actions and route handlers. Do not gate on client-only checks.

## 9. Database with Prisma

- Enable **Prisma strict**: `prisma.schema` with explicit relations and `@map`/`@@index`.
- Add **row-level guards** in queries (tenantId scoping).
- Use **migrate** in CI, and **prisma generate** during build.
- For heavy reads, create **computed read models** or materialized views; don’t abuse `include` trees—load only needed columns.

## 10. Performance

- Keep **P95 TTFB** under ~200ms for dynamic routes.
- **Images:** Next/Image with `fill` or width/height set; AVIF/WebP; CDN optimization on.
- **Fonts:** self-host with `next/font`; use `display: swap`.
- **Scripts:** `strategy="afterInteractive"` or `lazyOnload` for non-critical; avoid third-party bloat.
- **Minimize Client JS:** Prefer RSC; move logic to server; split client islands thoughtfully.
- **Edge runtime** for lightweight logic at the network edge (geo, A/B, headers). Avoid heavy Node APIs there.

## 11. Error handling & UX resilience

- Co-locate `error.tsx` per route; show friendly messages, not stack traces.
- Wrap server actions with a tiny helper to map Zod errors → user-readable messages.
- Use **problem-detail** semantics for API errors.
- Add **user journey fallbacks**: optimistic UI for simple mutations; pessimistic with toasts for risky operations.

## 12. Observability

- **Logging:** server-side structured logs (pino or console JSON on Vercel), include request id, user id, tenant id.
- **Tracing:** OpenTelemetry SDK; instrument route handlers and server actions; export OTLP to Grafana Tempo or vendor.
- **Metrics:** basic counters for requests, cache hits, mutations; push to Prometheus (via OTEL) or vendor.
- **Errors:** Sentry with source maps; tag release, route, user/tenant (PII-safe).

## 13. Security

- **Headers:** Next’s built-ins + strict **CSP** (nonce/sha256 for inline), `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.
- **Cookies:** `Secure`, `HttpOnly`, `SameSite=Lax|Strict`.
- **Rate limiting:** edge middleware (IP + user key).
- **Input validation:** Zod on all server boundaries (actions/route handlers).
- **SSRFs & fetch:** only call allowlisted origins; timeouts and abort signals on `fetch`.
- **Dependency hygiene:** `pnpm audit` in CI; Renovate bot for updates.

## 14. Middleware & edge

- Use `middleware.ts` for lightweight cross-cutting concerns: auth guards, geo routing, A/B flags, bot blocking.
- Keep it **fast** and **stateless**; read only `cookies()` you need; avoid DB calls.

## 15. Internationalization & accessibility

- **i18n routing** with `@vercel/edge` matcher or Next’s built-in. Store messages per locale, lazy load.
- **A11y:** use semantic HTML; run **eslint-plugin-jsx-a11y**; audit with Lighthouse and axe. Keyboard first, focus rings visible.

## 16. SEO & social

- Use **Metadata API** in the App Router for titles, descriptions, canonical, OG/Twitter images.
- Stable URLs, avoid dynamic title churn; sitemap & robots.txt via route handlers.
- Generate **OG images** at build or on-demand edge function.

## 17. Testing

- **Unit**: Vitest or Jest for utils & components.
- **Component**: React Testing Library (client) and **RSC testing** for server components with `@testing-library/react` + Next test utils.
- **E2E**: Playwright; run against preview URL in CI.
- Add a **performance smoke** (Lighthouse CI) for key pages.
- Contract tests for server actions and APIs (zod schema roundtrips).

## 18. CI/CD

- **CI**: typecheck, lint, test, build (generate Prisma client), preview deploy on PR.
- **Caching**: `pnpm` store, `.next/cache` between CI steps.
- **CD**: canary/preview → run smoke tests → promote to prod. Keep **/version** and **git SHA** exposed.
- **Warm revalidation** tasks post-deploy for hot pages.

## 19. Analytics & product loops

- **Privacy-first** analytics (Plausible/Umami) or first-party events.
- Send **server-side events** for critical funnels (server actions know the truth).
- A/B flags from an edge-capable provider; keep variants pure and small.

## 20. DX niceties

- **pnpm** workspaces.
- **Turborepo** cache for build/test/lint.
- **Graph of tasks**: `turbo run build --filter=...` per package.
- **Pre-commit** hooks: typecheck, eslint/biome, format.
- **Storybook** for the design system (runs against server-mocked data).

## 21. Content, images, uploads

- Store files in S3/GCS with **signed URLs**; never stream through the Next server for large payloads.
- Use **next/image** loaders + CDN.
- For rich text, use **Contentlayer** or MDX for docs/marketing; keep MDX server-rendered, not client-hydrated, unless interactive.

## 22. Multitenancy patterns

- Tenant ID in session & URL (e.g., `app.my.com/acme/...`) or subdomain routing via middleware.
- Prefix cache tags with tenant; ensure Prisma queries are tenant-scoped and covered by DB constraints.

## 23. Production hardening checklist

-  `NODE_ENV=production`, `NEXT_TELEMETRY_DISABLED=1` (if policy requires).
-  CSP in **enforce** mode (after a period of report-only).
-  All dynamic routes have `error.tsx` and `loading.tsx`.
-  No secret access in client bundles (verify with `next build` analyze).
-  Sentry + OTEL exporting, release tags wired.
-  Revalidation tags on every write path.
-  E2E green on preview; Lighthouse P95 ≥ 90 on core pages.
-  DB migrations run before promote; seed scripts idempotent.

---

## Code seeds

**Server Action with validation + revalidation**

```ts
// app/(app)/projects/actions.ts
'use server';
import { z } from 'zod'; import { revalidateTag } from 'next/cache'; import { db } from '@/db';  const Create = z.object({ name: z.string().min(2), tenantId: z.string().uuid() });  export async function createProject(input: unknown) {   const { name, tenantId } = Create.parse(input);   const project = await db.project.create({ data: { name, tenantId } });   revalidateTag(`projects:${tenantId}`);   return project.id; }
```

**Server Component fetching with tag caching**

```ts
// app/(app)/projects/page.tsx
import { unstable_cache } from 'next/cache';  const getProjects = unstable_cache(async (tenantId: string) => {   const res = await fetch(`${process.env.API_URL}/projects?tenantId=${tenantId}`, {     next: { tags: [`projects:${tenantId}`], revalidate: 300 },   });   return res.json(); }, ['projects'], { revalidate: 300 });  export default async function Projects({ params }: { params: { tenantId: string } }) {   const list = await getProjects(params.tenantId);   return <ProjectTable data={list} />; // client or server component as needed }
```

**Middleware for simple auth guard**

```ts
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
export function middleware(req: NextRequest) {   if (req.nextUrl.pathname.startsWith('/app')) {     const session = req.cookies.get('session')?.value;     if (!session) return NextResponse.redirect(new URL('/login', req.url));   }   return NextResponse.next(); }  export const config = {   matcher: ['/app/:path*'], };
```

---

## TL;DR setup (pin these)

- **Core:** Next 15, React 19, TS strict, Tailwind, Radix, Zod, Prisma, NextAuth, React Query (optional), Playwright, Sentry, OTEL, Turborepo, pnpm.
- **Philosophy:** server-first, cache-savvy, client-light, edge-aware, traceable, and boring where it matters.