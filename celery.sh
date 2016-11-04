#!/usr/bin/env bash


function start() {
    # Start the celery worker
    echo 'Starting celery workers'
    celery worker -A crashreporter_hq.celery --loglevel=debug
    celery -A crashreporter_hq.celery beat --loglevel=debug
}

function stop() {
    echo 'Stopping celery workers'
    ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
}

function list() {
    echo 'Active worker processes:'
    ps auxww | grep 'celery worker'
}

if [ $1 == 'start' ]
then
    start
elif [ $1 == 'stop' ]
then
    stop
elif [ $1 == 'list' ]
then
    list
fi

