# FrameRate — Circles + Home + Polish Patch

Apply these files over your `C:\framerate\` project. **No migrations needed** —
this patch only changes method bodies, form fields, and adds new files. The
existing database schema already supports everything (the `Review.circle` FK
and the `Circle` / `CircleMembership` tables already exist).

## What this adds

1. **Circles UI** — list, detail, create, join, leave. 1-founder model (the
   creator becomes the founder; no 3-founder gate). Navbar gets a **Circles**
   button.
2. **Real home page** — trending movies (TMDb `/trending/movie/week`) + the 5
   most recent community reviews.
3. **Circle tagging on reviews** — the Write/Edit Review form now has an
   optional "Tag to a circle" dropdown (only circles you've joined). Tagged
   reviews show a circle badge on the movie detail page, review detail page,
   and home feed.
4. **Polish** — profile page now uses Material Icons stars (matching the rest)
   and review titles link to the review detail page.

## 1. Copy these files over C:\framerate\

Mirror the folder structure below. Overwrite existing files; create new ones
where the path doesn't exist yet.

```
circles\models.py                 (overwrite)
circles\forms.py                  (new)
circles\views.py                  (overwrite — was empty stub)
circles\urls.py                   (new)

movies\tmdb_service.py            (overwrite — adds get_trending_movies)
movies\views.py                   (overwrite — adds home_view)

reviews\forms.py                  (overwrite — adds circle field)
reviews\views.py                  (overwrite — passes user to form)

framerate\urls.py                 (overwrite — includes circles.urls, home as view)

templates\circles\circle_list.html     (new)
templates\circles\circle_detail.html   (new)
templates\circles\circle_form.html     (new)

templates\movies\home.html            (overwrite)
templates\movies\movie_detail.html    (overwrite)

templates\reviews\review_form.html    (overwrite)
templates\reviews\review_detail.html  (overwrite)

templates\accounts\profile.html       (overwrite)
templates\partials\navbar.html        (overwrite)
```

On Windows, you can select all the folders inside `framerate_patches\`
(`circles`, `movies`, `reviews`, `framerate`, `templates`) and drag them onto
`C:\framerate\`, choosing **"Replace the files in the destination"** when
prompted. The new files (`circles\forms.py`, `circles\urls.py`, the three
`templates\circles\*.html`) will be created automatically.

## 2. Unlock the existing circle (one-time)

Your DB already has one circle ("Nolan Fanclub") that the old 2-founder rule
auto-locked. The model now treats any circle with a founder as active, but the
old `is_locked=True` flag is still sitting on that row. Clear it once:

```
python manage.py shell -c "from circles.models import Circle; Circle.objects.filter(is_locked=True).update(is_locked=False, locked_at=None)"
```

Run this from `C:\framerate\` with your venv active. It should print nothing
and return — that's success. New circles created via the UI never lock.

## 3. Restart the server + hard refresh

Python files changed, so restart `runserver`. Then hard-refresh the browser
(`Ctrl+Shift+R`) so the navbar / templates reload.

## 4. Test the demo flow

1. **Home** (`/`) — you should see a "Trending This Week" grid + "Recent
   Reviews" (your 7 existing reviews should appear).
2. **Circles** — click the new **Circles** button in the navbar. You should see
   "Nolan Fanclub". Click it → detail page shows its 1 review (the one already
   tagged) + the founder.
3. **Create a circle** — click **New Circle**, fill in name/topic/description,
   submit. You become the founder and land on the new circle's detail page.
4. **Join a circle** — open one you didn't create, click **Join Circle**.
5. **Tag a review** — search a movie → **Write a Review** → the form now has a
   "Tag to a circle" dropdown (shows circles you've joined). Pick one, post.
   The circle badge then shows on the movie detail page, the review detail
   page, and the home feed.
6. **Profile** — your profile now shows Material Icons stars and each review
   title links to its review detail page.

## Notes / assumptions

- **1-founder model.** `Circle.is_active` is now `founder_count >= 1` and the
  auto-lock signal only fires if a circle loses *all* founders (essentially
  never in normal use). The `is_locked` / `locked_at` fields are kept so no
  migration is needed.
- **Circle tagging is optional.** Reviews without a circle still work exactly
  as before (`circle = NULL`).
- **Trending fetch hits TMDb on every home load.** If TMDb is slow/down, the
  home page still renders the Recent Reviews section with a small "unavailable"
  note where trending would be.
- The `settings.py` duplicate `TEMPLATES` / `STATIC_URL` blocks (cosmetic, and
  harmless) were **not** changed — left untouched to avoid any risk to your
  running app. If you want, you can later delete the first `TEMPLATES = [...]`
  block (around lines 60–73) and the first `STATIC_URL = 'static/'` line.
