# PostgreSQL schema dump — `public`
_Generated: 2025-09-03 20:02:08_

## Tables & columns

### alembic_version

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `version_num` | `varchar` | NO |  | 32 |  |  |

### authors

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('authors_id_seq'::regclass)` |  | 32 |  |
| 2 | `telegram_id` | `int8` | NO |  |  | 64 |  |
| 3 | `username` | `varchar` | YES |  |  |  |  |
| 4 | `display_name` | `varchar` | YES | `'аноним'::character varying` |  |  |  |

### categories

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('categories_id_seq'::regclass)` |  | 32 |  |
| 2 | `name` | `text` | YES |  |  |  |  |
| 3 | `item_name` | `text` | YES |  |  |  |  |

### category_definitions

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `variant_name` | `text` | NO |  |  |  |  |
| 2 | `category_id` | `int4` | NO |  |  | 32 |  |

### contacts

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('contacts_id_seq'::regclass)` |  | 32 |  |
| 2 | `category` | `text` | YES |  |  |  |  |
| 3 | `item_name` | `text` | YES |  |  |  |  |
| 4 | `location` | `text` | YES |  |  |  |  |
| 5 | `telegram` | `text` | YES |  |  |  |  |
| 6 | `phone` | `text` | YES |  |  |  |  |
| 7 | `description` | `text` | YES |  |  |  |  |
| 8 | `rating` | `float8` | YES |  |  | 53 |  |
| 9 | `photo_url` | `text` | YES |  |  |  |  |

### entities

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('entities_id_seq'::regclass)` |  | 32 |  |
| 2 | `category_id` | `int4` | YES |  |  | 32 |  |
| 3 | `name` | `text` | NO |  |  |  |  |
| 4 | `location` | `text` | YES |  |  |  |  |
| 5 | `description` | `text` | YES |  |  |  |  |
| 6 | `photo_url` | `text` | YES |  |  |  |  |

### expert_info

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('expert_info_id_seq'::regclass)` |  | 32 |  |
| 2 | `content` | `text` | YES |  |  |  |  |
| 3 | `embedding` | `vector` | YES |  |  |  |  |
| 4 | `source` | `text` | YES |  |  |  |  |
| 5 | `created_at` | `timestamp` | YES | `CURRENT_TIMESTAMP` |  |  |  |

### jobs_media

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int8` | NO | `nextval('jobs_media_id_seq'::regclass)` |  | 64 |  |
| 2 | `media_id` | `int8` | NO |  |  | 64 |  |
| 3 | `job_type` | `text` | NO | `'tagging'::text` |  |  |  |
| 4 | `status` | `text` | NO | `'queued'::text` |  |  |  |
| 5 | `attempts` | `int4` | NO | `0` |  | 32 |  |
| 6 | `last_error` | `text` | YES |  |  |  |  |
| 7 | `created_at` | `timestamptz` | NO | `now()` |  |  |  |
| 8 | `updated_at` | `timestamptz` | NO | `now()` |  |  |  |

