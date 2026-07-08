#!/usr/bin/env node

// Thin wrapper around mcp-remote, pointed at Dali's hosted MCP server.
// Lets `npx dali-mcp` work for stdio-only MCP clients without needing
// Python or a local install — the real server runs at dali.getlulu.dev.
// Set DALI_MCP_URL to point at a self-hosted instance instead.

const { spawn } = require('child_process')
const path = require('path')

const DEFAULT_URL = 'https://dali.getlulu.dev/mcp'
const url = process.env.DALI_MCP_URL || DEFAULT_URL

// Resolve mcp-remote via Node's actual module resolution rather than a
// hardcoded node_modules/.bin path — npx/npm hoist dependencies to varying
// depths, so a fixed relative path breaks under npx (ENOENT) even though
// the package is genuinely installed and resolvable.
let mcpRemoteEntry
try {
  const pkgJsonPath = require.resolve('mcp-remote/package.json')
  const pkg = require(pkgJsonPath)
  mcpRemoteEntry = path.join(path.dirname(pkgJsonPath), pkg.bin['mcp-remote'])
} catch (err) {
  console.error('Could not locate the mcp-remote package:', err.message)
  process.exit(1)
}

const child = spawn(process.execPath, [mcpRemoteEntry, url, ...process.argv.slice(2)], {
  stdio: 'inherit',
})

child.on('error', (err) => {
  console.error('Failed to start mcp-remote:', err.message)
  process.exit(1)
})

child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal)
  else process.exit(code ?? 0)
})
