# Sumble Advanced Query API --- Coding Project

You have **3 hours** to complete the following coding project.\
When finished, submit your project via this Google Form:\
**https://forms.gle/AkcyVcfYNFzm7hy78**

## Overview

At **sumble.com/jobs**, users can browse jobs with "simple" filters
(technology **OR** job function).\
However, selecting a technology disables job-function filtering.

For power users, **advanced filtering** exists on **sumble.com**,
allowing multi-property logical queries such as:

-   `(tech: python AND tech: sql AND organization: amazon)`\
-   `(job_function: software engineer AND tech: sql)`

Your task is to build an API that supports these "advanced queries."

## Database Setup

We provide a subset of our production PostgreSQL database via Docker.

Run locally (requires Docker):

    docker run -p 5432:5432 nzsne8pttnh8wrpu/p2ckp9ddret2arc2

Connection details:

-   **Host:** 127.0.0.1\
-   **Port:** 5432\
-   **Username:** postgres\
-   **Password:** supersecretpassword\
-   **Database:** sumble_data

## Main Task

Build an API (in any language you prefer) that:

1.  Accepts **advanced query objects** (JSON recommended; no need to
    build a string parser).
2.  Supports boolean logic:
    -   **AND**
    -   **OR**
    -   **NOT**
3.  Operates on job post fields:
    -   `technology`
    -   `job_function`
    -   `organization`
4.  Returns **a JSON list of matching jobs**.\
    (You may limit output to **10 jobs** for development speed.)

Example logical query:

    NOT organization: apple AND (job_function: statistician OR tech: psql)

You are free to define the schema in a way that is easiest to implement.

## Additional Guidance

This project serves two purposes:

1.  To show you the type of systems we build at Sumble.
2.  To evaluate your ability to work across multiple engineering
    domains.

Use **any** language, libraries, or tools --- including ChatGPT --- to
build the solution.

## Submission Requirements

Your submission **must include**:

### 1. Your Code

The complete implementation of your API.

### 2. Docker Files

Include both:

-   `docker-compose.yml`
-   `Dockerfile`

We must be able to run your API via:

    docker compose up --build

### 3. `curl` Examples

Provide curl commands for the following:

#### a. Query

**organization: apple AND tech: .net**\
Must return in **\< 30 seconds**.

#### b. Query

**NOT organization: apple AND (job_function: statistician OR tech:
psql)**

## Project Submission

Upload a **ZIP file** containing all required artifacts to:\
**https://forms.gle/AkcyVcfYNFzm7hy78**

## Reference Files

### Example `docker-compose.yml`

``` yaml
services:
  db:
    image: nzsne8pttnh8wrpu/p2ckp9ddret2arc2
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 1s
    ports:
      - 5432:5432

  application:
    build: .
    depends_on:
      db:
        condition: service_healthy
    environment:
      - PGHOST=db
      - PGPORT=5432
      - PGUSER=postgres
      - PGPASSWORD=supersecretpassword
      - PGDATABASE=sumble_data
```

### Example `Dockerfile`

``` dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y postgresql-client
CMD ["psql", "-c", "\dt"]
```
