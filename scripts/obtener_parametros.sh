#! /bin/bash

echo

echo "Looking for \"period:\":"
grep "period:" $1
echo

echo "Looking for \"log_freq:\":"
grep "log_freq:" $1
echo

echo "Looking for \"mimo_layers:\":"
grep "mimo_layers:" $1
echo

echo "Looking for \"frequency:\":"
grep "frequency:" $1
echo

echo "Looking for \"bandwidth:\":"
grep "bandwidth:" $1
echo

echo "Looking for \"speed:\":"
grep "speed:" $1
echo

echo "Looking for \"max_distance:\":"
grep "max_distance:" $1
echo
