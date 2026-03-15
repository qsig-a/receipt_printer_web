## 2024-05-22 - Accessibility in Embedded Templates
**Learning:** This Flask application embeds HTML templates directly in Python strings, which led to missing standard accessibility features like `<label>` elements and viewport meta tags.
**Action:** When working with embedded templates, explicitly check for and add `<label>` elements and responsiveness meta tags to ensure basic accessibility and mobile usability.

## 2025-02-23 - Status Message Accessibility
**Learning:** The application uses a generic `.status-box` div for feedback, which is not announced by screen readers on page reload.
**Action:** Always add `role="alert"` to feedback containers in server-rendered templates to ensure screen reader users are immediately aware of the form submission outcome.

## 2025-05-23 - Visible Constraints for Better UX
**Learning:** The application enforces a `CHARACTER_LIMIT` on the backend but provided no visual indication on the frontend, leading to a frustrating "error-after-submit" experience.
**Action:** When backend constraints exist, surface them in the UI (e.g., character counters, `maxlength` attributes) to prevent errors before they happen.

## 2025-05-24 - Persist User Input on Error
**Learning:** Users lose their typed message if the submission fails (e.g., wrong password), causing significant frustration.
**Action:** Always re-populate form fields with the submitted data when rendering an error state, so users can correct the issue without retyping.

## 2025-05-25 - Copy Utility in Data Tables
**Learning:** Text in data tables (especially logs) is hard to select precisely. Adding a dedicated 'Copy' button reduces friction for administrative tasks.
**Action:** For read-only data views (like logs or histories), consider adding copy-to-clipboard actions for complex or long fields.

