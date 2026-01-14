const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');
const mysql = require('mysql2/promise');

function parseEnv(filePath) {
  const out = {};
  const text = fs.readFileSync(filePath, 'utf8');
  for (const line of text.split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const idx = t.indexOf('=');
    if (idx > 0) {
      const k = t.slice(0, idx).trim();
      let v = t.slice(idx + 1).trim();
      if (v.startsWith('"') && v.endsWith('"')) v = v.slice(1, -1);
      out[k] = v;
    }
  }
  return out;
}

async function main() {
  const envPath = path.join(process.cwd(), '.env');
  let cfg = {};
  if (fs.existsSync(envPath)) {
    cfg = parseEnv(envPath);
  }

  const user = cfg.MYSQL_USER || 'user';
  const password = cfg.MYSQL_PASSWORD || 'password';
  const database = cfg.MYSQL_DB || 'voice_chat';
  const port = Number(cfg.MYSQL_PORT || 3306);
  const hosts = [];
  if (cfg.MYSQL_HOST) hosts.push(cfg.MYSQL_HOST);
  hosts.push('localhost', '127.0.0.1');

  const hash = bcrypt.hashSync('admin', 10);

  let conn = null;
  for (const host of hosts) {
    try {
      conn = await mysql.createConnection({ host, port, user, password, database });
      console.log(`Connected to MySQL at ${host}:${port}`);
      break;
    } catch (e) {
      console.error(`Connect failed ${host}:${port} - ${e.code || e.message}`);
    }
  }
  if (!conn) {
    console.error('All connection attempts failed. Check .env (MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DB).');
    process.exit(2);
  }

  try {
    const [tables] = await conn.query("SHOW TABLES LIKE 'users'");
    if (!tables || tables.length === 0) {
      console.error('Table `users` not found. Please run Alembic migrations first.');
      process.exit(3);
    }
    const sql =
      "INSERT INTO users (username,email,hashed_password,full_name,is_active,created_at) VALUES (?,?,?,?,1,NOW()) " +
      "ON DUPLICATE KEY UPDATE email=VALUES(email), full_name=VALUES(full_name), hashed_password=VALUES(hashed_password), is_active=VALUES(is_active)";
    const params = ['admin', 'admin@example.com', hash, 'Admin User'];
    await conn.execute(sql, params);
    console.log('Admin user initialized: username=admin, password=admin');
  } catch (e) {
    console.error('Init admin failed:', e.message);
    process.exit(4);
  } finally {
    if (conn) await conn.end();
  }
}

main().catch((e) => {
  console.error('Unexpected error:', e);
  process.exit(1);
});