### media

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('media_id_seq'::regclass)` |  | 32 |  |
| 2 | `review_id` | `int4` | NO |  |  | 32 |  |
| 3 | `file_type` | `varchar` | NO |  |  |  |  |
| 4 | `file_id` | `text` | NO |  |  |  |  |
| 5 | `context_text` | `text` | YES |  |  |  |  |
| 6 | `embedding` | `vector` | YES |  |  |  |  |
| 7 | `tags` | `jsonb` | YES |  |  |  |  |
| 8 | `tagged_by_model` | `text` | YES |  |  |  |  |
| 9 | `tagged_at` | `timestamp` | YES | `CURRENT_TIMESTAMP` |  |  |  |
| 10 | `tg_unique_id` | `text` | YES |  |  |  |  |
| 11 | `tg_chat_id` | `int8` | YES |  |  | 64 |  |
| 12 | `tg_message_id` | `int8` | YES |  |  | 64 |  |
| 13 | `tg_forward_from_chat_id` | `int8` | YES |  |  | 64 |  |
| 14 | `tg_forward_from_message_id` | `int8` | YES |  |  | 64 |  |
| 15 | `mime_type` | `text` | YES |  |  |  |  |
| 16 | `ext` | `text` | YES |  |  |  |  |
| 17 | `bytes_size` | `int8` | YES |  |  | 64 |  |
| 18 | `width` | `int4` | YES |  |  | 32 |  |
| 19 | `height` | `int4` | YES |  |  | 32 |  |
| 20 | `duration_sec` | `int4` | YES |  |  | 32 |  |
| 21 | `sha256` | `text` | YES |  |  |  |  |
| 22 | `storage_path` | `text` | YES |  |  |  |  |
| 23 | `status` | `text` | YES | `'stored'::text` |  |  |  |
| 24 | `created_at` | `timestamptz` | YES | `now()` |  |  |  |
| 25 | `created_by` | `int8` | YES |  |  | 64 |  |
| 26 | `tag_ids` | `_int4` | YES | `'{}'::integer[]` |  |  |  |

### media_ai_meta

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `media_id` | `int8` | NO |  |  | 64 |  |
| 2 | `raw_json` | `jsonb` | NO |  |  |  |  |
| 3 | `quality` | `float4` | YES |  |  | 24 |  |
| 4 | `nsfw_flag` | `bool` | YES |  |  |  |  |
| 5 | `detected_text` | `text` | YES |  |  |  |  |
| 6 | `updated_at` | `timestamptz` | NO | `now()` |  |  |  |

### media_links

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int8` | NO | `nextval('media_links_id_seq'::regclass)` |  | 64 |  |
| 2 | `media_id` | `int8` | NO |  |  | 64 |  |
| 3 | `entity_id` | `int8` | YES |  |  | 64 |  |
| 4 | `review_id` | `int8` | YES |  |  | 64 |  |
| 5 | `relation_type` | `text` | NO | `'context'::text` |  |  |  |
| 6 | `created_at` | `timestamptz` | NO | `now()` |  |  |  |

### media_tags

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int8` | NO | `nextval('media_tags_id_seq'::regclass)` |  | 64 |  |
| 2 | `media_id` | `int8` | NO |  |  | 64 |  |
| 3 | `tag_id` | `int8` | NO |  |  | 64 |  |
| 4 | `source` | `text` | NO |  |  |  |  |
| 5 | `confidence` | `float4` | YES |  |  | 24 |  |
| 6 | `created_at` | `timestamptz` | NO | `now()` |  |  |  |

### ratings

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('ratings_id_seq'::regclass)` |  | 32 |  |
| 2 | `category` | `text` | YES |  |  |  |  |
| 3 | `item_name` | `text` | YES |  |  |  |  |
| 4 | `avg_cleanliness` | `float8` | YES |  |  | 53 |  |
| 5 | `avg_staff` | `float8` | YES |  |  | 53 |  |
| 6 | `avg_food` | `float8` | YES |  |  | 53 |  |
| 7 | `avg_beach` | `float8` | YES |  |  | 53 |  |
| 8 | `avg_fun` | `float8` | YES |  |  | 53 |  |
| 9 | `avg_infra` | `float8` | YES |  |  | 53 |  |
| 10 | `avg_psycho` | `float8` | YES |  |  | 53 |  |
| 11 | `avg_service` | `float8` | YES |  |  | 53 |  |
| 12 | `avg_atmosphere` | `float8` | YES |  |  | 53 |  |
| 13 | `avg_price_quality` | `float8` | YES |  |  | 53 |  |
| 14 | `avg_interest` | `float8` | YES |  |  | 53 |  |
| 15 | `avg_organization` | `float8` | YES |  |  | 53 |  |
| 16 | `avg_uniqueness` | `float8` | YES |  |  | 53 |  |
| 17 | `avg_saturation` | `float8` | YES |  |  | 53 |  |
| 18 | `avg_communication` | `float8` | YES |  |  | 53 |  |
| 19 | `avg_knowledge` | `float8` | YES |  |  | 53 |  |
| 20 | `avg_flexibility` | `float8` | YES |  |  | 53 |  |
| 21 | `avg_infrastructure` | `float8` | YES |  |  | 53 |  |
| 22 | `avg_water_quality` | `float8` | YES |  |  | 53 |  |
| 23 | `avg_silence` | `float8` | YES |  |  | 53 |  |
| 24 | `avg_photogenic` | `float8` | YES |  |  | 53 |  |
| 25 | `rating_cuba` | `float8` | YES |  |  | 53 |  |
| 26 | `rating_world` | `float8` | YES |  |  | 53 |  |
| 27 | `reviews_count` | `int4` | YES |  |  | 32 |  |
| 28 | `top_horror` | `text` | YES |  |  |  |  |
| 29 | `top_nice` | `text` | YES |  |  |  |  |

