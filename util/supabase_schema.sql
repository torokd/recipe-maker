create table public.saved_recipes (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    ingredients jsonb not null default '[]'::jsonb,
    instructions jsonb not null default '[]'::jsonb,
    is_favorite boolean not null default false,
    created_at timestamptz not null default now()
);

alter table public.saved_recipes
    add column if not exists is_favorite boolean not null default false;

alter table public.saved_recipes enable row level security;

grant select, insert, delete on public.saved_recipes to anon;
grant update (is_favorite) on public.saved_recipes to anon;

create policy "Anyone can view saved recipes"
    on public.saved_recipes for select to anon
    using (true);

create policy "Anyone can save recipes"
    on public.saved_recipes for insert to anon
    with check (true);

create policy "Anyone can remove saved recipes"
    on public.saved_recipes for delete to anon
    using (true);

create policy "Anyone can update recipe favorites"
    on public.saved_recipes for update to anon
    using (true)
    with check (true);
