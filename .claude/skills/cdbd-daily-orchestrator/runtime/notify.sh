#!/bin/zsh
# 사용법: notify.sh "메시지"
MSG="${1:-CdBd 자동제작 알림}"
MSG=${MSG//\"/\\\"}   # 메시지에 큰따옴표가 있어도 osascript 문자열 안 깨지게 이스케이프
/usr/bin/osascript -e "display notification \"${MSG}\" with title \"CdBd 자동제작\" sound name \"Basso\""