### review_ratings

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('review_ratings_id_seq'::regclass)` |  | 32 |  |
| 2 | `review_id` | `int4` | NO |  |  | 32 |  |
| 3 | `aspect` | `varchar` | NO |  |  |  |  |
| 4 | `score` | `int4` | NO |  |  | 32 |  |

### reviews

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | NO | `nextval('reviews_id_seq'::regclass)` |  | 32 |  |
| 2 | `text` | `text` | YES |  |  |  |  |
| 3 | `category` | `varchar` | NO |  |  |  |  |
| 4 | `reference_name` | `text` | YES |  |  |  |  |
| 5 | `author_id` | `int8` | YES |  |  | 64 |  |
| 6 | `timestamp` | `timestamp` | NO | `CURRENT_TIMESTAMP` |  |  |  |
| 7 | `embedding` | `vector` | YES |  |  |  |  |
| 8 | `rating` | `int4` | YES |  |  | 32 |  |
| 9 | `author_username` | `varchar` | YES |  |  |  |  |
| 10 | `author_telegram_id` | `int8` | YES |  |  | 64 |  |

### reviews_normalized

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int4` | YES |  |  | 32 |  |
| 2 | `text` | `text` | YES |  |  |  |  |
| 3 | `category` | `varchar` | YES |  |  |  |  |
| 4 | `reference_name` | `text` | YES |  |  |  |  |
| 5 | `author_id` | `int8` | YES |  |  | 64 |  |
| 6 | `timestamp` | `timestamp` | YES |  |  |  |  |
| 7 | `embedding` | `vector` | YES |  |  |  |  |
| 8 | `rating` | `int4` | YES |  |  | 32 |  |
| 9 | `author_username` | `varchar` | YES |  |  |  |  |
| 10 | `author_telegram_id` | `int8` | YES |  |  | 64 |  |
| 11 | `canonical_item_name` | `text` | YES |  |  |  |  |

### tag_definitions

| # | column | type | null | default | length | precision | scale |
|---|--------|------|------|---------|--------|-----------|-------|
| 1 | `id` | `int8` | NO | `nextval('tag_definitions_id_seq'::regclass)` |  | 64 |  |
| 2 | `code` | `text` | NO |  |  |  |  |
| 3 | `title_ru` | `text` | NO |  |  |  |  |
| 4 | `category` | `text` | YES |  |  |  |  |
| 5 | `is_active` | `bool` | NO | `true` |  |  |  |


--------------------------------------------------------------------------------

## Primary keys

### alembic_version

- `version_num`

### authors

- `id`

### categories

- `id`

### category_definitions

- `variant_name`

### contacts

- `id`

### entities

- `id`

### expert_info

- `id`

### jobs_media

- `id`

### media

- `id`

### media_ai_meta

- `media_id`

### media_links

- `id`

