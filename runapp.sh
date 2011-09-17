./gfserver.py -m app -n aaagfserver --pdir=pids/ -p 6 --debug --logdir logs/ --logfiles 5 --logsize 200000 -s tcp:localhost:8000 --backlog 4096 -a $1
