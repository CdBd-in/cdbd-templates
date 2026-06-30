#!/bin/zsh
# 사용법: notify.sh "메시지"
MSG="${1:-CdBd 자동제작 알림}"
/usr/bin/osascript -e "display notification \"${MSG}\" with title \"CdBd 자동제작\" sound name \"Basso\""