### media_tags

- `id`

### ratings

- `id`

### review_ratings

- `id`

### reviews

- `id`

### tag_definitions

- `id`


--------------------------------------------------------------------------------

## Foreign keys

### categories — fk_categories_category

- `name` → `category_definitions`.`variant_name` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### category_definitions — cd_category_fk

- `category_id` → `categories`.`id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### contacts — fk_contacts_category

- `category` → `category_definitions`.`variant_name` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### entities — entities_category_id_fkey

- `category_id` → `categories`.`id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### jobs_media — jobs_media_media_id_fkey

- `media_id` → `media`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media — media_review_id_fkey

- `review_id` → `reviews`.`id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### media_ai_meta — media_ai_meta_media_id_fkey

- `media_id` → `media`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media_links — media_links_entity_id_fkey

- `entity_id` → `entities`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media_links — media_links_media_id_fkey

- `media_id` → `media`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media_links — media_links_review_id_fkey

- `review_id` → `reviews`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media_tags — media_tags_media_id_fkey

- `media_id` → `media`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### media_tags — media_tags_tag_id_fkey

- `tag_id` → `tag_definitions`.`id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

### ratings — ratings_category_fkey

- `category` → `category_definitions`.`variant_name` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

### review_ratings — review_ratings_review_id_fkey

- `review_id` → `reviews`.`id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)


--------------------------------------------------------------------------------

## Unique constraints

- **media_tags** — `media_tags_media_id_tag_id_source_key`: media_id, tag_id, source
- **tag_definitions** — `tag_definitions_code_key`: code


--------------------------------------------------------------------------------

## Indexes

### alembic_version

- `alembic_version_pkc` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num)`

### authors

- `authors_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX authors_pkey ON public.authors USING btree (id)`

### categories

- `categories_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX categories_pkey ON public.categories USING btree (id)`

### category_definitions

- `category_definitions_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX category_definitions_pkey ON public.category_definitions USING btree (variant_name)`
- `cd_variant_uidx` (UNIQUE, btree): `CREATE UNIQUE INDEX cd_variant_uidx ON public.category_definitions USING btree (variant_name)`

### contacts

- `contacts_cat_item_idx` (normal, btree): `CREATE INDEX contacts_cat_item_idx ON public.contacts USING btree (category, item_name)`
- `contacts_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX contacts_pkey ON public.contacts USING btree (id)`

### entities

- `entities_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX entities_pkey ON public.entities USING btree (id)`

### expert_info

- `expert_embedding_cosine` (normal, ivfflat): `CREATE INDEX expert_embedding_cosine ON public.expert_info USING ivfflat (embedding) WITH (lists='100')`
- `expert_info_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX expert_info_pkey ON public.expert_info USING btree (id)`

### jobs_media

- `ix_jobs_media_status` (normal, btree): `CREATE INDEX ix_jobs_media_status ON public.jobs_media USING btree (status, created_at)`
- `jobs_media_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX jobs_media_pkey ON public.jobs_media USING btree (id)`
- `uq_jobs_media_active` (UNIQUE, btree): `CREATE UNIQUE INDEX uq_jobs_media_active ON public.jobs_media USING btree (media_id, job_type, status) WHERE (status = ANY (ARRAY['queued'::text, 'in_progress'::text]))`

### media

- `ix_media_chat_msg` (normal, btree): `CREATE INDEX ix_media_chat_msg ON public.media USING btree (tg_chat_id, tg_message_id)`
- `ix_media_created_at` (normal, btree): `CREATE INDEX ix_media_created_at ON public.media USING btree (created_at DESC)`
- `media_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX media_pkey ON public.media USING btree (id)`
- `uq_media_sha256` (UNIQUE, btree): `CREATE UNIQUE INDEX uq_media_sha256 ON public.media USING btree (sha256) WHERE (sha256 IS NOT NULL)`
- `uq_media_tg_unique_id` (UNIQUE, btree): `CREATE UNIQUE INDEX uq_media_tg_unique_id ON public.media USING btree (tg_unique_id) WHERE (tg_unique_id IS NOT NULL)`