## 2025-05-26 - Empty States for Data Tables
**Learning:** Tables without data look broken and confusing. Users might think the data failed to load.
**Action:** Always include an empty state (e.g., using Jinja's `{% else %}` block in loops) to reassure users that the system is working but there is no data.

## 2025-05-27 - Context for Textareas
**Learning:** Screen reader users miss helpful context (like shortcuts and limits) when it's just visual text near the input.
**Action:** Use `aria-describedby` to programmatically link helper text and character counters to the input they describe.

## 2025-05-28 - Localized Timestamps for Admin Views
**Learning:** Server-side timestamps (UTC) in logs force users to do mental math, increasing cognitive load during debugging.
**Action:** Render timestamps as ISO strings in `data` attributes and use `Intl.DateTimeFormat` on the client side to display them in the user's local timezone.

## 2026-02-24 - Avoid Dead Ends on Auth Failure
**Learning:** Returning a raw "Unauthorized" text response (401) on a failed form submission is a poor user experience as it forces the user to navigate back manually.
**Action:** Always re-render the form with an inline error message while preserving the 401 status code, so the user can immediately correct their mistake.

## 2026-03-01 - Friendly 404 Pages
**Learning:** Default server 404 pages are jarring and offer no path forward, leaving users stranded.
**Action:** Create a custom 404 template that matches the application's design language and provides a clear "Return Home" action to keep users within the flow.

## 2025-03-02 - Keyboard Navigation Visibility
**Learning:** Without explicit `:focus-visible` styles, users relying on keyboard navigation may have difficulty identifying the currently focused button or link.
**Action:** Always include a distinct focus indicator, such as an `outline` or `box-shadow`, for interactive elements like buttons and links when they receive focus via keyboard navigation.

## 2026-03-05 - Focus Visible for Keyboard Navigation
**Learning:** In a dark theme, default browser focus rings on buttons and links often lack sufficient contrast, making keyboard navigation difficult.
**Action:** Always add custom `:focus-visible` styles (e.g., using box-shadows) for interactive elements that match the design language and provide clear, high-contrast feedback.

## 2026-03-02 - Page Titles and Language Attributes in Embedded Templates
**Learning:** Missing language attributes (`lang="en"`) and descriptive `<title>` tags in embedded HTML templates hinder screen reader access and general usability.
**Action:** Ensure all root `<html>` elements in embedded templates have correct `lang` attributes and descriptive `<title>` tags to properly inform users and assistive tech of the page's purpose and language.

## 2026-03-06 - Visual Required Field Indicators
**Learning:** Users may not know which fields are mandatory until they submit the form and receive an error, causing frustration and a feeling of "error-after-submit".
**Action:** Always add visual indicators, such as a high-contrast asterisk (`<span aria-hidden="true">*</span>`), to the labels of required form fields to clearly indicate constraints upfront.

## 2026-03-05 - Clearing Validation States on Input
**Learning:** Persisting error styles (like red borders and `aria-invalid=\true\`) on inputs *after* the user begins typing to correct their mistake creates a frustrating, accusatory UX.
**Action:** Always add explicit JavaScript event listeners to form fields to clear validation styles (`.input-error`) and accessibility attributes (`aria-invalid`) immediately upon the `input` event. Additionally, ensure server-side errors render with `aria-invalid=\true\`.

## 2026-03-07 - OS-Aware Guidance and Semantic Landmarks
**Learning:** Generic keyboard hints (like "Ctrl+Enter") cause cognitive friction for Mac users, and generic layout divs (`<div class="container">`) hinder screen reader navigation by failing to define structural landmarks.
**Action:** Always use semantic HTML5 elements (like `<main>`) for core content areas to provide explicit navigation landmarks, and utilize `navigator.userAgent` to dynamically adapt UI text (like shortcut keys) to the user's specific operating system for a more intuitive experience.

## 2026-03-08 - Semantic Keyboard Shortcuts
**Learning:** Using generic `<strong>` or `<span>` tags for keyboard shortcuts misses an opportunity for semantic markup and visual clarity. Screen readers can better interpret `<kbd>` tags, and they can be styled to look like physical keys, enhancing the UI.
**Action:** Always use the `<kbd>` HTML element for indicating keyboard input or shortcuts, and apply distinct CSS styling (like borders and box-shadows) to make them visually resemble physical keys.

## 2026-03-08 - Hover Context for Icon Buttons
**Learning:** Icon-only buttons with `aria-label` are accessible to screen readers, but sighted mouse users relying on hover miss out on the context, leading to ambiguity.
**Action:** Always provide a `title` attribute alongside `aria-label` on icon-only buttons to ensure hover tooltips appear, providing explicit guidance for mouse users.

## 2026-03-09 - Disabled States for Empty Data Actions
**Learning:** When data tables are empty, destructive or export actions (like "Clear" or "Download") can be confusing if left active, potentially leading to invalid server requests.
**Action:** Always disable action buttons when the related dataset is empty, and provide clear explanations via tooltips (`title` attribute) and `aria-disabled="true"` to inform users why the action is unavailable.

## 2026-03-10 - Scrollable Table Accessibility
**Learning:** Tables that scroll vertically hide their column headers, confusing users. Furthermore, if a table container is scrollable, keyboard-only users cannot scroll it without `tabindex="0"`.
**Action:** Always make table headers sticky (`position: sticky; top: 0; z-index: 10;`) and wrap scrollable tables in a container with `tabindex="0"`, `role="region"`, and a descriptive `aria-label` to ensure they are fully navigable by keyboard and screen reader users. Also provide a custom `:focus-visible` outline for the container to highlight it when focused.

## 2026-03-11 - Explicit Error Associations
**Learning:** Relying solely on visual cues (like a red border) and `aria-invalid="true"` is insufficient for screen reader users to understand *why* an input is invalid if the error message is disconnected from the input in the DOM.
**Action:** Always use `aria-errormessage` on the invalid input, pointing to the `id` of the element containing the explicit error message, to provide clear, actionable feedback to screen reader users. Ensure this attribute is cleared simultaneously with `aria-invalid` when the user begins typing.

## 2026-03-11 - Accessible Copy Feedback
**Learning:** Changing an emoji in a copy-to-clipboard button (e.g., from 📋 to ✅) provides excellent visual feedback for sighted users, but offers absolutely no context to screen reader users about the outcome of the action.
**Action:** When updating a button's visual state to indicate success, concurrently update its `aria-label` and `title` attributes (e.g., to "Copied!") for the duration of the feedback state, ensuring equitable access to status updates.

## 2026-03-11 - Hiding Decorative Emojis
**Learning:** Using inline emojis for visual flair in headings or empty states can create jarring experiences for screen reader users, as the emojis are often read out with long, literal descriptions (e.g., "Remote Print fax machine").
**Action:** Wrap purely decorative emojis in a `<span aria-hidden="true">` to hide them from assistive technologies while preserving the visual design for sighted users.

## 2026-03-12 - Auth Failure Dead End Escape Hatch
**Learning:** Returning a raw "Unauthorized" text response or trapping unauthenticated users on a login screen without a clear exit path creates a dead end, forcing them to use the browser back button, which is poor UX.
**Action:** Always provide an "escape hatch" (like a "Back to Portal" link) on protected views or login screens so unauthenticated users can easily return to the main application flow.

## 2026-03-13 - State Communication for Toggle Buttons
**Learning:** Toggle buttons (like password visibility toggles) without explicit state attributes leave screen reader users unsure of the current state or the outcome of their action.
**Action:** Always use the `aria-pressed` attribute (toggling between `"true"` and `"false"`) on semantic `<button>` elements that act as toggles, and use `aria-controls` to explicitly link them to the element they modify, ensuring clear state communication for assistive technologies.

## 2026-03-13 - Toggle Button Anti-Pattern
**Learning:** Changing both the `aria-label` (e.g., from "Show password" to "Hide password") and the `aria-pressed` state simultaneously on a toggle button is a known W3C ARIA anti-pattern. Doing both results in confusing screen reader announcements like "Hide password, toggle button, pressed".
**Action:** For a true toggle button, either keep the `aria-label` static (e.g., "Show password" or "Toggle password visibility") while toggling `aria-pressed` between true/false, OR change the `aria-label` dynamically without using `aria-pressed`. Do not combine both approaches.

## 2026-03-14 - Data Table Scannability and Semantics
**Learning:** Wide data tables without visual aids (like hover states) cause users to lose their place when tracking across columns. Furthermore, generic markup (`<span>` for dates, `<th>` without scope) limits the usefulness of the data for screen reader users and automated parsing.
**Action:** Always include a subtle `.history-table tbody tr:hover` state for multi-column data tables to improve horizontal tracking. Additionally, ensure table headers explicitly declare `scope="col"`, use semantic `<time datetime="...">` tags for temporal data, and define explicit `type="button"` on in-row utility buttons to prevent accidental form submissions.
