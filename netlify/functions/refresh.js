/*
 * POST /.netlify/functions/refresh
 * Triggers the GitHub Actions "Fetch jobs" workflow (the Refresh button).
 * Token stays server-side. Auto-detects the repo's default branch so it works
 * whether your default branch is main or master.
 *
 * Netlify env vars (Site settings -> Environment variables):
 *   GH_DISPATCH_TOKEN  fine-grained PAT with "Actions: write" on the repo
 *   GH_REPO            "your-username/jobs-heyaman"
 *   GH_WORKFLOW        (optional) workflow file, default fetch-jobs.yml
 *   GH_BRANCH          (optional) branch override
 */
exports.handler = async () => {
  const token = process.env.GH_DISPATCH_TOKEN;
  const repo = process.env.GH_REPO;
  const wf = process.env.GH_WORKFLOW || "fetch-jobs.yml";
  if (!token || !repo) {
    return json(501, { error: "Refresh not configured: set GH_DISPATCH_TOKEN and GH_REPO in Netlify env vars." });
  }
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "the-job-hunt",
  };
  try {
    // resolve default branch unless overridden
    let ref = process.env.GH_BRANCH;
    if (!ref) {
      const info = await fetch(`https://api.github.com/repos/${repo}`, { headers });
      if (info.status === 401 || info.status === 403)
        return json(info.status, { error: "GitHub token rejected — check GH_DISPATCH_TOKEN scope (Actions: write)." });
      if (info.status === 404)
        return json(404, { error: `Repo not found: ${repo}. Check GH_REPO (owner/name) and token access.` });
      ref = (await info.json()).default_branch || "main";
    }
    const r = await fetch(
      `https://api.github.com/repos/${repo}/actions/workflows/${wf}/dispatches`,
      { method: "POST", headers, body: JSON.stringify({ ref }) }
    );
    if (r.status === 204) return json(200, { ok: true, ref });
    const t = await r.text();
    return json(r.status, { error: `GitHub said ${r.status}: ${t.slice(0, 160)}` });
  } catch (e) {
    return json(500, { error: String(e).slice(0, 160) });
  }
};

function json(statusCode, body) {
  return { statusCode, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
}
