import {defineConfig,devices} from "@playwright/test";
import path from "node:path";
const root=path.resolve(__dirname,"../..");
const python=process.platform==="win32"
 ? path.join(root,".venv","Scripts","python.exe")
 : "python";
export default defineConfig({
 testDir:"./e2e",timeout:60000,expect:{timeout:15000},fullyParallel:false,workers:1,
 reporter:[["list"],["html",{open:"never"}]],
 use:{baseURL:"http://127.0.0.1:3000",trace:"retain-on-failure",screenshot:"only-on-failure"},
 projects:[{name:"chromium",use:{...devices["Desktop Chrome"],viewport:{width:1440,height:1100}}}],
 webServer:[
  {command:`"${python}" -m uvicorn observatorio_api.principal:aplicacao --host 127.0.0.1 --port 8000`,cwd:root,url:"http://127.0.0.1:8000/api/saude",reuseExistingServer:false,timeout:30000},
  {command:"npm run start",url:"http://127.0.0.1:3000",reuseExistingServer:false,timeout:60000}
 ]
});
