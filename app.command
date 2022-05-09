#!/bin/zsh

dir=$(dirname $0)
cd $dir
echo $dir
echo $(pwd)
python "$dir/app.py"