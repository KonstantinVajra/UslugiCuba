import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from pathlib import Path

# 🔧 Укажи свои параметры подключения
DB_NAME = "clone_db_new"
DB_USER = "gen_user"
DB_PASS = "Kmkm72Timeweb"
DB_HOST = "46.19.64.78"  # например, pg.timeweb.ru
DB_PORT = 5432
SCHEMA  = "public"

OUT_FILE = Path("schema_full.md")

SECTION_LINE = "-" * 80

def fetch_all(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchall()

def main():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor(cursor_factory=DictCursor)

    with OUT_FILE.open("w", encoding="utf-8") as f:
        f.write(f"# PostgreSQL schema dump — `{SCHEMA}`\n")
        f.write(f"_Generated: {datetime.now():%Y-%m-%d %H:%M:%S}_\n\n")

        # --- TABLES & COLUMNS
        f.write("## Tables & columns\n\n")
        cols_sql = f"""
        SELECT
          c.table_name,
          c.ordinal_position,
          c.column_name,
          COALESCE(c.udt_name, c.data_type) AS data_type,
          c.is_nullable,
          c.column_default,
          c.character_maximum_length,
          c.numeric_precision,
          c.numeric_scale
        FROM information_schema.columns c
        WHERE c.table_schema = %s
        ORDER BY c.table_name, c.ordinal_position;
        """
        cols = fetch_all(cur, cols_sql, (SCHEMA,))
        current_table = None
        for r in cols:
            table = r["table_name"]
            if table != current_table:
                if current_table is not None:
                    f.write("\n")
                f.write(f"### {table}\n\n")
                f.write("| # | column | type | null | default | length | precision | scale |\n")
                f.write("|---|--------|------|------|---------|--------|-----------|-------|\n")
                current_table = table
            f.write("| {ord} | `{col}` | `{typ}` | {null} | {dflt} | {l} | {p} | {s} |\n".format(
                ord=r["ordinal_position"],
                col=r["column_name"],
                typ=r["data_type"],
                null="YES" if r["is_nullable"] == "YES" else "NO",
                dflt=f"`{r['column_default']}`" if r["column_default"] else "",
                l=r["character_maximum_length"] or "",
                p=r["numeric_precision"] or "",
                s=r["numeric_scale"] or "",
            ))
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- PRIMARY KEYS
        f.write("## Primary keys\n\n")
        pk_sql = f"""
        SELECT
          tc.table_name,
          kcu.column_name,
          kcu.ordinal_position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
        ORDER BY tc.table_name, kcu.ordinal_position;
        """
        pks = fetch_all(cur, pk_sql, (SCHEMA,))
        if pks:
            tbl = None
            for r in pks:
                if r["table_name"] != tbl:
                    if tbl is not None:
                        f.write("\n")
                    tbl = r["table_name"]
                    f.write(f"### {tbl}\n\n")
                f.write(f"- `{r['column_name']}`\n")
        else:
            f.write("_no primary keys found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- FOREIGN KEYS
        f.write("## Foreign keys\n\n")
        fk_sql = f"""
        SELECT
          tc.table_name AS table_name,
          tc.constraint_name,
          kcu.column_name AS column_name,
          ccu.table_name AS ref_table,
          ccu.column_name AS ref_column,
          rc.update_rule,
          rc.delete_rule,
          kcu.ordinal_position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints rc
          ON rc.constraint_name = tc.constraint_name
         AND rc.constraint_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = %s
        ORDER BY table_name, constraint_name, kcu.ordinal_position;
        """
        fks = fetch_all(cur, fk_sql, (SCHEMA,))
        if fks:
            cur_tbl, cur_c = None, None
            for r in fks:
                key = (r["table_name"], r["constraint_name"])
                if key != (cur_tbl, cur_c):
                    if cur_tbl is not None:
                        f.write("\n")
                    cur_tbl, cur_c = key
                    f.write(f"### {r['table_name']} — {r['constraint_name']}\n\n")
                f.write(f"- `{r['column_name']}` → `{r['ref_table']}`.`{r['ref_column']}` "
                        f"(ON UPDATE {r['update_rule']}, ON DELETE {r['delete_rule']})\n")
        else:
            f.write("_no foreign keys found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- UNIQUE constraints
        f.write("## Unique constraints\n\n")
        uq_sql = f"""
        SELECT
          tc.table_name,
          tc.constraint_name,
          string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columns
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s
          AND tc.constraint_type = 'UNIQUE'
        GROUP BY tc.table_name, tc.constraint_name
        ORDER BY tc.table_name, tc.constraint_name;
        """
        uqs = fetch_all(cur, uq_sql, (SCHEMA,))
        if uqs:
            for r in uqs:
                f.write(f"- **{r['table_name']}** — `{r['constraint_name']}`: {r['columns']}\n")
        else:
            f.write("_no unique constraints found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- INDEXES
        f.write("## Indexes\n\n")
        idx_sql = f"""
        SELECT
          t.relname AS table_name,
          i.relname AS index_name,
          am.amname AS method,
          ix.indisunique AS is_unique,
          ix.indisprimary AS is_primary,
          pg_get_indexdef(ix.indexrelid) AS indexdef
        FROM pg_class t
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_index ix ON ix.indrelid = t.oid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_am am ON am.oid = i.relam
        WHERE n.nspname = %s
          AND t.relkind = 'r'
        ORDER BY t.relname, i.relname;
        """
        idxs = fetch_all(cur, idx_sql, (SCHEMA,))
        if idxs:
            cur_tbl = None
            for r in idxs:
                if r["table_name"] != cur_tbl:
                    if cur_tbl is not None:
                        f.write("\n")
                    cur_tbl = r["table_name"]
                    f.write(f"### {cur_tbl}\n\n")
                flags = []
                if r["is_primary"]: flags.append("PRIMARY")
                if r["is_unique"]:  flags.append("UNIQUE")
                flags = (", ".join(flags)) or "normal"
                f.write(f"- `{r['index_name']}` ({flags}, {r['method']}): `{r['indexdef']}`\n")
        else:
            f.write("_no indexes found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- SEQUENCES
        f.write("## Sequences\n\n")
        seq_sql = f"""
        SELECT
          seq.relname AS sequence_name,
          ns.nspname AS schema,
          tab.relname AS table_name,
          col.attname AS column_name
        FROM pg_class seq
        JOIN pg_namespace ns ON ns.oid = seq.relnamespace
        LEFT JOIN pg_depend dep ON dep.objid = seq.oid AND dep.deptype = 'a'
        LEFT JOIN pg_class tab ON tab.oid = dep.refobjid
        LEFT JOIN pg_attribute col ON col.attrelid = tab.oid AND col.attnum = dep.refobjsubid
        WHERE seq.relkind = 'S' AND ns.nspname = %s
        ORDER BY sequence_name;
        """
        seqs = fetch_all(cur, seq_sql, (SCHEMA,))
        if seqs:
            for r in seqs:
                owner = f" → {r['table_name']}.{r['column_name']}" if r["table_name"] else ""
                f.write(f"- `{r['sequence_name']}`{owner}\n")
        else:
            f.write("_no sequences found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- ENUM TYPES
        f.write("## Enum types\n\n")
        enum_sql = f"""
        SELECT
          t.typname AS enum_name,
          string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) AS labels
        FROM pg_type t
        JOIN pg_enum e ON e.enumtypid = t.oid
        JOIN pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = %s
        GROUP BY t.typname
        ORDER BY t.typname;
        """
        enums = fetch_all(cur, enum_sql, (SCHEMA,))
        if enums:
            for r in enums:
                f.write(f"- `{r['enum_name']}`: {r['labels']}\n")
        else:
            f.write("_no enums found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- VIEWS
        f.write("## Views\n\n")
        view_sql = """
        SELECT table_name, view_definition
        FROM information_schema.views
        WHERE table_schema = %s
        ORDER BY table_name;
        """
        views = fetch_all(cur, view_sql, (SCHEMA,))
        if views:
            for r in views:
                f.write(f"### {r['table_name']}\n\n")
                f.write("```sql\n" + (r["view_definition"] or "").strip() + "\n```\n\n")
        else:
            f.write("_no views found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- MATERIALIZED VIEWS
        f.write("## Materialized views\n\n")
        matv_sql = """
        SELECT matviewname, definition
        FROM pg_matviews
        WHERE schemaname = %s
        ORDER BY matviewname;
        """
        matvs = fetch_all(cur, matv_sql, (SCHEMA,))
        if matvs:
            for r in matvs:
                f.write(f"### {r['matviewname']}\n\n")
                f.write("```sql\n" + (r["definition"] or "").strip() + "\n```\n\n")
        else:
            f.write("_no materialized views found_\n")
        f.write("\n\n" + SECTION_LINE + "\n\n")

        # --- FUNCTIONS
        # --- FUNCTIONS
        f.write("## Functions\n\n")
        func_sql = """
        SELECT
          p.oid,
          p.proname,
          p.prokind,  -- 'f' = function, 'p' = procedure, 'a' = aggregate, 'w' = window agg
          pg_catalog.pg_get_function_arguments(p.oid) AS args
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = %s
          AND p.prokind IN ('f','p')  -- исключаем агрегаты/оконные агрегаты
        ORDER BY p.proname;
        """
        funcs = fetch_all(cur, func_sql, (SCHEMA,))
        if funcs:
            for r in funcs:
                name = r['proname']
                args = r['args']
                try:
                    cur.execute("SELECT pg_catalog.pg_get_functiondef(%s);", (r['oid'],))
                    func_def = cur.fetchone()[0] or ""
                except Exception as e:
                    # На всякий случай — не падаем, а помечаем проблему и идём дальше
                    func_def = f"-- unable to dump definition: {e}"
                f.write(f"### {name}({args})\n\n")
                f.write("```sql\n" + func_def.strip() + "\n```\n\n")
        else:
            f.write("_no functions found_\n")

    cur.close()
    conn.close()
    print(f"✅ Готово: {OUT_FILE.resolve()}")

if __name__ == "__main__":
    main()