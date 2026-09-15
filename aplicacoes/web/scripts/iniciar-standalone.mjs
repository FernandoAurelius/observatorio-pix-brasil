import { cpSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const app = join(root, ".next", "standalone", "aplicacoes", "web");
const staticTarget = join(app, ".next", "static");

// O pacote standalone não copia ativos estáticos; prepare-os antes de iniciar.
mkdirSync(dirname(staticTarget), { recursive: true });
cpSync(join(root, ".next", "static"), staticTarget, { recursive: true });
if (existsSync(join(root, "public"))) {
  cpSync(join(root, "public"), join(app, "public"), { recursive: true });
}

const server = spawn(process.execPath, [join(app, "server.js")], { stdio: "inherit" });
server.on("exit", code => process.exit(code ?? 1));
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => server.kill(signal));
}