### media_ai_meta

- `media_ai_meta_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX media_ai_meta_pkey ON public.media_ai_meta USING btree (media_id)`

### media_links

- `media_links_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX media_links_pkey ON public.media_links USING btree (id)`
- `uq_media_links_unique` (UNIQUE, btree): `CREATE UNIQUE INDEX uq_media_links_unique ON public.media_links USING btree (media_id, COALESCE(entity_id, (0)::bigint), COALESCE(review_id, (0)::bigint), relation_type)`

### media_tags

- `ix_media_tags_media` (normal, btree): `CREATE INDEX ix_media_tags_media ON public.media_tags USING btree (media_id)`
- `media_tags_media_id_tag_id_source_key` (UNIQUE, btree): `CREATE UNIQUE INDEX media_tags_media_id_tag_id_source_key ON public.media_tags USING btree (media_id, tag_id, source)`
- `media_tags_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX media_tags_pkey ON public.media_tags USING btree (id)`

### ratings

- `ratings_cat_item_uidx` (UNIQUE, btree): `CREATE UNIQUE INDEX ratings_cat_item_uidx ON public.ratings USING btree (category, item_name)`
- `ratings_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX ratings_pkey ON public.ratings USING btree (id)`

### review_ratings

- `review_ratings_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX review_ratings_pkey ON public.review_ratings USING btree (id)`

### reviews

- `reviews_category_ref_idx` (normal, btree): `CREATE INDEX reviews_category_ref_idx ON public.reviews USING btree (category, reference_name)`
- `reviews_embedding_cosine` (normal, ivfflat): `CREATE INDEX reviews_embedding_cosine ON public.reviews USING ivfflat (embedding) WITH (lists='100')`
- `reviews_embedding_idx` (normal, ivfflat): `CREATE INDEX reviews_embedding_idx ON public.reviews USING ivfflat (embedding vector_cosine_ops)`
- `reviews_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX reviews_pkey ON public.reviews USING btree (id)`

### tag_definitions

- `tag_definitions_code_key` (UNIQUE, btree): `CREATE UNIQUE INDEX tag_definitions_code_key ON public.tag_definitions USING btree (code)`
- `tag_definitions_pkey` (PRIMARY, UNIQUE, btree): `CREATE UNIQUE INDEX tag_definitions_pkey ON public.tag_definitions USING btree (id)`


--------------------------------------------------------------------------------

## Sequences

- `authors_id_seq` → authors.id
- `categories_id_seq` → categories.id
- `contacts_id_seq` → contacts.id
- `entities_id_seq` → entities.id
- `expert_info_id_seq` → expert_info.id
- `jobs_media_id_seq` → jobs_media.id
- `media_id_seq` → media.id
- `media_links_id_seq` → media_links.id
- `media_tags_id_seq` → media_tags.id
- `ratings_id_seq` → ratings.id
- `review_ratings_id_seq` → review_ratings.id
- `reviews_id_seq` → reviews.id
- `tag_definitions_id_seq` → tag_definitions.id


--------------------------------------------------------------------------------

## Enum types

_no enums found_


--------------------------------------------------------------------------------

## Views

### reviews_normalized

```sql
SELECT r.id,
    r.text,
    r.category,
    r.reference_name,
    r.author_id,
    r."timestamp",
    r.embedding,
    r.rating,
    r.author_username,
    r.author_telegram_id,
    e.name AS canonical_item_name
   FROM (((reviews r
     JOIN category_definitions cd ON ((lower((r.category)::text) = lower(cd.variant_name))))
     JOIN categories c ON ((cd.category_id = c.id)))
     JOIN entities e ON (((lower(r.reference_name) = lower(e.name)) AND (e.category_id = c.id))));
```



