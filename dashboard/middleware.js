export default function middleware(request) {
  const url = new URL(request.url);
  console.log(`[PISI Edge] ${request.method} ${url.pathname}${url.search} -> Forwarding to Render`);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
