# Security Remediation Guide -- SecureShop E-Commerce Platform

**Report ID**: SC-2025-00847
**Date**: 2025-04-05
**Prepared by**: Security Company -- WebSec, AppSec, InfraSec, IncidentResp

This guide provides step-by-step remediation instructions for each of the 23 findings from the security audit. Code examples are provided where applicable.

---

## Table of Contents

- [Phase 1: Critical (0-72 hours)](#phase-1-critical-0-72-hours)
  - [SC-001: SQL Injection in Search Endpoint](#sc-001-sql-injection-in-search-endpoint)
  - [SC-002: JWT Token Forgery](#sc-002-jwt-token-forgery)
  - [SC-003: Sensitive Data in Error Responses](#sc-003-sensitive-data-in-error-responses)
  - [SC-004: SSRF via Image Upload](#sc-004-ssrf-via-image-upload)
- [Phase 2: High (1-2 weeks)](#phase-2-high-1-2-weeks)
  - [SC-005: IDOR on Order API](#sc-005-idor-on-order-api)
  - [SC-006: Reflected XSS](#sc-006-reflected-xss)
  - [SC-007: Weak Session Management](#sc-007-weak-session-management)
  - [SC-008: TLS 1.0/1.1 Enabled](#sc-008-tls-1011-enabled)
  - [SC-009: No Rate Limiting](#sc-009-no-rate-limiting)
  - [SC-010: Open Redirect](#sc-010-open-redirect)
- [Phase 3: Medium (1-4 weeks)](#phase-3-medium-1-4-weeks)
  - [SC-011: Missing CSP](#sc-011-missing-content-security-policy)
  - [SC-012: Clickjacking](#sc-012-clickjacking)
  - [SC-013: Directory Listing](#sc-013-directory-listing)
  - [SC-014: CORS Wildcard](#sc-014-cors-wildcard)
  - [SC-015: Stored XSS](#sc-015-stored-xss)
  - [SC-016: Tech Stack Disclosure](#sc-016-tech-stack-disclosure)
  - [SC-017: CSRF Missing](#sc-017-csrf-token-missing)
  - [SC-018: MD5 Password Hash](#sc-018-md5-password-hash)
- [Phase 4: Low (1-3 months)](#phase-4-low-1-3-months)
  - [SC-019: Missing X-Content-Type](#sc-019-missing-x-content-type-options)
  - [SC-020: TRACE Method](#sc-020-http-trace-method)
  - [SC-021: robots.txt](#sc-021-robotstxt-info-leak)
  - [SC-022: Suspicious Logs](#sc-022-suspicious-log-patterns)
  - [SC-023: Vulnerable Dependencies](#sc-023-vulnerable-dependencies)
- [Hardened Nginx Configuration](#hardened-nginx-configuration)

---

## Phase 1: Critical (0-72 hours)

### SC-001: SQL Injection in Search Endpoint

**Severity**: Critical | **CVSS**: 9.8

Immediately stop string concatenation in SQL queries. Use parameterized queries.

#### Node.js / Express (knex.js example):
```javascript
// VULNERABLE -- DO NOT USE
router.get('/search', async (req, res) => {
  const results = await db.raw(`SELECT * FROM products WHERE name LIKE '%${req.query.q}%'`);
  res.json(results);
});

// SECURE -- Use parameterized query
router.get('/search', async (req, res) => {
  const { q } = req.query;
  const results = await db('products')
    .where('name', 'like', `%${q}%`)
    .select('id', 'name', 'price', 'description');
  res.json(results);
});
```

#### Python / Django example:
```python
# VULNERABLE -- DO NOT USE
cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")

# SECURE -- Use parameterized query
cursor.execute("SELECT * FROM products WHERE name LIKE %s", [f'%{query}%'])
```

#### Python / SQLAlchemy:
```python
# SECURE
from sqlalchemy import text
query = text("SELECT * FROM products WHERE name LIKE :search")
results = db.execute(query, {"search": f"%{user_input}%"})
```

**Also apply to**: `/api/v1/products`, `/api/v1/reviews`, `/api/v1/comments`, and ALL endpoints accepting user input.

---

### SC-002: JWT Token Forgery

**Severity**: Critical | **CVSS**: 9.1

#### Step 1: Rotate the JWT secret immediately
```bash
# Generate a new secure secret (32-byte random)
openssl rand -base64 48
```

#### Step 2: Update JWT configuration
```javascript
// config/jwt.js
const crypto = require('crypto');

module.exports = {
  // Store in environment variable or secrets vault -- NEVER hardcode
  secret: process.env.JWT_SECRET,  // Must be >= 256 bits
  algorithm: 'HS256',
  expiresIn: process.env.NODE_ENV === 'production' ? '24h' : '7d',
  issuer: 'secureshop.com.br',
  audience: 'secureshop-api',
  // Rotate keys using JWKs in production
  keyRotationDays: 90,
};

// Force immediate re-authentication
const blacklist = new Set();  // Invalidate all existing tokens
// In production, use Redis: redis.set(`token_blacklist:${tokenId}`, '1', 'EX', oldExpiry)
```

#### Step 3: Invalidating all existing tokens
```javascript
// Middleware to check token blacklisted status
const verifyToken = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  const payload = jwt.verify(token, process.env.JWT_SECRET);

  // Check if token was issued before rotation
  if (payload.iat < KEY_ROTATION_TIMESTAMP) {
    return res.status(401).json({ error: 'Token expired due to key rotation' });
  }

  req.user = payload;
  next();
};
```

#### Production recommendation:
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Implement JWKs (JSON Web Keys) for rotation without downtime
- Add `iat` (issued at) claim and verify it

---

### SC-003: Sensitive Data in Error Responses

**Severity**: Critical | **CVSS**: 8.6

Replace verbose error responses with generic messages. Log details server-side.

```javascript
// error-handler.js
const errorHandler = (err, req, res, next) => {
  // Always log full error server-side
  console.error('[ERROR]', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    ip: req.ip,
    timestamp: new Date().toISOString()
  });

  // Generic response for client
  const response = {
    error: 'An internal error occurred',
    code: 'INTERNAL_ERROR',
    // Only expose trace in development
    ...(process.env.NODE_ENV === 'development' && { details: err.message })
  };

  const statusCode = err.statusCode || 500;
  res.status(statusCode).json(response);
};
```

#### Also: Remove secrets from error handling middleware
```javascript
// Remove ALL environment variable references from error responses
// Never return: req.app.get('db_url'), process.env.STRIPE_KEY, etc.
```

#### Nginx level (custom error pages):
```nginx
error_page 500 502 503 504 /50x.html;
location = /50x.html {
    internal;
    root /var/www/errors;
}
```

---

### SC-004: SSRF via Image Upload

**Severity**: Critical | **CVSS**: 8.2

Block internal IP ranges and cloud metadata endpoints.

```javascript
const http = require('http');
const https = require('https');
const { URL } = require('url');

const BLOCKED_RANGES = [
    '127.0.0.0/8',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    '169.254.169.254/32',  // AWS/GCP/Azure metadata
    '0.0.0.0/8',
    '::1/128',
];

function isBlockedIP(hostname) {
    // Resolve hostname and check against blocked ranges
    const { isIP } = require('net');
    const ip = require('dns').lookupSync(hostname).address;
    const ipnum = require('net').isIPv4(ip)
        ? ip.split('.').reduce((a, o) => (a << 8) + parseInt(o), 0)
        : null;
    // Implement range check...
    return false; // Replace with actual check
}

function validateImageUrl(urlString) {
    const url = new URL(urlString);
    const allowedProtocols = ['https:'];
    if (!allowedProtocols.includes(url.protocol)) {
        throw new Error('Only HTTPS URLs are allowed');
    }
    if (isBlockedIP(url.hostname)) {
        throw new Error('Internal addresses are not allowed');
    }
    const blockedDomains = ['metadata.google.internal', '169.254.169.254'];
    if (blockedDomains.includes(url.hostname)) {
        throw new Error('Cloud metadata endpoints are not allowed');
    }
    return true;
}

// Usage in upload handler
router.post('/products/upload-image', async (req, res) => {
    try {
        validateImageUrl(req.body.image_url);
        // Proceed with download
    } catch (err) {
        res.status(400).json({ error: 'Invalid image URL' });
    }
});
```

---

## Phase 2: High (1-2 weeks)

### SC-005: IDOR on Order API

**Severity**: High | **CVSS**: 7.5

```javascript
// middleware/authorize-resource.js
const authorizeOrderAccess = async (req, res, next) => {
    const order = await db('orders')
        .where({ id: req.params.id })
        .first();

    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }

    if (order.user_id !== req.user.id && req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Access denied' });
    }

    req.order = order;  // Attach for downstream middleware
    next();
};

// Apply to route
router.get('/orders/:id', authMiddleware, authorizeOrderAccess, getOrder);
```

---

### SC-006: Reflected XSS

**Severity**: High | **CVSS**: 7.4

```javascript
// Template engine (use auto-escaping)
const ejs = require('ejs');
// In config: { escape: require('lodash/escape') }

// OR use HTML entity encoding
function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// In controller
router.get('/search', (req, res) => {
    const q = escapeHtml(req.query.q || '');
    res.render('search', { query: q, results: [] });
});
```

```html
<!-- search.ejs -- use escaped output -->
<h1>Search results for: <%= query %></h1>
<!-- NOT: <h1>Search results for: <%= - query %></h1> -->
```

---

### SC-007: Weak Session Management

**Severity**: High | **CVSS**: 7.2

```javascript
// Express session configuration
const session = require('express-session');
const RedisStore = require('connect-redis').default;

app.use(session({
    store: new RedisStore({ client: redisClient }),
    secret: process.env.SESSION_SECRET,
    name: '__session',
    resave: false,
    saveUninitialized: false,
    cookie: {
        httpOnly: true,        // Prevent JS access
        secure: true,          // HTTPS only
        sameSite: 'strict',    // CSRF protection
        maxAge: 24 * 60 * 60 * 1000,  // 24 hours
        // Absolute expiration handling:
        // Store session creation time in Redis, validate on each request
    },
    rolling: true,  // Refresh expiry on activity
}));
```

For JWT sessions, add expiration:
```javascript
const token = jwt.sign(payload, secret, {
    expiresIn: '24h',  // Idle token expiry
    algorithm: 'HS256',
});
```

---

### SC-008: TLS 1.0/1.1 Enabled

**Severity**: High | **CVSS**: 7.0

See the [Hardened Nginx Configuration](#hardened-nginx-configuration) section below. Key directives:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
ssl_prefer_server_ciphers on;
```

---

### SC-009: No Rate Limiting

**Severity**: High | **CVSS**: 6.8

#### Nginx level:
```nginx
http {
    # Global rate limit
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        # For login endpoint
        location /api/v1/auth/login {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://backend;
        }

        # For general API
        location /api/v1/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
        }

        # Return 429 with JSON body
        limit_req_status 429;
    }
}
```

#### Express middleware (express-rate-limit):
```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
    windowMs: 60 * 1000,       // 1 minute
    max: 5,                     // 5 attempts per minute per IP
    message: {
        error: 'Too many login attempts',
        retryAfter: '60 seconds'
    },
    standardHeaders: true,      // RateLimit-* headers
    legacyHeaders: false,
});

const apiLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
});

app.use('/api/v1/auth/login', loginLimiter);
app.use('/api/v1/', apiLimiter);
```

---

### SC-010: Open Redirect

**Severity**: High | **CVSS**: 6.5

```javascript
const { URL } = require('url');

const ALLOWED_DOMAINS = ['secureshop.com.br', 'www.secureshop.com.br'];

function validateRedirect(urlString) {
    if (!urlString) return '/';
    try {
        const url = new URL(urlString, 'https://secureshop.com.br');
        if (!ALLOWED_DOMAINS.includes(url.hostname)) {
            return '/';  // Redirect to home instead
        }
        return url.pathname + url.search;
    } catch {
        return '/';
    }
}

router.get('/auth/logout', (req, res) => {
    req.session.destroy();
    const redirectUrl = validateRedirect(req.query.next);
    res.redirect(redirectUrl);
});
```

---

## Phase 3: Medium (1-4 weeks)

### SC-011: Missing Content-Security-Policy

```nginx
# In Nginx config
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.stripe.com; frame-ancestors 'none';" always;
```

Or via Express/helmet:
```javascript
const helmet = require('helmet');

app.use(helmet.contentSecurityPolicy({
    directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "https://js.stripe.com"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "https://api.stripe.com"],
        frameAncestors: ["'none'"],
    }
}));
```

### SC-012: Clickjacking

```nginx
# Already covered by CSP frame-ancestors 'none' above
# Additional defense:
add_header X-Frame-Options "DENY" always;
```

### SC-013: Directory Listing

```nginx
# Remove this if present:
# autoindex on;

# Add this explicitly:
location /uploads/ {
    autoindex off;
    # Only serve specific file types
    location ~* \.(jpg|jpeg|png|gif|webp|pdf)$ {
        # serve files
    }
    location ~* / {
        return 403;  # Deny all others
    }
}

# Block sensitive paths entirely
location ~* /(\.git|\.env|config|backups|sql|temp|tmp|logs)/ {
    deny all;
    return 403;
}
```

### SC-014: CORS Wildcard

```javascript
const cors = require('cors');

const corsOptions = {
    origin: function (origin, callback) {
        const allowed = [
            'https://secureshop.com.br',
            'https://www.secureshop.com.br',
            'https://admin.secureshop.com.br',
        ];
        if (!origin || allowed.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    maxAge: 86400,
};

app.use(cors(corsOptions));
```

### SC-015: Stored XSS

```javascript
// Sanitize on input
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

router.post('/reviews', async (req, res) => {
    const sanitized = DOMPurify.sanitize(req.body.text, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
        ALLOWED_ATTR: ['href'],
    });

    const review = await db('reviews').insert({
        text: sanitized,
        // ...
    });
});
```

### SC-016: Tech Stack Disclosure

```nginx
# Hide nginx version
server_tokens off;

# Remove headers
proxy_hide_header X-Powered-By;
proxy_hide_header Server;
more_clear_headers 'Server' 'X-Powered-By' 'X-AspNet-Version' 'X-Runtime';

# In Express, add early in middleware chain:
app.disable('x-powered-by');
```

### SC-017: CSRF Token Missing

```javascript
const csrf = require('csurf');

// For cookie-based auth (not JWT):
const csrfProtection = csrf({
    cookie: {
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
    },
});

app.use('/api/v1/account/*', csrfProtection);

// Frontend: include token in headers
// <input type="hidden" name="_csrf" value="{{ csrfToken }}">
// Or in meta tag and fetch header:
// fetch('/api/v1/account/address', {
//   headers: { 'X-CSRF-Token': document.querySelector('meta[name=csrf-token]').content }
// })
```

### SC-018: MD5 Password Hash

**Step 1**: Switch to bcrypt for all new passwords.
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

async function hashPassword(plainText) {
    return await bcrypt.hash(plainText, SALT_ROUNDS);
}

async function verifyPassword(plainText, hashedPassword) {
    // Support both old MD5 and new bcrypt during migration
    if (hashedPassword.startsWith('$2')) {
        return await bcrypt.compare(plainText, hashedPassword);
    } else {
        // Old MD5 -- still allow login, but rehash immediately
        const crypto = require('crypto');
        const md5Hash = crypto.createHash('md5').update(plainText).digest('hex');
        if (md5Hash === hashedPassword) {
            // Rehash with bcrypt and update database
            const newHash = await bcrypt.hash(plainText, SALT_ROUNDS);
            await db('users').where({ password: hashedPassword }).update({ password: newHash });
            return true;
        }
        return false;
    }
}
```

**Step 2**: Force password reset campaign via email notification.
**Step 3**: After migration window, remove MD5 fallback code.

---

## Phase 4: Low (1-3 months)

### SC-019: Missing X-Content-Type-Options

```nginx
add_header X-Content-Type-Options "nosniff" always;
```

```javascript
app.use(helmet.noSniff());
```

### SC-020: HTTP TRACE Method

```nginx
# In Nginx location block:
if ($request_method = TRACE) {
    return 405;
}

# Or in Apache:
# TraceEnable Off
```

### SC-021: robots.txt Info Leak

```
# Minimal robots.txt -- do not reveal paths
User-agent: *
Disallow:
Sitemap: https://www.secureshop.com.br/sitemap.xml
```

Security through obscurity is insufficient. Use proper access controls for sensitive paths.

### SC-022: Suspicious Log Patterns

```javascript
// Implement automated alerting
const failedLogins = new Map();

app.use('/api/v1/auth/login', (req, res, next) => {
    const ip = req.ip;
    const key = ip;

    if (!failedLogins.has(key)) {
        failedLogins.set(key, { count: 0, first: Date.now() });
    }

    const record = failedLogins.get(key);
    record.count++;

    // Alert if > 50 failed logins in 10 minutes
    if (record.count > 50 && (Date.now() - record.first) < 600000) {
        console.warn(`[ALERT] Possible brute force from ${ip}: ${record.count} attempts`);
        // Send to monitoring (e.g., Slack, PagerDuty, email)
        sendAlert('brute_force', { ip, count: record.count });
    }

    // Reset after 10 minutes
    if (Date.now() - record.first > 600000) {
        record.count = 0;
        record.first = Date.now();
    }

    next();
});
```

For data exfiltration detection:
```javascript
// Monitor response sizes
app.use((req, res, next) => {
    const originalWrite = res.write.bind(res);
    const originalEnd = res.end.bind(res);
    let totalBytes = 0;

    res.write = function(chunk) {
        if (chunk) totalBytes += chunk.length;
        return originalWrite(chunk);
    };

    res.end = function(chunk) {
        if (chunk) totalBytes += chunk.length;

        // Alert on unusually large responses
        if (totalBytes > 5 * 1024 * 1024) {  // >5MB
            console.warn(`[ALERT] Large response: ${totalBytes} bytes for ${req.path} from ${req.ip}`);
        }

        return originalEnd(chunk);
    };

    next();
});
```

### SC-023: Vulnerable Dependencies

```bash
# Check for vulnerabilities
npm audit

# Auto-fix where possible
npm audit fix

# Force fix (may introduce breaking changes)
npm audit fix --force

# Update specific packages
npm install lodash@latest express@latest axios@latest jsonwebtoken@latest

# Add helmet
npm install helmet

# Add audit to CI/CD pipeline
# In .github/workflows/ci.yml:
# - name: Audit dependencies
#   run: npm audit --audit-level=moderate
```

```javascript
// In app.js, add early
const helmet = require('helmet');
app.use(helmet());  // Sets all security headers automatically
```

---

## Hardened Nginx Configuration

See the companion file `nginx_secure.conf` for a complete hardened configuration.

---

## Verification

After applying fixes, re-run the scanners:

```bash
# From the project root
bash scripts/run_audit.sh --target https://shop.secureshop.com.br
```

All findings should show reduced severity or be marked as resolved.
