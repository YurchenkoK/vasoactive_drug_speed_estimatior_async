#!/bin/sh
# Script to initialize Redis with ACL user for the application

echo "Initializing Redis ACL for user management..."

# Try to connect and create default user with Lua script capabilities
redis-cli -h redis << 'EOF'
# Create default ACL user with permissions for Lua scripts
ACL SETUSER default on >redis ~* +@all

# Verify user was created
ACL LIST

# Test connection
PING
EOF

echo "Redis ACL initialization complete!"
