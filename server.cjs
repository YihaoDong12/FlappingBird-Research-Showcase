const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = fs.realpathSync(__dirname);
const args = process.argv.slice(2);
const option = name => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
};
const port = Number(option('--port') || process.env.PORT || 3013);
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Choose a port from 1 to 65535.');
const prefixOption = option('--base-path') || '';
const basePath = prefixOption ? '/' + prefixOption.replace(/^\/+|\/+$/g, '') : '';
if (basePath && !/^\/[a-zA-Z0-9_-]+$/.test(basePath)) throw new Error('Use a simple base path, such as /FlappingBird-Research-Showcase.');
const mime = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml',
  '.webp': 'image/webp', '.ico': 'image/x-icon', '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.woff2': 'font/woff2', '.pdf': 'application/pdf', '.csv': 'text/csv; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.py': 'text/plain; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
};

function withinRoot(file) {
  const relative = path.relative(root, file);
  return relative !== '..' && !relative.startsWith('..' + path.sep) && !path.isAbsolute(relative);
}

function reject(res, status, message, headers = {}) {
  res.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8', ...headers });
  res.end(message);
}

const server = http.createServer(async (req, res) => {
  res.setHeader('X-Showcase-Server', 'FlappingBird-Research-Showcase');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    reject(res, 405, 'Method not allowed', { Allow: 'GET, HEAD' });
    return;
  }
  let file;
  try {
    let pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (basePath) {
      if (pathname === basePath) { res.writeHead(308, { Location: basePath + '/' }); res.end(); return; }
      if (!pathname.startsWith(basePath + '/')) { reject(res, 404, 'Not found'); return; }
      pathname = pathname.slice(basePath.length);
    }
    if (pathname.includes('\0') || pathname.split(/[\\/]/).some(part => part.startsWith('.'))) {
      reject(res, 403, 'Forbidden');
      return;
    }
    const publicPath = pathname === '/' ? '/index.html' : pathname;
    if (!/^\/(index\.html|style\.css|app\.js|favicon\.svg)$/.test(publicPath)
      && !/^\/(media|research)\/[a-zA-Z0-9_./-]+$/.test(publicPath)) {
      reject(res, 404, 'Not found'); return;
    }
    file = path.resolve(root, '.' + publicPath);
    if (!withinRoot(file)) { reject(res, 403, 'Forbidden'); return; }
  } catch { reject(res, 400, 'Bad request'); return; }

  try {
    let stat = await fs.promises.stat(file);
    if (stat.isDirectory()) {
      file = path.join(file, 'index.html');
      stat = await fs.promises.stat(file);
    }
    file = await fs.promises.realpath(file);
    if (!withinRoot(file)) { reject(res, 403, 'Forbidden'); return; }
    if (!stat.isFile() || ['.cjs', '.ps1', '.cmd', '.log'].includes(path.extname(file))) {
      reject(res, 404, 'Not found'); return;
    }
    const extension = path.extname(file).toLowerCase();
    const headers = {
      'Content-Type': mime[extension] || 'application/octet-stream',
      'Accept-Ranges': 'bytes', 'Last-Modified': stat.mtime.toUTCString(),
      'Cache-Control': ['.html', '.css', '.js'].includes(extension) ? 'no-cache' : 'private, max-age=3600',
    };
    let start = 0;
    let end = stat.size - 1;
    const range = req.headers.range;
    if (range) {
      const match = /^bytes=(\d*)-(\d*)$/.exec(range);
      if (!match || (!match[1] && !match[2]) || stat.size === 0) {
        reject(res, 416, 'Range not satisfiable', { 'Content-Range': `bytes */${stat.size}` }); return;
      }
      if (!match[1]) start = Math.max(0, stat.size - Number(match[2]));
      else {
        start = Number(match[1]);
        if (match[2]) end = Math.min(Number(match[2]), end);
      }
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || start > end) {
        reject(res, 416, 'Range not satisfiable', { 'Content-Range': `bytes */${stat.size}` }); return;
      }
      headers['Content-Range'] = `bytes ${start}-${end}/${stat.size}`;
    }
    headers['Content-Length'] = Math.max(0, end - start + 1);
    res.writeHead(range ? 206 : 200, headers);
    if (req.method === 'HEAD' || stat.size === 0) { res.end(); return; }
    const stream = fs.createReadStream(file, { start, end });
    stream.on('error', error => res.destroy(error));
    res.on('close', () => stream.destroy());
    stream.pipe(res);
  } catch (error) {
    if (!res.headersSent) reject(res, error.code === 'EACCES' ? 403 : 404, 'Not found');
    else res.destroy(error);
  }
});
server.on('error', error => {
  console.error(error.code === 'EADDRINUSE' ? `Port ${port} is already in use. Choose another port with --port.` : error);
  process.exitCode = 1;
});
server.listen(port, '127.0.0.1', () => console.log(`Flapping Bird Research: http://127.0.0.1:${port}${basePath}/ (PID ${process.pid})`));
