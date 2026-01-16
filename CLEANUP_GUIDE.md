# Git大文件清理指南

## 问题描述
Git推送时出现以下错误：
```
remote: warning: File build/llama_med_webui/PYZ-00.pyz is 73.53 MB; this is larger than GitHub's recommended maximum file size of 50.00 MB
remote: error: File build/llama_med_webui/llama_med_webui.pkg is 273.37 MB; this exceeds GitHub's file size limit of 100.00 MB
```

这些是PyInstaller生成的打包文件，不应该提交到Git仓库。

## 解决方案

### 方案1：使用git filter-branch（推荐用于小型仓库）
```bash
# 1. 备份当前仓库
cd /home/dell/llama_med_webui
cp -r .git .git_backup

# 2. 使用git filter-branch删除大文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch build/llama_med_webui/PYZ-00.pyz build/llama_med_webui/llama_med_webui.pkg" \
  --prune-empty --tag-name-filter cat -- --all

# 3. 清理本地引用
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制推送到远程
git push origin --force --all
git push origin --force --tags
```

### 方案2：使用BFG Repo-Cleaner（推荐用于大型仓库）
```bash
# 1. 下载BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# 2. 备份仓库
cd /home/dell/llama_med_webui
cp -r .git .git_backup

# 3. 删除大文件
java -jar bfg-1.14.0.jar --delete-files "*.pyz" --delete-files "*.pkg" .

# 4. 清理Git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. 强制推送
git push origin --force --all
git push origin --force --tags
```

### 方案3：使用git-lfs（如果确实需要这些文件）
如果这些打包文件确实需要版本控制，可以使用Git LFS：

```bash
# 1. 安装git-lfs
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# 2. 初始化git-lfs
git lfs install

# 3. 跟踪大文件类型
git lfs track "*.pyz"
git lfs track "*.pkg"
git lfs track "*.exe"
git lfs track "*.app"
git lfs track "*.dmg"
git lfs track "*.msi"

# 4. 提交.gitattributes
git add .gitattributes
git commit -m "Add git-lfs tracking for large files"

# 5. 重新添加大文件
git add build/llama_med_webui/PYZ-00.pyz
git add build/llama_med_webui/llama_med_webui.pkg
git commit -m "Add large files via git-lfs"

# 6. 推送
git push origin main
```

## 预防措施

### 1. 更新.gitignore
已经更新了`.gitignore`文件，包含了以下规则：
```
# PyInstaller打包文件（特别大的文件）
*.pkg
*.pyz
*.spec
*.exe
*.app
*.dmg
*.msi
*.whl
*.egg
*.tar.gz
*.zip
build/*.pkg
build/*.pyz
build/*.exe
build/*.app
build/*.dmg
build/*.msi
```

### 2. 添加预提交钩子
创建`.git/hooks/pre-commit`文件：

```bash
#!/bin/bash
# 预提交钩子：检查文件大小

MAX_SIZE=52428800  # 50MB in bytes

# 检查暂存的文件大小
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        if [ "$size" -gt "$MAX_SIZE" ]; then
            echo "错误：文件 $file 大小超过50MB ($((size/1048576))MB)"
            echo "请使用git-lfs或从提交中移除该文件"
            exit 1
        fi
    fi
done
```

### 3. 添加.gitattributes
创建`.gitattributes`文件：

```gitattributes
# 自动检测文本文件
* text=auto

# 二进制文件
*.pyz binary
*.pkg binary
*.exe binary
*.app binary
*.dmg binary
*.msi binary
*.whl binary
*.egg binary
*.tar.gz binary
*.zip binary

# 构建文件不应该被跟踪
build/*.pkg binary -diff -merge
build/*.pyz binary -diff -merge
build/*.exe binary -diff -merge
```

## 清理后的验证

```bash
# 检查仓库大小
git count-objects -vH

# 检查大文件是否还在历史中
git log --all --stat --oneline | grep -E "MB|GB|\.pkg|\.pyz"

# 检查当前工作区
git status
git ls-files | grep -E "\.(pkg|pyz|exe|app|dmg|msi)$"
```

## 注意事项

1. **备份**：在执行任何清理操作前，务必备份整个`.git`目录
2. **协作**：如果有多人协作，需要通知所有协作者重新克隆仓库
3. **历史重写**：`git filter-branch`和BFG都会重写Git历史，这会影响所有分支和标签
4. **Git LFS限制**：GitHub免费账户的Git LFS有存储和带宽限制

## 推荐方案

对于这个项目，**推荐方案1**（使用git filter-branch），因为：
1. 这些是构建产物，不应该提交到Git
2. 项目历史相对简单
3. 可以彻底从历史中删除大文件

执行后，`.gitignore`会防止未来再次提交这些文件。