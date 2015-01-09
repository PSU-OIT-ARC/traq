#!/bin/bash


# Set timezone
ln -sf /usr/share/zoneinfo/US/Pacific /etc/localtime
echo Date: 
date

# Set LDAP search base
echo "base dc=pdx,dc=edu" >> /etc/ldap.conf
