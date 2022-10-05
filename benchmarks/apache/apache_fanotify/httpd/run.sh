#!/bin/bash
/bin/fanotify &
apachectl -D FOREGROUND
