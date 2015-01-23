#!/bin/bash
ssh -f -N -L 195.19.44.143:30090:10.20.0.55:5000 tpadmin@195.19.44.143 -o TCPKeepAlive=yes ServerAliveInterval=5000 ServerAliveCountMax=3
