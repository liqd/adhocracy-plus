# Learning Nuggets

This app introduces the **Learning Center**, a dynamic content hub for educational nuggets organized by category. It blends structured Wagtail page models, global snippet management, and dynamic frontend behavior — offering a modular, scalable way to build learning content.

---

## Features

- **Learning Center Landing Page**  
  A singleton page under the homepage that acts as the entry point to the Learning Center. It renders a category-based index and loads nugget content dynamically.

- **Category-Based Nuggets**  
  Nuggets are organized into categories (managed as **Wagtail snippets**) and rendered via custom URLs like:  
  ```
  /learning-center/<category>/<nugget>/
  ```

- **htmx-Powered Navigation**  
  Nuggets load in the sidebar via [htmx](https://htmx.org/) (`hx-get` / `hx-target` / `hx-push-url`) for smooth transitions, while still supporting full server-side rendering (SSR) as a fallback. The views serve a partial when `request.htmx` is true (`django-htmx`), otherwise the full page.

- **Video Block Support**  
  Repurposed a `VideoBlock` from the Liquid site and added it to the CMS. It can be embedded within any nugget to enhance interactivity.

- **Role-Based Access**  
  Categories are tied to custom permissions (e.g., Moderator, Initiator, Participant) to control access per user role.

- **Modular Asset Structure**  
  Introduced an `assets/` folder at the app level to hold JS/CSS for better modularity and maintainability.

---

## Setup Instructions

### 1. Create the “Learning Nuggets” Singleton Page

- In Wagtail admin, go to the **Homepage**
- Add a new child page using the appropriate `LearningCenterPage` model
- **Name it exactly**: `Learning Center`  
  (this is critical for URL resolution to work)

This page will become the parent for all individual nuggets.

> 💡 **Future enhancement:**  
> Improve routing so it no longer depends on the page title being `"Learning Center"`. Instead, we could fetch the first instance of the `LearningCenterPage` dynamically or use a site setting to define it explicitly. This would improve flexibility and avoid title-coupling.

---

### 2. Add Nuggets

- Under the “Learning Center” page, create new `LearningNuggetPage` entries
- Each nugget is tied to a **Category snippet**
- The category’s slug is used to build the final URL

---

### 3. Manage Categories via Snippets

- Go to **Snippets > Learning Categories**
- Add/edit categories globally
- Assign them to nuggets through the dropdown field in each nugget page

Each category has:
- A slug (used in URLs)
- A title
- A description
- A role-based permission (`permission_level`)

> ⚠️ **The `permission_level` is not enforced yet.** All categories and nuggets
> are publicly visible regardless of the level. The permissions in `rules.py`
> (`view_participant_content`, `view_initiator_content`,
> `view_moderator_content`) are defined but not checked anywhere.
>
> Reason: the underlying `is_initiator` / `is_moderator` predicates from
> `adhocracy4` require a **project/organisation** as the subject, but
> `LearningCategory` is a global snippet with no such relation. Enforcing role
> access needs a concept first (global groups/staff, Wagtail groups, or an
> organisation FK on the category). Implementation should filter/404 at object
> level in the views.

---

## Preview Limitations

> ⚠️ **Wagtail’s preview functionality is currently unsupported for nuggets.**

Due to the use of custom routing (e.g., via a `CategoryView`), Wagtail’s default preview URLs don’t work. It attempts to load draft content through the live view, which fails if the associated category isn’t published or the object isn't resolved.

### Possible fix (future):

- Implement a custom `serve_preview()` method on the `LearningNuggetPage` model
- This would bypass the URL resolver and render the preview using a custom template