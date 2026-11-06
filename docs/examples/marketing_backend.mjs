/** Minimal Node BE adapter; authentication and database code belong to your BE.
 * Uses only built-in crypto/fetch. No frontend service credentials.
 */
import { createHmac, randomUUID } from 'node:crypto';

// Call only after BE authentication, active shop membership and role checks.
// Never pass req.body directly as verifiedIdentity.
export function issueAiToken(verifiedIdentity, env = process.env) {
  const { user_id, tenant_id, shop_id, role } = verifiedIdentity;
  if (![user_id, tenant_id, shop_id].every(v => typeof v === 'string' && v.length > 0)
      || !['owner', 'admin', 'analyst', 'viewer'].includes(role)) {
    throw new Error('Missing verified BE identity');
  }
  if (!env.WEB_TOKEN_SECRET || env.WEB_TOKEN_SECRET.length < 32) {
    throw new Error('Configure WEB_TOKEN_SECRET on BE');
  }
  const now = Math.floor(Date.now() / 1000);
  const encode = v => Buffer.from(JSON.stringify(v)).toString('base64url');
  const head = encode({ alg: 'HS256', typ: 'JWT' });
  const claims = encode({ user_id, tenant_id, shop_id, role, iat: now, exp: now + 120,
    iss: env.WEB_TOKEN_ISSUER || 'finora-web', aud: env.WEB_TOKEN_AUDIENCE || 'finora-ai' });
  const signature = createHmac('sha256', env.WEB_TOKEN_SECRET).update(`${head}.${claims}`).digest('base64url');
  return `${head}.${claims}.${signature}`;
}

const routes = new Set(['generate', 'rewrite', 'calendar', 'strategy', 'video-scripts/generate', 'video-scripts/adapt']);

export async function callMarketing({ verifiedIdentity, route, payload, idempotencyKey, env = process.env }) {
  if (!routes.has(route)) throw new Error('Unsupported marketing operation');
  if (!idempotencyKey) throw new Error('Persist one key per user action before calling AI');
  if (!env.FINORA_SERVICE_KEY || !env.FINORA_AI_URL) throw new Error('Configure AI URL and service key');
  const timeoutMs = Number(env.FINORA_MARKETING_HTTP_TIMEOUT_MS || 70000);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${env.FINORA_AI_URL.replace(/\/$/, '')}/api/v1/marketing/${route}`, {
      method: 'POST', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${issueAiToken(verifiedIdentity, env)}`,
        'X-Finora-Service-Key': env.FINORA_SERVICE_KEY, 'Idempotency-Key': idempotencyKey,
        'X-Request-ID': `req_be_${randomUUID()}` },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    // Preserve partial_success items and per-slot errors. A 409 IN_PROGRESS is
    // retried with the SAME key/body; a targeted generation retry uses a NEW key.
    return { httpStatus: response.status, body, retryAfter: response.headers.get('retry-after') };
  } finally {
    clearTimeout(timer);
  }
}

/** Map each returned item to your EXISTING BE versioning transaction.
 * Enforce a unique constraint on tenant/shop/client_reference in the BE.
 */
export async function persistMarketingResult({ verifiedIdentity, request, result, transaction }) {
  for (const item of result.items || []) {
    await transaction.appendDraftVersion({
      tenantId: verifiedIdentity.tenant_id, shopId: verifiedIdentity.shop_id, userId: verifiedIdentity.user_id,
      clientReference: item.client_reference, sku: item.sku, target: item.target,
      content: item.content, status: 'draft', productSnapshot: request.product,
      generationSettings: request, sourceVersionReference: item.source_version_reference,
      sourceClientReference: item.source_client_reference, aiMetadata: result.metadata,
    });
  }
  // Calendar references a specific version. Validate refs against this shop,
  // resolve new client refs to BE IDs after saving, then save the proposal.
  // Mark ready only after user review and comparison with current price/offer.
}
