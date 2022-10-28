#!/bin/bash

##################################################################
# This script listens for sleep and lock events, and responds to #
# them by locking the screen with the eww script.                #
##################################################################

export SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

echo "initializing"

while true; do
echo 'starting loop'

# systemd-inhibit prevents sleeping until this command finishes
systemd-inhibit --what=sleep --mode=delay --who="Theme Locker" --why="to lock the screen" \
  gdbus monitor -y -d org.freedesktop.login1 | (
    CONTINUE=true
    while $CONTINUE; do
      # each line is generally an event
      read X
      # log what was recieved
      echo $X
      if [ -z "$X" ]; then
        echo "recieved an empty line, breaking loop"
        CONTINUE=false
      fi

      # test for lock shutdown
      if [ -f '/tmp/theme-lock-shutdown' ]; then
        exit
      fi

      # if the line contains the word "PrepareForSleep", then the system is about to sleep
      # if the line contains the word "Lock", then the system is about to lock
      echo $X | grep -P ".Lock|.PrepareForSleep"
      if [ $? -eq 0 ]; then
        # sleep has been triggered, lock
        echo before lock
        $SCRIPTPATH/eww/scripts/lock
        echo after lock
        # kill the monitor to stop inhibition
        killall -u $USER gdbus
        echo after kill
        # end the loop
        CONTINUE=false
      else 
        # leave alone
        echo ignoring
      fi
    done
  )

echo after loop
if [ -f '/tmp/theme-lock-shutdown' ]; then
  echo "exiting"
  rm -f /tmp/theme-lock-shutdown
  exit
fi

# wait for the system to sleep before inhibiting again
sleep 5

done
