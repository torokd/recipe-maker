create table public.saved_recipes (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    ingredients jsonb not null default '[]'::jsonb,
    instructions jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

alter table public.saved_recipes enable row level security;

grant select, insert, delete on public.saved_recipes to anon;

create policy "Anyone can view saved recipes"
    on public.saved_recipes for select to anon
    using (true);

create policy "Anyone can save recipes"
    on public.saved_recipes for insert to anon
    with check (true);

create policy "Anyone can remove saved recipes"
    on public.saved_recipes for delete to anon
    using (true);
