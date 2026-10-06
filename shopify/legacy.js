// Intentional BreakGuard fixture: legacy ScriptTag usage
export function installLegacyScriptTag(admin) {
  return admin.rest.resources.ScriptTag.create({
    src: "https://example.com/legacy.js"
  });
}
