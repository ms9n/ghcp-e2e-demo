Add to context: plan.md, activity.md

We are building StockTracker project from scratch in this repo.

First read activity.md to see what was recently accomplished.

Start the site locally either with python3 -m http.server or npm run dev. If port is taken, try another port.

Open plan.md and choose the single highest priority task where passes is false.

This should be the one YOU decide has the highest priority - not necessarily the first in the list.

Check that the types check via pnpm typecheck and that the tests pass via pnpm test.

Work on exactly ONE task: implement the change.

After implementing, use Playwright to:
1. Navigate to the local server URL
2. Take a screenshot and save it as screenshots/[task-name].png

Append a dated progress entry to activity.md describing what you changed and the screenshot filename.

Update that task's passes in plan.md from false to true.

Make one git commit for that task only with a clear message.

Do not git init, do not change remotes, do not push.

ONLY WORK ON A SINGLE TASK.

When ALL tasks have passes true, output <promise>COMPLETE</promise>