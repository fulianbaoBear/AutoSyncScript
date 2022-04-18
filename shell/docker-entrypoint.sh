#!/bin/bash
set -x;

echo "===================开始更新=================";

if [ -z "$CODE_DIR" ]; then
  CODE_DIR="/scripts";
fi

if [ -z "$SSH_ROOT" ]; then
    SSH_ROOT=~/.ssh/;
fi

if [ ! -d $SSH_ROOT ]; then
  mkdir ~/.ssh/;
  ssh-keyscan github.com > $SSH_ROOT/known_hosts;
fi

if [ ! -d $CODE_DIR ]; then
    mkdir -p $CODE_DIR;
fi


if [ ! -d $CODE_DIR/.git ]; then
  cd $CODE_DIR && git init;
  if [ -z "$REPO_URL" ]; then
    REPO_URL=https://github.com/ClassmateLin/scripts_v2.git;
  fi
  git remote add origin $REPO_URL;
  git pull origin master;
  git branch --set-upstream-to=origin/master master;
else
  cd $CODE_DIR && git fetch --all && git reset --hard origin/master;
fi

CONF_DIR="$CODE_DIR/conf";

if [ ! -f "$CONF_DIR/config.json" ]; then
  cp $CODE_DIR/.config.json $CONF_DIR/config.json;
fi

python $CODE_DIR/tools/update_config.py;

python $CODE_DIR/tools/update_crontab.py;
crontab -r;
crontab -u root $CODE_DIR/shell/crontab.sh;
/etc/init.d/cron restart;

pip install -r $CODE_DIR/requirements.txt;

cp $CODE_DIR/shell/docker-entrypoint.sh /bin/docker-entrypoint;
chmod a+x /bin/docker-entrypoint;

tail -f /dev/null;
