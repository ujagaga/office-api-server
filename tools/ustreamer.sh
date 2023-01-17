#!/bin/bash

if [[ "$#" -lt 2 ]]; then
    echo "Usage:"
    echo "$0 <working_dir> start <user> <password>"
    echo "    or"
    echo "$0 <working_dir> stop"
    exit 1
fi

WORKING_DIR=$1
OPERATION=$2
USER_NAME=$3
USER_PASS=$4
PID_FILE_PATH="runner.pid"

cd ${WORKING_DIR}

case "${OPERATION}" in
    start)
        # Already running
        if [ -f ${PID_FILE_PATH} ]; then
            pid=$(cat ${PID_FILE_PATH})
            if $(ps -p ${pid} > /dev/null); then
                echo "Already running [PID: ${pid}], you can stop it and retry."
                exit 1
            fi
        fi

        ustreamer --host=0.0.0.0 --port=8013 --device=/dev/video1 --drop-same-frames=30 --slowdown \
        --user ${USER_NAME} --passwd ${USER_PASS} --static . 2>&1 & echo $! > ${PID_FILE_PATH}

        if ps -p $! > /dev/null
        then
           echo "Success"
           exit 0
        else
           echo "Failed"
           exit 1
        fi
    ;;
    stop)
        kill $(cat ${PID_FILE_PATH})
    ;;
esac