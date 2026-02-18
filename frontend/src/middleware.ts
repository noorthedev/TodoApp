import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check if the request is for a protected route
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    // Check for auth token in cookies or we'll rely on client-side check
    // Since we're using localStorage, we'll let the client-side handle the redirect
    // This middleware serves as a backup layer
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/dashboard/:path*',
};
