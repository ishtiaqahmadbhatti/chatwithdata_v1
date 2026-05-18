// Pure JavaScript Lambda Runtime Loop - NO native dependencies!
// Implements AWS Lambda Runtime API directly using Node.js built-in http module.
// Replaces aws-lambda-ric entirely — zero apt-get, zero native compilation.

import { readFileSync } from 'fs';
import { join, extname } from 'path';
import http from 'http';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const RUNTIME_API = process.env.AWS_LAMBDA_RUNTIME_API;
const PUBLIC_DIR = join(__dirname, 'public');

// MIME types
const MIME = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.mjs': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.webp': 'image/webp',
    '.txt': 'text/plain',
    '.xml': 'application/xml',
    '.map': 'application/json',
};

// ── Lambda Runtime API helpers ─────────────────────────────────────────────────

function httpRequest(options, body) {
    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            const chunks = [];
            res.on('data', c => chunks.push(c));
            res.on('end', () => resolve({
                statusCode: res.statusCode,
                headers: res.headers,
                body: Buffer.concat(chunks).toString()
            }));
        });
        req.on('error', reject);
        if (body) req.write(body);
        req.end();
    });
}

async function getNextInvocation() {
    const [host, port] = RUNTIME_API.split(':');
    const res = await httpRequest({
        host,
        port: port || 80,
        path: '/2018-06-01/runtime/invocation/next',
        method: 'GET',
    });
    const requestId = res.headers['lambda-runtime-aws-request-id'];
    const event = JSON.parse(res.body);
    return { requestId, event };
}

async function sendResponse(requestId, response) {
    const [host, port] = RUNTIME_API.split(':');
    const body = JSON.stringify(response);
    await httpRequest({
        host,
        port: port || 80,
        path: `/2018-06-01/runtime/invocation/${requestId}/response`,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body),
        },
    }, body);
}

async function sendError(requestId, error) {
    const [host, port] = RUNTIME_API.split(':');
    const body = JSON.stringify({
        errorMessage: error.message,
        errorType: error.name || 'Error',
    });
    await httpRequest({
        host,
        port: port || 80,
        path: `/2018-06-01/runtime/invocation/${requestId}/error`,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body),
        },
    }, body);
}

// ── Static File Handler ────────────────────────────────────────────────────────

function serveStatic(urlPath) {
    // Strip query string
    const cleanPath = urlPath.split('?')[0];
    // Decode URL encoding
    let decodedPath;
    try { decodedPath = decodeURIComponent(cleanPath); }
    catch { decodedPath = cleanPath; }

    // Default to index.html
    const requestedFile = (decodedPath === '/' || decodedPath === '') ? '/index.html' : decodedPath;
    const filePath = join(PUBLIC_DIR, requestedFile);

    // Try exact file
    try {
        const content = readFileSync(filePath);
        const ext = extname(filePath).toLowerCase();
        const isAsset = ext !== '.html';
        return {
            statusCode: 200,
            headers: {
                'Content-Type': MIME[ext] || 'application/octet-stream',
                'Cache-Control': isAsset ? 'public, max-age=31536000, immutable' : 'no-cache, no-store, must-revalidate',
            },
            body: content.toString('base64'),
            isBase64Encoded: true,
        };
    } catch {
        // File not found → SPA fallback to index.html
        try {
            const index = readFileSync(join(PUBLIC_DIR, 'index.html'));
            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                },
                body: index.toString('base64'),
                isBase64Encoded: true,
            };
        } catch {
            return {
                statusCode: 500,
                headers: { 'Content-Type': 'text/plain' },
                body: 'index.html not found',
                isBase64Encoded: false,
            };
        }
    }
}

// ── Main Lambda Runtime Loop ───────────────────────────────────────────────────

console.log('Lambda bootstrap starting...');
console.log('Public dir:', PUBLIC_DIR);
console.log('Runtime API:', RUNTIME_API);

async function runLoop() {
    while (true) {
        let requestId;
        try {
            const invocation = await getNextInvocation();
            requestId = invocation.requestId;
            const event = invocation.event;

            const urlPath = event.rawPath || event.path || '/';
            console.log(`[${requestId}] ${event.requestContext?.http?.method || 'GET'} ${urlPath}`);

            const response = serveStatic(urlPath);
            await sendResponse(requestId, response);
        } catch (err) {
            console.error('Handler error:', err);
            if (requestId) {
                await sendError(requestId, err).catch(() => { });
            }
        }
    }
}

runLoop().catch(err => {
    console.error('Fatal error in runtime loop:', err);
    process.exit(1);
});
