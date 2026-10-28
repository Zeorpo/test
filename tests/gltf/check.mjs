// Usage: node check.mjs FIXTURE.glb
// Checks gltfpack options quoted in skills/art-vfx-realtime and validates every output.
import { execFileSync } from "node:child_process";
import { readFileSync, statSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import validator from "gltf-validator";

const fixture = process.argv[2];
const dir = mkdtempSync(join(tmpdir(), "gltfpack-"));
const results = [];
const check = (id, text, ok, detail = "") => results.push({ id, text, ok, detail });

async function info(file) {
  const r = await validator.validateBytes(new Uint8Array(readFileSync(file)));
  return {
    errors: r.issues.numErrors, warnings: r.issues.numWarnings,
    ext: r.info.extensionsUsed ?? [], tris: r.info.totalTriangleCount,
    bytes: statSync(file).size,
  };
}
function pack(name, args) {
  const out = join(dir, `${name}.glb`);
  execFileSync("npx", ["gltfpack", "-i", fixture, "-o", out, ...args], { stdio: "pipe" });
  return out;
}

const base = await info(fixture);
check("PACK-0", "Blender export of the fixture validates with 0 errors", base.errors === 0, JSON.stringify(base));

const si = await info(pack("si", ["-si", "0.25"]));
check("PACK-1", "-si 0.25 reduces triangles to 25% (+-2%), valid, quantization extension on by default",
  si.errors === 0 && Math.abs(si.tris / base.tris - 0.25) < 0.02 && si.ext.includes("KHR_mesh_quantization"),
  JSON.stringify(si));

const cc = await info(pack("cc", ["-si", "0.25", "-cc"]));
check("PACK-2", "-cc adds EXT_meshopt_compression, is valid and smaller than without it",
  cc.errors === 0 && cc.ext.includes("EXT_meshopt_compression") && cc.bytes < si.bytes,
  JSON.stringify(cc));

check("PACK-3", "Optimized file is under 20% of the original size",
  cc.bytes < 0.2 * base.bytes, `${cc.bytes} vs ${base.bytes}`);

let failed = 0;
for (const r of results) {
  console.log(`${r.ok ? "PASS" : "FAIL"} ${r.id.padEnd(7)} ${r.text}${r.ok ? "" : "\n         -> " + r.detail}`);
  failed += !r.ok;
}
console.log(`\n${results.length - failed}/${results.length} passed`);
process.exit(failed);
