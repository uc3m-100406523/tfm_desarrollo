#! /bin/bash

# Dependencias de Netfilter Queues, Minimalistic Netlink, Make y g++
sudo apt-get install libnetfilter-queue-dev libmnl-dev make g++ -y

# Solución a un error frecuente de dependencias
# wget http://archive.ubuntu.com/ubuntu/pool/universe/libn/libnetfilter-queue/libnetfilter-queue-dev_1.0.3-1_amd64.deb
# wget http://archive.ubuntu.com/ubuntu/pool/universe/libn/libnetfilter-queue/libnetfilter-queue1_1.0.3-1_amd64.deb
# sudo dpkg -i libnetfilter-queue-dev_1.0.3-1_amd64.deb
# sudo dpkg -i libnetfilter-queue1_1.0.3-1_amd64.deb
# rm libnetfilter-queue-dev_1.0.3-1_amd64.deb libnetfilter-queue1_1.0.3-1_amd64.deb
