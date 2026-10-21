# OWASP Checks Catalog

Mapped to the OWASP Top 10:2025. Search patterns are starting points, not verdicts. Adapt them to the languages present, and always read the code around a hit.

Run searches from the target root with the excluded paths left out, for example:

```bash
grep -rnE '<pattern>' . --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.venv --exclude-dir=dist --exclude-dir=build --exclude-dir=.git --exclude='*.min.js' --exclude='*.lock' --exclude='package-lock.json' --exclude='*-CHECK.md'
```

Match method calls without their receiver (`\.send\(` rather than `res.send(`), so chained calls like `res.status(500).send(...)` are found.

## O0 - Application surface inventory

Find what the application exposes and what it can reach.

- Languages and frameworks: `package.json`, `requirements*.txt`, `pyproject.toml`, `Gemfile`, `go.mod`, `pom.xml`, `build.gradle`, `composer.json`, `*.csproj`, `Cargo.toml`
- Entry points: `app.get(`, `router.`, `@app.route`, `@router.`, `@GetMapping`, `@RequestMapping`, `path(`, `urlpatterns`, `Route::`, `http.HandleFunc`, `get '`, `resources :`, queue consumers, cron jobs, CLI commands
- Auth: `passport`, `jwt`, `jsonwebtoken`, `session`, `login`, `@login_required`, `authenticate`, `Devise`, `spring-security`, `next-auth`, middleware registration
- Data stores and integrations: DB drivers and ORMs, `redis`, `s3`, `smtp`, outbound HTTP clients
- Config: `.env*`, `settings*.py`, `config/`, `application*.yml`, `appsettings*.json`, `Dockerfile`, `docker-compose*.yml`, IaC files

Record each component, its location, and whether it is reachable without authentication.

## O1 - Broken Access Control (A01:2025)

- **Missing authorization:** routes that read or change data with no auth middleware/decorator, or with authentication but no role or ownership check. Compare route lists against where auth is applied.
- **IDOR/BOLA:** object IDs from `params`, `query`, `body`, or the path (`req.params.id`, `request.args['id']`, `@PathVariable`) passed to a lookup without scoping to the current user/tenant (`WHERE id = ?` without `AND owner_id = ?`, `findById(id)` with no ownership check).
- **Client-trusted roles:** `isAdmin`, `role`, `user_id`, `tenant_id` read from the request body, query, or an unsigned cookie.
- **Path traversal:** `open(`, `fs.readFile`, `sendFile`, `File(`, `os.path.join`, `path.join` with request data and no normalization plus root check (`realpath`/`resolve` then `startsWith(root)`).
- **SSRF:** `requests.get(`, `urllib`, `fetch(`, `axios`, `http.Get(`, `RestTemplate`, `HttpClient`, `curl_exec` with a request-supplied URL and no host allowlist (internal IPs, `169.254.169.254`, `localhost`).
- **CORS:** `Access-Control-Allow-Origin: *` or the request `Origin` reflected, together with `Allow-Credentials: true`; `cors({ origin: true, credentials: true })`.
- **CSRF:** cookie-authenticated state-changing routes (POST, PUT, PATCH, DELETE, or a GET that changes data) with CSRF protection disabled or absent (`csrf_exempt`, `csrf: false`, `skip_forgery_protection`, `.csrf().disable()`) and no `SameSite=Strict/Lax` session cookie. If such routes exist but the cookie is set outside the repo, report `Needs verification`. If no cookie-authenticated route changes state, CSRF does not apply; say so in the O1 notes.
- **Open redirect:** `redirect(req.query.next)`, `res.redirect(url)` with unvalidated request data.

Fail when a route lets a user act on data or functions beyond their role, or a request value controls a file path, outbound URL, or redirect without an allowlist.

## O2 - Security Misconfiguration (A02:2025)

- Debug in production config: `DEBUG = True`, `debug: true`, `app.run(debug=True)`, `NODE_ENV` not production in prod files, Spring `actuator` endpoints exposed, `display_errors = On`.
- Stack traces or internal errors returned to clients (`err\.stack`, `\.send\(err`, `traceback` in responses), whether set by config or written in handler code.
- Default or sample credentials in config (`admin/admin`, `root` with empty password, `password: password`).
- Missing security headers when the app serves HTML: no `helmet`, `SecurityMiddleware`, `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`.
- Cookies without `Secure`, `HttpOnly`, `SameSite` (`cookie: { secure: false }`, `SESSION_COOKIE_SECURE = False`).
- `ALLOWED_HOSTS = ['*']`, directory listing enabled, admin panels on default paths without extra protection.
- XML parsers with external entities enabled (XXE): `XMLParser(resolve_entities=True)`, `DocumentBuilderFactory` without `disallow-doctype-decl`, `libxml_disable_entity_loader(false)`.
- Containers running as root with no `USER`, world-open ports or buckets in IaC (`0.0.0.0/0`, `public-read`).

