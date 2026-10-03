// Wrapper (n64-suite): print brileta trees/boulders as JSON RGBA for Python.
// usage: node dump.mjs '[{"kind":"tree","seed":3,"size":40,"arch":"deciduous"},{"kind":"rock","seed":1,"size":20}]'
import { generateTree } from "./dist/trees.js";
import { generateBoulder } from "./dist/boulders.js";
const reqs = JSON.parse(process.argv[2] || "[]");
const out = reqs.map((r) => {
  const res = r.kind === "rock" ? generateBoulder(r.seed, r.size || 16) : generateTree(r.seed, r.size || 20, r.arch || undefined);
  const c = res.canvas;
  return { w: c.width, h: c.height, arch: res.archetype, data: Buffer.from(c.data).toString("base64") };
});
process.stdout.write(JSON.stringify(out));
