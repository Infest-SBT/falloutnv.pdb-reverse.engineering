#!/bin/sh
# Сборка fnv_probe.dll (x86, без CRT) clang + lld-link; повторяемая: одинаковый вход -> одинаковый выход.
set -e
cd "$(dirname "$0")"
llvm-dlltool -m i386 -d kernel32.def -l kernel32.lib -k
clang --target=i686-pc-windows-msvc -O2 -ffreestanding -fno-builtin -fno-stack-protector -mno-sse \
      -fno-asynchronous-unwind-tables -c fnv_probe.c -o fnv_probe.obj
lld-link /dll /noentry /nodefaultlib /machine:x86 /safeseh:no /brepro /out:fnv_probe.dll fnv_probe.obj kernel32.lib \
      /export:NVSEPlugin_Query /export:NVSEPlugin_Load
rm -f fnv_probe.lib fnv_probe.exp
sha256sum fnv_probe.dll
