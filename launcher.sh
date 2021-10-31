#!/usr/bin/env bash
python -c'from localhigh.gateways.db import init_db;init_db()'
python -m 'localhigh'
