"use strict";

// Read a copied Chromium local-storage LevelDB without modifying the live DB.
// Inputs are deliberately explicit so this helper is not tied to one Codex install.
const { ClassicLevel } = require(process.env.B4ML_CLASSIC_LEVEL_MODULE);

async function main() {
  const directory = process.env.B4ML_DB_COPY;
  const needle = process.env.B4ML_STORAGE_NEEDLE;
  if (!directory || !needle) throw new Error("B4ML_DB_COPY and B4ML_STORAGE_NEEDLE are required");
  const db = new ClassicLevel(directory, { keyEncoding: "buffer", valueEncoding: "buffer" });
  await db.open();
  let matches = 0;
  for await (const [key, value] of db.iterator()) {
    const forms = [
      key.toString("utf8"), value.toString("utf8"),
      key.toString("utf16le"), value.toString("utf16le"),
    ];
    if (!forms.some((text) => text.includes(needle))) continue;
    process.stdout.write(JSON.stringify({
      key_base64: key.toString("base64"),
      value_base64: value.toString("base64"),
      key_utf8: forms[0],
      value_utf8: forms[1],
      key_utf16le: forms[2],
      value_utf16le: forms[3],
    }) + "\n");
    matches += 1;
  }
  await db.close();
  if (!matches) throw new Error("No matching local-storage record")
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
