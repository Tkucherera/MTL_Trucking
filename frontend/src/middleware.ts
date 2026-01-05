import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Note: We're checking localStorage in the client-side code
  // Middleware can't access localStorage, so we handle redirects client-side
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
};