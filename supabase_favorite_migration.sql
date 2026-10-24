do $$
begin
    if exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'saved_recipes'
          and column_name = 'isFavorite'
    ) and not exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'saved_recipes'
          and column_name = 'is_favorite'
    ) then
        alter table public.saved_recipes
            rename column "isFavorite" to is_favorite;
    elsif not exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'saved_recipes'
          and column_name = 'is_favorite'
    ) then
        alter table public.saved_recipes
            add column is_favorite boolean not null default false;
    end if;
end $$;

grant update (is_favorite) on public.saved_recipes to anon;

drop policy if exists "Anyone can update recipe favorites"
    on public.saved_recipes;

create policy "Anyone can update recipe favorites"
    on public.saved_recipes for update to anon
    using (true)
    with check (true);
