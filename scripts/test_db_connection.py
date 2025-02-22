#!/usr/bin/env python3
"""Test database connectivity using psycopg2"""

import os
import sys
# pylint: disable=import-error
import psycopg2  # type: ignore

def test_connection():
    """Test database connection using environment variables"""
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        print('Database connection successful!')
        return True
    except (psycopg2.Error, KeyError) as e:
        print(f'Database connection failed: {e}')
        return False

if __name__ == "__main__":
    sys.exit(0 if test_connection() else 1)
