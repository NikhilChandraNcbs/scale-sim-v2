#!/bin/bash
while IFS= read -r line; do
    echo "Executing: $line"
    eval "$line"
done < "configs/vit_cfgs/cmds_l.txt"