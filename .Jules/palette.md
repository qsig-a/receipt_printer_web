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