Fail when a production-facing config enables any of the above. Settings clearly scoped to development or tests are Info.

## O3 - Software Supply Chain Failures (A03:2025)

- No lockfile for an ecosystem in use (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `Gemfile.lock`, `go.sum`, `composer.lock`, `Cargo.lock`).
- Unpinned or wildcard versions: `"*"`, `"latest"`, `>=` with no upper bound, git dependencies on a branch instead of a commit.
- Dependencies from untrusted sources: `http://` registries, raw GitHub URLs, tarball URLs.
- Install hooks in the project's own package (`preinstall`, `postinstall`) that download and run code.
- CI: third-party actions (any owner other than `actions/` and `github/`) pinned to a tag or branch instead of a commit SHA (`uses: org/action@v1`), `curl ... | sh` in pipelines or Dockerfiles, `pull_request_target` workflows that check out PR code.
- Known-vulnerable versions: only report one if you can name the package, version, and CVE; otherwise list "no SCA scan was run" under Limitations.

Fail on any of the above in production dependencies or release pipelines.

## O4 - Cryptographic Failures (A04:2025)

- Password storage: plain text, reversible encryption, or `md5`, `sha1`, `sha256` (even salted) instead of `bcrypt`, `scrypt`, `argon2`, or `PBKDF2` with a high iteration count.
- Weak algorithms and modes: `DES`, `3DES`, `RC4`, `ECB`, `AES/ECB`, `Cipher.getInstance("AES")` (defaults to ECB), static or zero IVs, hardcoded encryption keys.
- Insecure randomness for security values (tokens, reset links, session IDs, OTPs): `Math.random`, `random.random`, `rand()`, `java.util.Random`, `mt_rand` instead of `crypto.randomBytes`, `secrets`, `SecureRandom`, `random_bytes`.
- TLS verification disabled: `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, trust-all `TrustManager`.
- Sensitive data sent over `http://` to non-local hosts.
- Hardcoded secrets in tracked files: `-----BEGIN .*PRIVATE KEY-----`, `AKIA[0-9A-Z]{16}`, `ghp_`, `xox[bp]-`, `sk_live_`, `sk-`, `password\s*=\s*['"]`, connection strings with credentials. Check `git ls-files` to confirm it is tracked, and judge whether it is real or a placeholder.

Fail when sensitive data is protected with a weak or broken mechanism, or a real secret is committed.

## O5 - Injection (A05:2025)

Untrusted data reaching an interpreter without parameterization or encoding.

