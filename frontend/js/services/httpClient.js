export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "HttpError";
    this.status = status;
  }
}

export async function getJson(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" }
  });

  if (!response.ok) {
    const body = await response.text();
    const message = body || `HTTP ${response.status}`;
    throw new HttpError(response.status, message);
  }

  return response.json();
}
