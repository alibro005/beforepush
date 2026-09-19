# Git Pre-push Hook

You can configure BeforePush to run automatically before `git push`. This allows you to check your branch before every push without running `beforepush` manually.

## How It Works

When you run:

```bash
git push
```

Git runs the `pre-push` hook first.

The hook runs:

```bash
beforepush
```

If BeforePush exits with a non-zero status because a check fails, the push is blocked.

## Setup

From the root of your Git repository, create a file named:

```text
.git/hooks/pre-push
```

Add:

```sh
#!/bin/sh

beforepush
status=$?

if [ $status -ne 0 ]; then
    echo "BeforePush checks failed. Push aborted."
    exit $status
fi
```

On macOS and Linux, make the hook executable:

```bash
chmod +x .git/hooks/pre-push
```

The hook is now active.

## Test the Hook

Make a change in your repository and run:

```bash
git push
```

BeforePush will run automatically before Git attempts to push.

If all checks pass, the push continues.

If a check fails, the push is stopped.

## Bypass the Hook

If you need to push without running the pre-push hook, use:

```bash
git push --no-verify
```

Use this only when you intentionally want to bypass the checks.

## Notes

Git hooks are local to your repository and are not included when you push the repository to GitHub. Each user who wants to use the hook needs to configure it locally.

The `beforepush` command must be installed and available in the user's `PATH`.
