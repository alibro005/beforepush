# Git Pre-push Hook

BeforePush can run automatically before `git push` using a Git `pre-push` hook.

Instead of running `beforepush` manually before every push, you can let BeforePush manage the hook for you.

## How It Works

When you run:

```bash
git push
```

Git runs the `pre-push` hook before the push.

The BeforePush hook runs:

```bash
beforepush
```

If BeforePush exits with a non-zero status because a check fails, the hook returns that status and Git stops the push.

If all checks pass, the push continues normally.

## Install the Hook

From inside a Git repository, run:

```bash
beforepush install-hook
```

BeforePush creates the repository's `pre-push` hook and configures it to run BeforePush automatically.

After installation, you can use:

```bash
git push
```

and BeforePush will run automatically.

Installing the hook again is safe. If the BeforePush hook is already installed, no changes are made.

## Uninstall the Hook

To remove a pre-push hook installed by BeforePush, run:

```bash
beforepush uninstall-hook
```

If BeforePush did not install the existing hook, it will not remove it.

## Existing Hooks

BeforePush does not overwrite an existing `pre-push` hook that it did not install.

If a `pre-push` hook already exists, `beforepush install-hook` leaves it unchanged and reports that an existing hook was found.

This prevents BeforePush from accidentally replacing hooks managed by another tool or created manually.

## Test the Hook

After installing the hook, make a change in your repository and run:

```bash
git push
```

BeforePush will run automatically before Git attempts to push.

If all checks pass, the push continues.

If a check fails, the push is stopped.

## Bypass the Hook

If you intentionally need to push without running the `pre-push` hook, use:

```bash
git push --no-verify
```

This bypasses Git's pre-push hook for that push.

## Notes

Git hooks are local to each repository and are not included when the repository is pushed to GitHub. Each user who wants to use the BeforePush hook must install it locally.

The `beforepush` command must be installed and available in the user's `PATH` when Git runs the hook.

For example:

```bash
beforepush --version
```

can be used to verify that the command is available.
