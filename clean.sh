#!/bin/bash

# 清除build产生的文件，但保留bin和logs目录及其内容

# 删除build和dist目录（如果存在）
[ -d "build" ] && rm -rf build
[ -d "dist" ] && rm -rf dist

# 删除Python编译文件和缓存目录，排除bin和logs
find . -path "./bin" -prune -o -path "./logs" -prune -o -type d -name "__pycache__" -exec rm -rf {} +
find . -path "./bin" -prune -o -path "./logs" -prune -o -type f -name "*.pyc" -delete
find . -path "./bin" -prune -o -path "./logs" -prune -o -type f -name "*.pyo" -delete
find . -path "./bin" -prune -o -path "./logs" -prune -o -type f -name "*.pyd" -delete
