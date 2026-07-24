const CSRF_COOKIE =
  "neurovest_csrf";

export function readCsrfToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  for (
    const part
    of document.cookie.split(";")
  ) {
    const [
      rawName,
      ...rawValue
    ] = part.trim().split("=");

    if (rawName === CSRF_COOKIE) {
      return decodeURIComponent(
        rawValue.join("=")
      );
    }
  }

  return null;
}

export function csrfHeaders(): HeadersInit {
  const token = readCsrfToken();

  return token
    ? {
        "X-NeuroVest-CSRF": token,
      }
    : {};
}