- **SQL:** string-built queries: `execute(f"`, `execute("..." + `, `% (` in queries, `` `SELECT ... ${ ``, `.raw(`, `knex.raw(`, `sequelize.query(` with interpolation, `createQuery("..." +`, `Statement.execute`, `text(f"`.
- **NoSQL:** request objects passed directly as filters (`find(req.body)`, `findOne({ user: req.body.user })` without type checks), `$where`.
- **OS command:** `os.system(`, `subprocess.*(..., shell=True)`, `exec(`, `execSync(`, `child_process.exec(`, `Runtime.exec(`, `system(`, backticks, `popen(` with request data.
- **Code eval:** `eval(`, `new Function(`, `vm.runIn`, `exec(` (Python), `setTimeout("...")` with strings.
- **Template injection (SSTI):** `render_template_string(` with user data, `Template(user_input)`, `ejs.render(user_input)`.
- **XSS:** `innerHTML =`, `outerHTML`, `document.write(`, `dangerouslySetInnerHTML`, `v-html`, `|safe`, `{% autoescape false %}`, `<%-`, `{!! !!}`, `html_safe`, `raw(`, `Markup(`, `res.send(` of unescaped request data with HTML content type.
- **LDAP / XPath / header injection:** filters or expressions built by concatenation; request data written into response headers (CRLF).

Fail when a request-derived value reaches one of these sinks with no parameterization, allowlist, or context-appropriate encoding. Bound parameters (`?`, `$1`, `:name`) and ORM query builders are safe.

## O6 - Insecure Design (A06:2025)

- Business values trusted from the client: price, total, discount, quantity, role, or approval status taken from the request instead of computed server-side.
- Security enforced only in the frontend: hidden buttons, client-side validation, route guards with no server check.
- No rate limiting or anti-automation on expensive or sensitive flows: signup, login, password reset, OTP, coupon redemption, file upload, search.
- Unrestricted file upload: no type allowlist, no size limit, files stored under the web root or served with the uploaded name and content type.
- Multi-step flows that can be skipped (e.g. payment confirmation reachable without the payment step), race conditions on balances or one-time actions without locking or transactions.
- Mass assignment: whole request bodies bound to models (`User(**request.json)`, `Model.create(req.body)`, `update(params)` without permitted fields, `@ModelAttribute` on entities with role fields).

Fail when the design lets a user bypass a business rule that the server does not enforce.

## O7 - Authentication Failures (A07:2025)

- JWT: `algorithms` not fixed, `alg: none` accepted, `jwt.decode(` without verification (`verify=False`, `options={"verify_signature": False}`), weak or hardcoded signing secrets, no expiry.
- Sessions: session ID not regenerated after login (fixation), no logout invalidation, very long or no session expiry, tokens in URLs.
- Credentials: no minimum password policy, no protection against brute force (see O6 rate limits), default or hardcoded users, user enumeration through different errors for "unknown user" vs "wrong password".
- Password reset: predictable tokens, tokens that never expire or are reusable, reset links built from the `Host` header.
- Comparisons of secrets or tokens with `==` instead of a constant-time compare (`hmac.compare_digest`, `crypto.timingSafeEqual`).
- MFA bypass: second factor checked only on the client or skippable by calling the next endpoint.

Fail when an attacker can log in as someone else, keep access after logout, or guess credentials without limits.

## O8 - Software or Data Integrity Failures (A08:2025)

- Insecure deserialization of untrusted data: `pickle.loads`, `yaml.load(` without `SafeLoader`, `marshal.loads`, `ObjectInputStream.readObject`, `BinaryFormatter`, PHP `unserialize(`, `node-serialize`, Java `XMLDecoder`.
- Unsigned or unverified data trusted for decisions: cookies or client tokens holding roles without a signature, webhooks accepted without verifying the provider signature.
- Auto-update or plugin loading from URLs without signature or checksum checks; scripts loaded from CDNs without `integrity=` (SRI).
- Prototype pollution: deep merge of request JSON into objects (`_.merge(obj, req.body)`, custom recursive merge without `__proto__` filtering).

Fail when untrusted data is deserialized into objects or trusted without an integrity check.

## O9 - Security Logging and Alerting Failures (A09:2025)

- Missing logs for security events: login success/failure, password change, permission change, access denied, admin actions.
- Sensitive data in logs: passwords, tokens, session IDs, full card numbers, request bodies of auth endpoints (`logger.info(req.body)`, `console.log(password)`).
- Log injection: raw request data written to logs without stripping newlines.
- No error monitoring or alerting hook (e.g. Sentry, OpenTelemetry, a log shipper) for production; only judge this from what the repo shows and note it under Limitations if unknown.

Fail when sensitive values are logged, or security-relevant actions leave no trace.

## O10 - Mishandling of Exceptional Conditions (A10:2025)

- Fail open: a `catch`/`except` around an auth, permission, payment, or validation check that returns success, `next()`, `True`, or continues (`except: return True`, `catch (e) { next() }`).
- Swallowed errors: empty `catch {}`, `except: pass`, `_ = err` in Go around security or data-integrity operations.
- Error details leaked to clients: exception messages, SQL errors, stack traces, or internal paths in responses (overlaps O2; report once with both IDs).
- Missing cleanup: no transaction rollback on error, partial writes left behind, resources or locks not released (`finally`, `defer`, `with`).
- Unhandled async errors in servers (`unhandledRejection` ignored, promises without `catch` in request handlers, streams such as `createReadStream` or `pipe(` with no `.on('error'`) that crash the process or leave requests hanging (denial of service).
- Missing limits on input size, recursion, or regex complexity (ReDoS: nested quantifiers like `(a+)+` applied to request data).

Fail when an error path weakens a security decision, leaks internals, or leaves data inconsistent.
