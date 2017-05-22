#!/bin/bash
# Script for playing Fuego on 9x9 KGS on a machine with 2 cores / 2 GB

FUEGO="../../build/autotools/release/fuegomain/fuego"
NAME=Fuego9
DESCRIPTION=""

usage() {
  cat >&2 <<EOF
Usage: $0 [options]
Options:
  -n maxgames: Limit number games to maxgames
  -h Print help and exit
EOF
}

MAXGAMES_OPTION=""
while getopts "n:h" O; do
case "$O" in
  n)   MAXGAMES_OPTION="-maxgames $OPTARG";;
  h)   usage; exit 0;;
  [?]) usage; exit 1;;
esac
done

shift $(($OPTIND - 1))
if [ $# -gt 0 ]; then
  usage
  exit 1
fi


echo "Enter KGS password for $NAME:"
read PASSWORD

GAMES_DIR="games/$NAME"
mkdir -p "$GAMES_DIR"

cat <<EOF >config-9-2c.gtp
# This file is auto-generated by play-9-2c.sh. Do not edit.

go_param debug_to_comment 1
go_param auto_save $GAMES_DIR/$NAME-
go_sentinel_file stop-9-2c

# Use 1.6 GB for two trees (search and the init tree used for reuse_subtree)
uct_max_memory 1600000000
uct_param_player reuse_subtree 1
uct_param_player ponder 1

# Set KGS rules (Chinese, positional superko)
go_rules kgs

sg_param time_mode real
uct_param_search number_threads 2
uct_param_search lock_free 1
EOF

cat >tmp.cfg <<EOF
name=$NAME
password=$PASSWORD
room=Computer Go
mode=custom
gameNotes=$DESCRIPTION
rules=chinese
rules.boardSize=9
rules.time=10:00
verbose=t
engine=$FUEGO --size 9 --config config-9-2c.gtp $MAXGAMES_OPTION
reconnect=t
EOF
java -jar kgsGtp.jar tmp.cfg && rm -f tmp.cfg

#-----------------------------------------------------------------------------
