# Database Schema Summary

## Tables Overview

### Main Tables
1. **job_posts** - Main job posting table
2. **organizations** - Company/organization lookup table
3. **tech** - Technology lookup table
4. **job_functions** - Job function lookup table

### Junction Tables (Many-to-Many)
5. **job_posts_tech** - Links job posts to technologies
6. **job_posts_job_functions** - Links job posts to job functions

### Additional
7. **job_posts_details** - Additional job post details (not explored yet)

## Table Structures

### job_posts
- `id` (bigint) - Primary key
- `organization_id` (bigint) - Foreign key to organizations.id
- `country_id` (bigint)
- `datetime_pulled` (timestamp)
- `technologies` (text) - May be redundant with junction table
- `job_functions` (text) - May be redundant with junction table

### organizations
- `id` (bigint) - Primary key
- `name` (text) - **Use this for organization queries**
- `slug` (text)
- Other fields: industry, headquarters_location, url, etc.

### tech
- `id` (bigint) - Primary key
- `name` (text) - **Use this for technology queries**
- `slug` (text)

### job_functions
- `id` (bigint) - Primary key
- `name` (text) - **Use this for job_function queries**
- `slug` (text)
- `total_mentions` (bigint)

### job_posts_tech
- `job_post_id` (bigint) - Foreign key to job_posts.id
- `tech_id` (bigint) - Foreign key to tech.id

### job_posts_job_functions
- `job_post_id` (bigint) - Foreign key to job_posts.id
- `job_function_id` (bigint) - Foreign key to job_functions.id

## Query Strategy

For the advanced query API, we need to:

1. **Organization queries**: JOIN `job_posts` with `organizations` on `organization_id`
2. **Technology queries**: JOIN `job_posts` → `job_posts_tech` → `tech`
3. **Job Function queries**: JOIN `job_posts` → `job_posts_job_functions` → `job_functions`

## Sample Data
- Total jobs: ~89,397
- Apple organization exists
- .NET technologies exist (C# (.NET 3.5/4), JScript.NET, C .NET, etc.)

## Example Query Structure

To find jobs matching: `organization: apple AND tech: .net`

```sql
SELECT DISTINCT jp.id
FROM job_posts jp
INNER JOIN organizations o ON jp.organization_id = o.id
INNER JOIN job_posts_tech jpt ON jp.id = jpt.job_post_id
INNER JOIN tech t ON jpt.tech_id = t.id
WHERE o.name ILIKE '%apple%'
  AND t.name ILIKE '%.net%'
```