--------------------------------------------------------------------------------

## Materialized views

_no materialized views found_


--------------------------------------------------------------------------------

## Functions

### array_to_halfvec(numeric[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_halfvec(numeric[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
```

### array_to_halfvec(integer[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_halfvec(integer[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
```

### array_to_halfvec(double precision[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_halfvec(double precision[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
```

### array_to_halfvec(real[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_halfvec(real[], integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_halfvec$function$
```

### array_to_sparsevec(numeric[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_sparsevec(numeric[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
```

### array_to_sparsevec(integer[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_sparsevec(integer[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
```

### array_to_sparsevec(real[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_sparsevec(real[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
```

### array_to_sparsevec(double precision[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_sparsevec(double precision[], integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_sparsevec$function$
```

### array_to_vector(numeric[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_vector(numeric[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
```

### array_to_vector(integer[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_vector(integer[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
```

### array_to_vector(real[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_vector(real[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
```

### array_to_vector(double precision[], integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.array_to_vector(double precision[], integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$array_to_vector$function$
```

### binary_quantize(vector)

```sql
CREATE OR REPLACE FUNCTION public.binary_quantize(vector)
 RETURNS bit
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$binary_quantize$function$
```

### binary_quantize(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.binary_quantize(halfvec)
 RETURNS bit
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_binary_quantize$function$
```

### cosine_distance(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.cosine_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$cosine_distance$function$
```

### cosine_distance(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.cosine_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_cosine_distance$function$
```

### cosine_distance(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.cosine_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_cosine_distance$function$
```

### halfvec(halfvec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.halfvec(halfvec, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec$function$
```

### halfvec_accum(double precision[], halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_accum(double precision[], halfvec)
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_accum$function$
```

### halfvec_add(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_add(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_add$function$
```

### halfvec_avg(double precision[])

```sql
CREATE OR REPLACE FUNCTION public.halfvec_avg(double precision[])
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_avg$function$
```

### halfvec_cmp(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_cmp(halfvec, halfvec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_cmp$function$
```

### halfvec_combine(double precision[], double precision[])

```sql
CREATE OR REPLACE FUNCTION public.halfvec_combine(double precision[], double precision[])
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_combine$function$
```

### halfvec_concat(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_concat(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_concat$function$
```

### halfvec_eq(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_eq(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_eq$function$
```

### halfvec_ge(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_ge(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_ge$function$
```

### halfvec_gt(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_gt(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_gt$function$
```

### halfvec_in(cstring, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_in(cstring, oid, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_in$function$
```

### halfvec_l2_squared_distance(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_l2_squared_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_squared_distance$function$
```

### halfvec_le(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_le(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_le$function$
```

### halfvec_lt(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_lt(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_lt$function$
```

### halfvec_mul(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_mul(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_mul$function$
```

### halfvec_ne(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_ne(halfvec, halfvec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_ne$function$
```

### halfvec_negative_inner_product(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_negative_inner_product(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_negative_inner_product$function$
```

### halfvec_out(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_out(halfvec)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_out$function$
```

### halfvec_recv(internal, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_recv(internal, oid, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_recv$function$
```

### halfvec_send(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_send(halfvec)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_send$function$
```

### halfvec_spherical_distance(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_spherical_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_spherical_distance$function$
```

### halfvec_sub(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_sub(halfvec, halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_sub$function$
```

