#!/bin/bash
# Script para instalar dependências e rodar a análise

echo "📦 Instalando dependências..."

# Tentar paru
if command -v paru &> /dev/null; then
    echo "Usando paru..."
    paru -S python-pymysql --noconfirm
# Tentar yay
elif command -v yay &> /dev/null; then
    echo "Usando yay..."
    yay -S python-pymysql --noconfirm
# Tentar pacman direto
else
    echo "Usando pacman (precisa de sudo)..."
    sudo pacman -S python-pymysql --noconfirm
fi

echo ""
echo "✅ Dependências instaladas!"
echo ""
echo "🔍 Rodando análise..."
python3 /home/will/bancochico/analyze_mysql.py
