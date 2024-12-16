#!/bin/bash
while IFS= read -r line; do
    echo "Executing: $line"
    eval "$line"
done < "configs/vit_cfgs/dense/cmds_d.txt"