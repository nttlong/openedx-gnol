#!/usr/bin/env bash

set -e

source $HOME/jenkins_env

NODE_ENV_DIR=$HOME/nenv
NODE_VERSION=8.9.3

NODE_INSTALL_COMMAND="nodeenv --node=$NODE_VERSION --prebuilt $NODE_ENV_DIR --force"

# Clear the mongo database
# Note that this prevents us from running jobs in parallel on a single worker.
mongo --quiet --eval 'db.getMongo().getDBNames().forEach(function(i){db.getSiblingDB(i).dropDatabase()})'

# Ensure we have fetched origin/master
# Some of the reporting tools compare the checked out branch to origin/master;
# depending on how the GitHub plugin refspec is configured, this may
# not already be fetched.
git fetch origin master:refs/remotes/origin/master

# Reset the jenkins worker's virtualenv back to the
# state it was in when the instance was spun up.
if [ -e $HOME/edx-venv_clean.tar.gz ]; then
    rm -rf $HOME/edx-venv
    tar -C $HOME -xf $HOME/edx-venv_clean.tar.gz
fi

# Activate the Python virtualenv
source $HOME/edx-venv/bin/activate

# add the node packages dir to PATH
PATH=$PATH:node_modules/.bin

echo "setting up nodeenv"
pip install nodeenv
# Ensure we are starting with a clean node env directory
rm -rf $NODE_ENV_DIR

# Occasionally, the command to install node hangs. We need to catch that and retry.
# Note that this will retry even if the command itself fails.
WAIT_COUNT=0
until timeout 30s $NODE_INSTALL_COMMAND || [ $WAIT_COUNT -eq 2 ]; do
    echo "re-trying to install node version..."
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT+1))
done

# If we tried the max number of times, we need to quit.
if [ $WAIT_COUNT -eq 2 ]; then
    echo "Node environment installation command was not successful. Exiting."
    exit 1
fi

source $NODE_ENV_DIR/bin/activate
echo "done setting up nodeenv"
echo "node version is `node --version`"
echo "npm version is `npm --version`"

# Log any paver or ansible command timing
TIMESTAMP=$(date +%s)
SHARD_NUM=${SHARD:="all"}
export PAVER_TIMER_LOG="test_root/log/timing.paver.$TEST_SUITE.$SHARD_NUM.log"
export ANSIBLE_TIMER_LOG="test_root/log/timing.ansible.$TIMESTAMP.log"

echo "This node is `curl http://169.254.169.254/latest/meta-data/hostname`"
