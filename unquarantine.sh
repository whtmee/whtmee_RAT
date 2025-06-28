#!/bin/bash


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$DIR/client.app"


xattr -cr "$APP_PATH" 2>/dev/null


chmod +x "$APP_PATH"


spctl --remove "$APP_PATH" 2>/dev/null


find "$APP_PATH" -type f -exec xattr -cr {} \; 2>/dev/null


find "$APP_PATH" -type f -exec chmod +x {} \; 2>/dev/null

echo "все, теперь норм" 