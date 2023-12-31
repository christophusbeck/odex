# PSE Implementation 
[![pipeline status](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation/badges/main/pipeline.svg)](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation/-/commits/main)
[![coverage report](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation/badges/main/coverage.svg)](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation/-/commits/main)


The main objective of the project is to develop an experimental framework for studying the detection and generation of outlying data on high dimensional data sets. We build an experimental framework as a web application. The application applies different detection algorithms to detect outliers in an arbitrary selection of subspaces and datasets, and then, gather the results of the run. The application records the results of all runs. If the user provides a ground truth file, it compares the detected data objects with a ground truth label and output the accuracy of the final model.

The building blocks are:
- Browser: Chrome (version: 111.0.5563.64 on Windows/Linux/MacOS)
- Python version: 3.9+
- Django: 4.1.5
- Sqlite3

# Overview for this README
- [Dependencies](#dependencies)
- [Instructions](#installation)
- [Run Tests](#run-Tests)

# Dependencies
See [requirements.txt](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation/-/blob/514efcf442ab5e1f37a2dec8c930c2fdbd023299/requirements.txt)


# Installation
Supported local installations:
- [Docker (recommended)](#docker)
- [Instructions](#instructions)


# Docker
- Prepare directory for project code and virtualenv. Feel free to use a different location:
```
    $ mkdir -p ~/odex
    $ cd ~/odex
```

- Pull project code from [GitLab](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation)
```
    $ git clone https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation.git
```

- Build image(get into pse-implementation/docker) with GitLab account
```
    $ cd pse-implementation
    $ cd docker
    $ export USER=your username on GitLab
    $ export PASSWORD=your password
    $ docker build --build-arg GITLAB="$USER:$PASSWORD" -t odex:v1 .
```
If the passworf is plaintext, use URL encoding
```
!     #    $    &    '    (    )    *    +    ,    /    :    ;    =    ?    @    [    ]
%21  %23  %24  %26  %27  %28  %29  %2A  %2B  %2C  %2F  %3A  %3B  %3D  %3F  %40  %5B  %5D
```


- Run Server(location: pse-implementation/docker)
```
    $ docker-compose up
```

The site should now be running at `http://127.0.0.1:3214`

- Default users
```
    username: tester1
    password: 123

    username: tester2
    password: 123

```

- Available TANs
```
    121
    122
    124
    125
    126
    127
    128
    129
    130
```

- Used TANs
```
    123
```

# Instructions

## Debian/Ubuntu
- Install default environment
```
    $ sudo apt -y update
    $ sudo apt install -y gcc python3-dev python3-venv libcurl4-openssl-dev libssl-dev build-essential libsqlite3-dev
    $ sudo apt -y upgrade
```

- Prepare directory for project code and virtualenv. Feel free to use a different location:
```
    $ mkdir -p ~/odex
    $ cd ~/odex
```

- Prepare virtual environment
```
    $ python3 -m venv hc-venv
    $ source hc-venv/bin/activate
    $ pip3 install wheel 
```

- Pull project code from [GitLab](https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation)
```
    $ git clone https://git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation.git
```

- Install requirements into virtualenv
```
    $ pip3 install -r pse-implementation/requirements.txt
```

- Migrate database tables
```
    $ cd ~/odex/pse-implementation
    $ python3 manage.py makemigrations user
    $ python3 manage.py makemigrations experiment
    $ python3 manage.py migrate
```

- Load default database data
```
    $ python manage.py loaddata fixtures/fixtures.json
```

- Run server
```
    $ python3 manage.py runserver
```

The site should now be running at `http://127.0.0.1:8000`

- Default user
```
    username: tester1
    password: 123

    username: tester2
    password: 123
```

- Available TANs
```
    121
    122
    124
    125
    126
    127
    128
    129
    130
```

- Used TANs
```
    123
```

# Run Tests

location: pse-implementation/

## Unit tests
```
    $ coverage run manage.py test user.tests experiment.tests
```

## Integration tests
```
    $ python3 manage.py test integration_tests.TestCases
```
