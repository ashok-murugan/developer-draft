# .gitignore Security Verification Checklist

## ✅ Pre-Commit Security Checklist

Before pushing to a public GitHub repository, verify the following:

### 1. Compiled & Build Artifacts
- [ ] No `.class` files
- [ ] No `.jar`, `.war`, `.ear` files
- [ ] No `target/` directory (Maven)
- [ ] No `build/` directory (Gradle)
- [ ] No `out/` directory (IDE output)

### 2. IDE Configuration Files
- [ ] No `.idea/` directory (IntelliJ)
- [ ] No `.iml` files
- [ ] No `.settings/` directory (Eclipse)
- [ ] No `.vscode/` directory
- [ ] No `.project` or `.classpath` files

### 3. Operating System Files
- [ ] No `.DS_Store` files (macOS)
- [ ] No `Thumbs.db` files (Windows)
- [ ] No `desktop.ini` files

### 4. **CRITICAL: Sensitive Information**
- [ ] No `.env` files or environment variables
- [ ] No `.key`, `.pem`, `.p12`, `.pfx` files
- [ ] No `.jks`, `.keystore`, `.truststore` files
- [ ] No `secrets/` or `credentials/` directories
- [ ] No AWS credentials (`.aws/` directory)
- [ ] No Google Cloud credentials
- [ ] No API keys in code or config files
- [ ] No passwords or tokens

### 5. Logs & Temporary Files
- [ ] No `.log` files
- [ ] No `.tmp` or `.temp` files
- [ ] No `.bak` backup files
- [ ] No `.swp` or `.swo` editor swap files

### 6. Test Coverage Reports
- [ ] No `coverage/` directory
- [ ] No `jacoco.exec` files
- [ ] Coverage reports in `target/site/` are ignored

## 🔍 Verification Commands

Run these commands before committing:

```bash
# Check what files will be committed
git status

# Check for sensitive patterns
git ls-files | grep -E '\.(env|key|pem|jks|keystore)$'

# Check for credentials in tracked files
git grep -i "password\|api_key\|secret\|token" -- ':!.gitignore' ':!*.md'

# Verify .gitignore is working
git check-ignore -v target/ .idea/ .env

# List all untracked files
git ls-files --others --exclude-standard

# Check file sizes (large files might be binaries)
git ls-files | xargs ls -lh | awk '{if ($5 > 1000000) print $9, $5}'
```

## 🛡️ Security Best Practices

### What Should NEVER Be Committed:
1. **Credentials**: Passwords, API keys, tokens, certificates
2. **Personal Data**: Email addresses, phone numbers, addresses
3. **Build Artifacts**: Compiled code, packaged applications
4. **IDE Settings**: Personal IDE configurations
5. **Large Files**: Binaries, videos, large datasets
6. **Logs**: Application logs, debug files
7. **Temporary Files**: Swap files, cache, backups

### What SHOULD Be Committed:
1. **Source Code**: `.java` files
2. **Build Configuration**: `pom.xml`, `build.gradle`
3. **Documentation**: `README.md`, `CONTRIBUTING.md`
4. **Tests**: Test source files
5. **Configuration Templates**: `.env.example` (without actual values)
6. **Project Structure**: Directory structure, package organization

## 📋 Current .gitignore Organization

Our `.gitignore` is organized into these sections:

1. **Compiled Output** - Java bytecode and archives
2. **Build Tools** - Maven and Gradle artifacts
3. **IDEs & Editors** - IntelliJ, Eclipse, VS Code, NetBeans
4. **Operating Systems** - macOS, Windows, Linux
5. **Logs & Databases** - Log files and database files
6. **Security & Credentials** - CRITICAL security patterns
7. **Testing & Coverage** - Test reports and coverage
8. **Temporary & Backup Files** - Temp files and backups
9. **AI Assistants** - Copilot and other AI tools
10. **Documentation Build** - Generated documentation
11. **Misc** - Other patterns

## 🚨 Emergency: If You Accidentally Committed Secrets

If you've already committed sensitive information:

```bash
# DO NOT just delete and recommit - it's still in history!

# Option 1: Remove from last commit (if not pushed)
git rm --cached <file>
git commit --amend

# Option 2: Remove from history (if pushed) - USE WITH CAUTION
# This rewrites history and requires force push
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <file>" \
  --prune-empty --tag-name-filter cat -- --all

# Then force push (WARNING: coordinate with team)
git push origin --force --all

# Option 3: Use BFG Repo-Cleaner (recommended for large repos)
# https://rtyley.github.io/bfg-repo-cleaner/

# IMPORTANT: After removing secrets from Git
# 1. Rotate/revoke the exposed credentials immediately
# 2. Update all systems using those credentials
# 3. Monitor for unauthorized access
```

## ✅ Final Verification

Before making your repository public:

```bash
# 1. Review all files to be committed
git status
git diff --cached

# 2. Check for large files
git ls-files | xargs du -h | sort -h | tail -20

# 3. Search for common secret patterns
git grep -i "password" -- ':!.gitignore' ':!SECURITY_CHECKLIST.md'
git grep -i "api.key" -- ':!.gitignore' ':!SECURITY_CHECKLIST.md'
git grep -i "secret" -- ':!.gitignore' ':!SECURITY_CHECKLIST.md'

# 4. Verify .gitignore patterns
git check-ignore -v .idea/ target/ .env *.class

# 5. List what WILL be committed
git ls-files
```

## 📚 Resources

- [GitHub's .gitignore templates](https://github.com/github/gitignore)
- [Git documentation on .gitignore](https://git-scm.com/docs/gitignore)
- [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

## 🔐 Automated Security Scanning

Consider using these tools:

- **git-secrets**: Prevents committing secrets
- **truffleHog**: Searches for secrets in Git history
- **GitGuardian**: Real-time secret detection
- **GitHub Secret Scanning**: Built-in GitHub feature

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or download from: https://github.com/awslabs/git-secrets

# Set up git-secrets for this repo
git secrets --install
git secrets --register-aws
```

---

**Last Updated**: 2025-12-13  
**Status**: ✅ Verified and organized