### halfvec_to_float4(halfvec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_to_float4(halfvec, integer, boolean)
 RETURNS real[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_float4$function$
```

### halfvec_to_sparsevec(halfvec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_to_sparsevec(halfvec, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_sparsevec$function$
```

### halfvec_to_vector(halfvec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.halfvec_to_vector(halfvec, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_to_vector$function$
```

### halfvec_typmod_in(cstring[])

```sql
CREATE OR REPLACE FUNCTION public.halfvec_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_typmod_in$function$
```

### hamming_distance(bit, bit)

```sql
CREATE OR REPLACE FUNCTION public.hamming_distance(bit, bit)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$hamming_distance$function$
```

### hnsw_bit_support(internal)

```sql
CREATE OR REPLACE FUNCTION public.hnsw_bit_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_bit_support$function$
```

### hnsw_halfvec_support(internal)

```sql
CREATE OR REPLACE FUNCTION public.hnsw_halfvec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_halfvec_support$function$
```

### hnsw_sparsevec_support(internal)

```sql
CREATE OR REPLACE FUNCTION public.hnsw_sparsevec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$hnsw_sparsevec_support$function$
```

### hnswhandler(internal)

```sql
CREATE OR REPLACE FUNCTION public.hnswhandler(internal)
 RETURNS index_am_handler
 LANGUAGE c
AS '$libdir/vector', $function$hnswhandler$function$
```

### inner_product(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.inner_product(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_inner_product$function$
```

### inner_product(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.inner_product(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_inner_product$function$
```

### inner_product(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.inner_product(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$inner_product$function$
```

### ivfflat_bit_support(internal)

```sql
CREATE OR REPLACE FUNCTION public.ivfflat_bit_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$ivfflat_bit_support$function$
```

### ivfflat_halfvec_support(internal)

```sql
CREATE OR REPLACE FUNCTION public.ivfflat_halfvec_support(internal)
 RETURNS internal
 LANGUAGE c
AS '$libdir/vector', $function$ivfflat_halfvec_support$function$
```

### ivfflathandler(internal)

```sql
CREATE OR REPLACE FUNCTION public.ivfflathandler(internal)
 RETURNS index_am_handler
 LANGUAGE c
AS '$libdir/vector', $function$ivfflathandler$function$
```

### jaccard_distance(bit, bit)

```sql
CREATE OR REPLACE FUNCTION public.jaccard_distance(bit, bit)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$jaccard_distance$function$
```

### l1_distance(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.l1_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l1_distance$function$
```

### l1_distance(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.l1_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l1_distance$function$
```

### l1_distance(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.l1_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l1_distance$function$
```

### l2_distance(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.l2_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_distance$function$
```

### l2_distance(halfvec, halfvec)

```sql
CREATE OR REPLACE FUNCTION public.l2_distance(halfvec, halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_distance$function$
```

### l2_distance(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.l2_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l2_distance$function$
```

### l2_norm(sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.l2_norm(sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_norm$function$
```

### l2_norm(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.l2_norm(halfvec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_norm$function$
```

### l2_normalize(sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.l2_normalize(sparsevec)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_normalize$function$
```

### l2_normalize(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.l2_normalize(halfvec)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_l2_normalize$function$
```

### l2_normalize(vector)

```sql
CREATE OR REPLACE FUNCTION public.l2_normalize(vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$l2_normalize$function$
```

### sparsevec(sparsevec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec(sparsevec, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec$function$
```

### sparsevec_cmp(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_cmp(sparsevec, sparsevec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_cmp$function$
```

### sparsevec_eq(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_eq(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_eq$function$
```

### sparsevec_ge(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_ge(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_ge$function$
```

### sparsevec_gt(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_gt(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_gt$function$
```

### sparsevec_in(cstring, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_in(cstring, oid, integer)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_in$function$
```

### sparsevec_l2_squared_distance(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_l2_squared_distance(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_l2_squared_distance$function$
```

### sparsevec_le(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_le(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_le$function$
```

### sparsevec_lt(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_lt(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_lt$function$
```

### sparsevec_ne(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_ne(sparsevec, sparsevec)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_ne$function$
```

### sparsevec_negative_inner_product(sparsevec, sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_negative_inner_product(sparsevec, sparsevec)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_negative_inner_product$function$
```

### sparsevec_out(sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_out(sparsevec)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_out$function$
```

### sparsevec_recv(internal, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_recv(internal, oid, integer)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_recv$function$
```

### sparsevec_send(sparsevec)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_send(sparsevec)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_send$function$
```

### sparsevec_to_halfvec(sparsevec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_to_halfvec(sparsevec, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_to_halfvec$function$
```

### sparsevec_to_vector(sparsevec, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_to_vector(sparsevec, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_to_vector$function$
```

### sparsevec_typmod_in(cstring[])

```sql
CREATE OR REPLACE FUNCTION public.sparsevec_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$sparsevec_typmod_in$function$
```

### subvector(halfvec, integer, integer)

```sql
CREATE OR REPLACE FUNCTION public.subvector(halfvec, integer, integer)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_subvector$function$
```

### subvector(vector, integer, integer)

```sql
CREATE OR REPLACE FUNCTION public.subvector(vector, integer, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$subvector$function$
```

### vector(vector, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.vector(vector, integer, boolean)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector$function$
```

### vector_accum(double precision[], vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_accum(double precision[], vector)
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_accum$function$
```

### vector_add(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_add(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_add$function$
```

### vector_avg(double precision[])

```sql
CREATE OR REPLACE FUNCTION public.vector_avg(double precision[])
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_avg$function$
```

### vector_cmp(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_cmp(vector, vector)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_cmp$function$
```

### vector_combine(double precision[], double precision[])

```sql
CREATE OR REPLACE FUNCTION public.vector_combine(double precision[], double precision[])
 RETURNS double precision[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_combine$function$
```

### vector_concat(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_concat(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_concat$function$
```

### vector_dims(halfvec)

```sql
CREATE OR REPLACE FUNCTION public.vector_dims(halfvec)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$halfvec_vector_dims$function$
```

### vector_dims(vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_dims(vector)
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_dims$function$
```

### vector_eq(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_eq(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_eq$function$
```

### vector_ge(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_ge(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_ge$function$
```

### vector_gt(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_gt(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_gt$function$
```

### vector_in(cstring, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.vector_in(cstring, oid, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_in$function$
```

### vector_l2_squared_distance(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_l2_squared_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_l2_squared_distance$function$
```

### vector_le(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_le(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_le$function$
```

### vector_lt(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_lt(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_lt$function$
```

### vector_mul(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_mul(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_mul$function$
```

### vector_ne(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_ne(vector, vector)
 RETURNS boolean
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_ne$function$
```

### vector_negative_inner_product(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_negative_inner_product(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_negative_inner_product$function$
```

### vector_norm(vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_norm(vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_norm$function$
```

### vector_out(vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_out(vector)
 RETURNS cstring
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_out$function$
```

### vector_recv(internal, oid, integer)

```sql
CREATE OR REPLACE FUNCTION public.vector_recv(internal, oid, integer)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_recv$function$
```

### vector_send(vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_send(vector)
 RETURNS bytea
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_send$function$
```

### vector_spherical_distance(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_spherical_distance(vector, vector)
 RETURNS double precision
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_spherical_distance$function$
```

### vector_sub(vector, vector)

```sql
CREATE OR REPLACE FUNCTION public.vector_sub(vector, vector)
 RETURNS vector
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_sub$function$
```

### vector_to_float4(vector, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.vector_to_float4(vector, integer, boolean)
 RETURNS real[]
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_float4$function$
```

### vector_to_halfvec(vector, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.vector_to_halfvec(vector, integer, boolean)
 RETURNS halfvec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_halfvec$function$
```

### vector_to_sparsevec(vector, integer, boolean)

```sql
CREATE OR REPLACE FUNCTION public.vector_to_sparsevec(vector, integer, boolean)
 RETURNS sparsevec
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_to_sparsevec$function$
```

### vector_typmod_in(cstring[])

```sql
CREATE OR REPLACE FUNCTION public.vector_typmod_in(cstring[])
 RETURNS integer
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/vector', $function$vector_typmod_in$function$
```

