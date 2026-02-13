#!/usr/bin/env bash
set -euo pipefail

MSG="${1:-update}"
REMOTE="${2:-origin}"
BRANCH="${3:-main}"

echo "==> 1) 修复 github.com host key（known_hosts）"
ssh-keygen -R github.com >/dev/null 2>&1 || true
ssh-keygen -R 140.82.121.4 >/dev/null 2>&1 || true

tmpfile="$(mktemp)"
ssh-keyscan -t rsa,ecdsa,ed25519 github.com 2>/dev/null | sort -u > "$tmpfile"

echo "==> 2) 当前抓到的 GitHub 指纹："
ssh-keygen -lf "$tmpfile" || true
echo
echo "请对照 GitHub 官方文档核验指纹："
echo "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints"
echo

read -r -p "确认无误后继续写入 ~/.ssh/known_hosts ? (yes/no): " ok
if [[ "$ok" != "yes" ]]; then
  echo "已取消。"
  rm -f "$tmpfile"
  exit 1
fi

mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat "$tmpfile" >> ~/.ssh/known_hosts
sort -u ~/.ssh/known_hosts -o ~/.ssh/known_hosts
chmod 600 ~/.ssh/known_hosts
rm -f "$tmpfile"

echo "==> 3) 测试 SSH 到 GitHub"
ssh -T git@github.com || true

echo "==> 4) 提交并推送"
git add .
git commit -m "$MSG" || echo "没有新改动，跳过 commit"
git push "$REMOTE" "$BRANCH"

echo "✅ 完成"
