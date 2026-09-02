/* 通过 PowerPoint COM 逐页导出 PNG 用于视觉检查 */
const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const root = path.join(__dirname, "..");
const pptx = path.join(root, "绿茵慧眼_球员能力评估系统_项目立项答辩.pptx");
const outDir = path.join(__dirname, "render");
fs.mkdirSync(outDir, { recursive: true });

const script = `
$ErrorActionPreference = 'Stop'
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ppt.Presentations.Open('${pptx}', $true, $false, $false)
  $n = $pres.Slides.Count
  for ($i = 1; $i -le $n; $i++) {
    $out = Join-Path '${outDir}' ('slide-' + $i.ToString().PadLeft(2,'0') + '.png')
    $pres.Slides.Item($i).Export($out, 'PNG', 1600, 900)
  }
  Write-Output ('EXPORTED ' + $n + ' slides')
  $pres.Close()
} finally {
  $ppt.Quit()
}
`;

const encoded = Buffer.from(script, "utf16le").toString("base64");
try {
  const out = execFileSync("powershell", ["-NoProfile", "-EncodedCommand", encoded], { encoding: "utf8" });
  console.log(out.trim());
} catch (e) {
  console.error("EXPORT FAILED:", e.message);
  process.exit(1);
}
